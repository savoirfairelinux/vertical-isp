# -*- coding: utf-8 -*-

#
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
#
#
from openerp.osv import orm, fields


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _get_analytic_lines(self, cr, uid, ids, field_name,
                            arg=None, context=None):

        account_analytic_account_obj = self.pool.get(
            'account.analytic.account')
        account_analytic_line_obj = self.pool.get('account.analytic.line')
        ir_model_data_obj = self.pool.get('ir.model.data')

        query1 = [
            ('state', '=', 'open'),
            ('partner_id', '=', ids[0]),
            ('type', '=', 'contract')
        ]

        contract_ids = account_analytic_account_obj.search(cr, uid, query1,
                                                           context=context)

        query2 = [('account_id', 'in', contract_ids)]
        if arg and arg.get('journal_id', False):
            module, ref_name = arg['journal_id'].split('.')
            journal_id = ir_model_data_obj.get_object_reference(cr, uid,
                                                                module,
                                                                ref_name)[1]
            query2.append(('journal_id', '=', journal_id))

        line_ids = account_analytic_line_obj.search(cr, uid,
                                                    query2,
                                                    context=context)

        return {ids[0]: line_ids}

    _columns = {
        'account_analytic_account_ids': fields.one2many(
            'account.analytic.account',
            'partner_id',
            'Analytic Accounts/Contracts',
            domain=[('type', '=', 'contract')]),
        'analytic_data_lines': fields.function(
            _get_analytic_lines,
            type="one2many",
            obj='account.analytic.line',
            arg={'journal_id': 'contract_isp.analytic_journal_data'},
            string='Account Lines'),
        'analytic_tel_lines': fields.function(
            _get_analytic_lines,
            type="one2many",
            obj='account.analytic.line',
            arg={'journal_id': 'contract_isp.analytic_journal_tel'},
            string='Account Lines'),
        'invoice_ids': fields.one2many(
            'account.invoice',
            'partner_id',
            'Invoices',
            domain=[('type', '=', 'out_invoice')]),
        'refund_ids': fields.one2many(
            'account.invoice',
            'partner_id',
            'Refunds',
            domain=[('type', '=', 'out_refund')]),
        'payments_ids': fields.one2many(
            'account.voucher',
            'partner_id',
            'Payments'),
        'all_bank_ids': fields.one2many(
            'res.partner.bank', 'partner_id', 'Banks',
            domain=['|', ('is_active', '=', False), ('is_active', '=', True)],
        ),
        'nsf_lines': fields.one2many(
            'account.move.line', 'partner_id', 'NSF',
            domain=['&',
                    ('name', 'like', 'NSF-%'),
                    ('account_id.type', '=', 'receivable'),
                    ],
        ),
    }
