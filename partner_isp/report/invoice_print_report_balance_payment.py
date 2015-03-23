# -*- encoding: utf-8 -*-
###############################################################################
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
###############################################################################

from datetime import datetime, timedelta

from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class InvoiceReport(report_sxw.rml_parse):
    BILL_DELAY = 3
    BILL_DURATION = 5

    def __init__(self, cr, uid, name, context=None):
        super(InvoiceReport, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'get_payment_message': self._get_payment_message,
        })

    def _message_manual(self, invoice):
        if invoice.date_due:
            return _(
                'The payment of {amount} must be received before {date_due}'
            ).format(
                date_due=invoice.date_due,
                amount=self.formatLang(invoice.to_pay, monetary=True,
                                       currency_obj=invoice.currency_id),
            )
        elif invoice.payment_term:
            return invoice.payment_term.note
        else:
            return ''

    def _get_bill_interval(self, invoice):
        invoice_day = int(invoice.company_id.invoice_day)
        billing_day = invoice.company_id.billing_day
        if not billing_day:
            billing_day = int(invoice_day) + self.BILL_DELAY
        else:
            billing_day = int(billing_day)

        inv_day = datetime.strptime(invoice.date_invoice,
                                    DEFAULT_SERVER_DATE_FORMAT)

        start = inv_day.replace(day=billing_day)
        end = start + timedelta(days=self.BILL_DURATION)
        return start, end

    def _message_credit_card(self, invoice):
        bill_start, bill_end = self._get_bill_interval(invoice)

        return _(
            'The payment of {amount} will be automatically charged on the '
            'credit card ending with {last_digits} between the {bill_start} '
            'and {bill_end}.'
        ).format(
            amount=self.formatLang(invoice.to_pay, monetary=True,
                                   currency_obj=invoice.currency_id),
            last_digits=invoice.partner_bank_id.acc_number[-4:],
            bill_start=self.formatLang(bill_start, date=True),
            bill_end=self.formatLang(bill_end, date=True),
        )

    def _message_bank(self, invoice):
        bill_start, bill_end = self._get_bill_interval(invoice)
        return _(
            'The payment of {amount} will be withdrawn from your '
            'pre-authorized bank account between the '
            '{bill_start} and {bill_end}.'
        ).format(
            amount=self.formatLang(invoice.to_pay, monetary=True,
                                   currency_obj=invoice.currency_id),
            bill_start=self.formatLang(bill_start, date=True),
            bill_end=self.formatLang(bill_end, date=True),
        )

    def _get_payment_message(self, invoice):
        if not invoice.partner_bank_id:
            # Use payment term
            return self._message_manual(invoice)
        payment_type = invoice.partner_bank_id.state
        if payment_type == 'credit_card':
            return self._message_credit_card(invoice)
        elif payment_type == 'bank_ca':
            return self._message_bank(invoice)
        return ''

report_sxw.report_sxw(
    'report.account.invoice.balance_payment.isp',
    'account.invoice',
    'addons/partner_isp/report/invoice_print_report_balance_payment.rml',
    parser=InvoiceReport,
)
