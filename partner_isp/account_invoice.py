# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<www.savoirfairelinux.com>).
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

from openerp.osv import fields, orm


class AccountInvoice(orm.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    def _get_partner_code(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            res[inv.id] = inv.partner_id.code
        return res

    def _search_partner_code(self, cr, uid, obj, name, args, context):
        ids = set(
            partner_id
            for cond in args
            if len(cond) == 3
            for partner_id in self.pool["res.partner"].search(
                cr, uid,
                [('code', cond[1], cond[2])],
                context=context,
            )
        )
        if ids:
            return [('partner_id', 'in', tuple(ids))]
        else:
            return [('id', '=', 0)]

    _columns = {
        'partner_code': fields.function(
            _get_partner_code,
            fnct_search=_search_partner_code,
            type='char',
            method=True,
            string='Partner Code',
        ),
    }

    def invoice_print(self, cr, uid, ids, context=None):
        # Override print invoice to use our report
        result = super(AccountInvoice, self).invoice_print(
            cr, uid, ids, context=context)
        result['report_name'] = 'account.invoice.balance_payment.isp'
        return result
