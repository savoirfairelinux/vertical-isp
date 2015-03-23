# -*- encoding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

# About encryption in this module
#
# The goal of this module is to store CC numbers in an encrypted way using an
# assymetric encryption method (we use RSA). This way, someone with full access
# to our DB won't be able to decrypt our CC numbers unless he also has access
# to the private key, which of course isn't stored in the BD.
#
# Because the output of PyCrypto.PublicKey.RSA.encrypt() is binary data and
# that we store the encrypted key in a char field, we encode that encrypted
# data with base64.

import re
import binascii
from datetime import datetime
from Crypto.PublicKey import RSA

from openerp.tools.translate import _
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


def is_credit_card_number_valid(credit_card_number):
    """Credit card number validation according to the MODULO-10 algorithm.
    """
    str_card_number = str(credit_card_number)
    str_check_digit = str_card_number[-1]
    str_validation_vect = ""
    str_result_vect = []
    result = 0
    next_closest_ten = 10

    # Make sure the credit card number consists of
    # digits only
    if not re.match(r"^[0-9]+$", str_card_number):
        return False

    # Build the validation vector '212121...'
    for i in range(len(str_card_number) - 1):
        if i % 2 == 0:
            str_validation_vect += '2'
        else:
            str_validation_vect += '1'

    # Multiply each digit of the card number
    # by the corresponding validation digit,
    # except for the last digit
    for i in range(len(str_validation_vect)):
        res = int(str_card_number[i]) * int(str_validation_vect[i])
        str_result_vect.append(res)

    # Add the result of the above multiplication
    # and consider a 2-digit number as 2 numbers
    # of one digit
    for number in str_result_vect:
        if number < 10:
            result += number
        else:
            str_number = str(number)
            num_1 = int(str_number[0])
            num_2 = int(str_number[1])
            result += num_1 + num_2

    # Compute the check digit and compare it
    # with the last digit of the card number
    while next_closest_ten < result:
        next_closest_ten += 10

    check_digit = next_closest_ten - result

    if str(check_digit) == str_check_digit:
        return True
    else:
        return False


def fix_public_key(key):
    # Copy/Pasting public key leads to formatting loss, and PyCrypto is
    # sensitive on this matter.  It wants all \n preserved, but in OpenERP's
    # char field, those \n are going to be replaced with spaces. But don't try
    # to naively replace spaces with newlines, because you're going to end up
    # with BEGIN\nPUBLIC\KEY, which PyCrypto won't accept.
    if key.strip().startswith('ssh-rsa'):
        # This key is not of the type that starts with BEGIN PUBLIC KEY. Just
        # return the stripped version
        return key.strip()
    stripped = re.sub(r'\s?-----[A-Z\s]+-----\s?', '', key)
    stripped = stripped.replace(' ', '\n')
    return '\n'.join(('-----BEGIN PUBLIC KEY-----',
                      stripped,
                      '-----END PUBLIC KEY-----'))


def is_encrypted(cc_number):
    return 'X-X' in cc_number


def encrypt_cc_number(cc_number, public_key):
    if isinstance(cc_number, unicode):
        cc_number = cc_number.encode('utf-8')
    key = RSA.importKey(fix_public_key(public_key))
    encrypted_cc_number = key.encrypt(cc_number, 42)[0]
    return binascii.b2a_base64(encrypted_cc_number).strip()


def obfuscate_cc(cc_number):
    """ Obfuscate a credit card number
    Replaces all but the first 6 and last 4 digits by X, and formats them
    as 1111-11XX-XXXX-1111
    """
    # Strip all non-numbers
    cc_number = re.sub(r'[^\d]', '', cc_number)
    digits = list(cc_number)
    digits[6:-4] = 'X' * len(digits[6:-4])
    for i in range((len(digits) - 1) // 4, 0, -1):
        i = i * 4
        digits[i:i] = '-'
    return ''.join(digits)


def encrypt_cc_vals(partner_obj, vals):
    if 'acc_number' not in vals:
        # no acc_number, no problem
        return
    cc_number = vals['acc_number']
    if is_encrypted(cc_number):
        # We're not actually changing the number, just remove it
        del vals['acc_number']
    elif is_credit_card_number_valid(cc_number):
        # Ok, we're actually submitting a CC number here
        # Never ever store CCAnumber in clear
        vals['acc_number'] = obfuscate_cc(cc_number)
        vals['encrypted_cc_number'] = encrypt_cc_number(
            cc_number, partner_obj.company_id.cc_number_encrypt_key)


class res_partner_bank(orm.Model):
    _inherit = 'res.partner.bank'

    _columns = {
        # RSA-encrypted, bas64-encoded.
        'encrypted_cc_number': fields.char("Encrypted Credit Card Number",
                                           size=1024),
        'expiration_date': fields.char('Expiration date (YYMM)', size=4),
    }

    def check_credit_card_number(self, cr, uid, ids, context=None):
        for bank_acc in self.browse(cr, uid, ids, context=context):
            if bank_acc.state != 'credit_card':
                continue
            cc_number = bank_acc.acc_number
            if is_encrypted(cc_number):
                # It's a hidden number, so we're not actually changing the
                # encrypted CC number.  Consider as valid
                continue
            if not is_credit_card_number_valid(cc_number):
                return False
        return True

    def check_expiration_date(self, cr, uid, ids, context=None):
        today = datetime.strptime(
            fields.date.context_today(self, cr, uid),
            DEFAULT_SERVER_DATE_FORMAT,
        ).date()
        for bank_acc in self.browse(cr, uid, ids, context=context):
            if bank_acc.state != 'credit_card':
                continue
            if not bank_acc.active:
                continue
            if not bank_acc.expiration_date:
                return False
            m = re.match(r"^([0-9]{2})([0-9]{2})$", bank_acc.expiration_date)
            if m is None:
                return False
            # We have year/month from our card.
            try:
                cc_date = datetime(int(m.group(1)) + 2000, int(m.group(2)), 1)
            except ValueError:
                return False

            # Not comparing directly to avoid dealing with the day
            if cc_date.year < today.year:
                return False
            if cc_date.year == today.year and cc_date.month < today.month:
                return False
        return True

    def _construct_constraint_msg_card_number(self, cr, uid, ids,
                                              context=None):
        return (_("Credit card number is invalid")), ()

    def _construct_constraint_msg_expiration_date(self, cr, uid, ids,
                                                  context=None):
        return (_("Expiration date is invalid")), ()

    _constraints = [
        (check_credit_card_number,
         _construct_constraint_msg_card_number, ["acc_number"]),
        (check_expiration_date,
         _construct_constraint_msg_expiration_date, ["expiration_date"]),
    ]

    def create(self, cr, uid, vals, context=None):
        if vals.get('state') == 'credit_card':
            partner_obj = self.pool.get('res.partner').browse(
                cr, uid, vals['partner_id'], context=context)
            encrypt_cc_vals(partner_obj, vals)
        return super(res_partner_bank, self).create(cr, uid, vals,
                                                    context=context)

    def write(self, cr, uid, ids, vals, context=None):
        self_obj = self.browse(cr, uid, ids[0], context=context)
        try:
            state = vals['state']
        except KeyError:
            state = self_obj.state
        if state == 'credit_card':
            encrypt_cc_vals(self_obj.partner_id, vals)
        return super(res_partner_bank, self).write(cr, uid, ids, vals,
                                                   context=context)


class res_company(orm.Model):
    _inherit = 'res.company'

    def _get_short_pubkey(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for company in self.browse(cr, uid, ids, context=context):
            pubkey = company.cc_number_encrypt_key
            if pubkey:
                res[company.id] = pubkey[:30] + "..."
            else:
                res[company.id] = ""
        return res

    def _set_short_pubkey(self, cr, uid, id, name, value, fnct_inv_arg,
                          context):
        if len(value) > 40:
            # We only save the key if it's not the truncated value
            self.write(cr, uid, id, {'cc_number_encrypt_key': value})

    _columns = {
        'cc_number_encrypt_key_short': fields.function(
            _get_short_pubkey, fnct_inv=_set_short_pubkey,
            type='char', string='Credit Card Encryption Key'),
        'cc_number_encrypt_key': fields.char(
            'Credit Card Encryption Key', size=2048,
            help="Public key with which to encrypt our credit card number "
                 "before writing them to the DB"),
    }
