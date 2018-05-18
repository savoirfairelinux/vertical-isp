# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<www.savoirfairelinux.com>).
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
##############################################################################

import logging
import sys

from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


PROCESS_CRON = 'cron'
PROCESS_INITIAL = 'initial'
PROCESS_MANUAL = 'manual'
PROCESS_PRORATA = 'prorata'
PROCESS_RECURRENT = 'recurrent'


class Invoice(orm.Model):
    _name = _inherit = 'account.invoice'
    _columns = {
        'source_process': fields.selection([
            (PROCESS_CRON, 'Scheduled'),
            (PROCESS_INITIAL, 'Initial'),
            (PROCESS_MANUAL, 'Manual'),
            (PROCESS_PRORATA, 'Pro Rata'),
            (PROCESS_RECURRENT, 'Recurrent Billing'),
        ], 'Billing Process', required=False),
        'to_send': fields.boolean('To Send by Email'),
    }
    _defaults = {
        'to_send': False,
    }

    def write(self, cr, uid, ids, values, context=None):
        if values.get('sent'):
            values['to_send'] = False
        return super(Invoice, self).write(cr, uid, ids, values,
                                          context=context)

    def send_email_contract_invoice(self, cr, uid, ids, context=None):
        context = context or {}

        if not isinstance(ids, list):
            ids = [ids]

        mail_template_obj = self.pool.get('email.template')
        ir_model_data_obj = self.pool.get('ir.model.data')
        mail_template_id = ir_model_data_obj.get_object_reference(
            cr, uid, 'account',
            'email_template_edi_invoice')[1]
        mail_mail_obj = self.pool.get('mail.mail')

        for inv in ids:
            _logger.info("Mailing invoice %s", inv)

            try:
                mail_id = mail_template_obj.send_mail(
                    cr, uid, mail_template_id, inv, context=context)
                mail_message = mail_mail_obj.browse(
                    cr, uid, mail_id,
                    context=context).mail_message_id
                mail_message.write({'type': 'email'})
            except:
                _logger.error(
                    'Error generating mail for invoice %s: \n\n %s',
                    self.browse(
                        cr, uid, inv, context=context).name,
                    sys.exc_info()[0])
            else:
                self.write(cr, uid, [inv],
                           {'to_send': False},
                           context=context)

        return True

    def send_pending_invoices(self, cr, uid, ids, company_id=None, context=None):
        """
        Send invoices that have been marked `to_send`
        """
        domain = [('to_send', '=', True)]
        if company_id:
            domain.append(('company_id', '=', company_id))
        if ids:
            domain.append(('id', 'in', ids))

        to_send = self.search(cr, uid, domain, context=context)
        self.send_email_contract_invoice(cr, uid, to_send, context=context)
        return True

    def _auto_init(self, cr, context=None):
        res = super(Invoice, self)._auto_init(cr, context=context)

        # Create indexes that will speed up invoicing
        for idx, on in (("account_invoice_partner_date_index",
                         "account_invoice (partner_id, date_invoice)"),
                        ("res_partner_bank_company_active_index",
                         "res_partner_bank (company_id, active)")):
            cr.execute("""
                       SELECT indexname FROM pg_indexes
                       WHERE indexname = %s
                       """,
                       (idx, ))
            if not cr.fetchall():
                cr.execute("CREATE INDEX {0} ON {1}".format(idx, on))
                cr.commit()

        return res
