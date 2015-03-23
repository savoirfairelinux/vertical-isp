# -*- encoding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

{
    "name": "Encrypted Credit Cards",
    "version": "1.0",
    "author": "Savoir-faire Linux",
    "website": "http://www.savoirfairelinux.com",
    "category": "Accounting & Finance",
    "description": """
    Adds a new "Credit Card" bank type.

    This new bank type stores credit card numbers in an encrypted form, using a
    public key stored in res.company.

    To comply with PCI-DSS, we never ever store the credit card number in the
    DB, so the bank type record's 'acc_number' field contains stuff like
    "XXXX-XXXX-XXXX-1234". The actual credit card number is stored in
    "encrypted_cc_number", encrypted with the company's public key.

    The encryption method used is RSA. Because we store the encrypted CC number
    in a char() field and that encrypted data is binary, we encode that
    encrypted CC number in base64.

    This way, someone with full access to the DB is still unable to extract CC
    number unless he also has access to the private key, which hopefully is
    stored elsewhere, in a very secure place.

    We don't do any decryption here. It's up to another process to have access
    to the private key and decrypt those numbers.

    This module requires PyCrypto ( https://pypi.python.org/pypi/pycrypto )
    """,
    "depends": ['sale'],
    'external_dependencies': {
        'python': ['Crypto'],
    },
    "init_xml": [],
    'data': [
        'encrypted_credit_card_data.xml',
        'encrypted_credit_card_view.xml',
    ],
    "demo_xml": [],
    "installable": True,
    "certificate": ''
}
