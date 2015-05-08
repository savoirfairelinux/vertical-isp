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
from openerp.osv import orm
from openerp.tools.translate import _


class account_analytic_account(orm.Model):
    _inherit = 'account.analytic.account'
    _defaults = {
        'manager_id': lambda self, cr, uid, c: uid,
    }

    def open_contract(self, cr, uid, id, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': id[0],
            'target': 'current',
        }

    def _confirm_wizard(self, cr, uid, ids, method, context=None):

        return {
            'type': 'ir.actions.act_window',
            'src_model': 'account.analytic.account',
            'res_model': 'contract.isp.confirm_action',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_method': method,
                'default_account_id': ids[0],
            },
        }

    def set_pending(self, cr, uid, ids, context=None):
        if context and context.get("confirm_set_pending"):
            return super(account_analytic_account, self).set_suspend(
                cr, uid, ids, context=context)
        else:
            return self._confirm_wizard(cr, uid, ids, "set_pending",
                                        context=context)

    def set_cancel(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids, context=None):
            if contract.invoice_ids:
                raise orm.except_orm(
                    _("Not allowed"),
                    _("You cannot cancel a contract that has been invoiced"),
                )

        if context and context.get("confirm_set_cancel"):
            return super(account_analytic_account, self).set_cancel(
                cr, uid, ids, context=context)
        else:
            return self._confirm_wizard(cr, uid, ids, "set_cancel",
                                        context=context)

    def action_cancel_multi(self, cr, uid, ids, context=None):
        ids = context.pop("active_ids", None)
        if not ids:
            return {}

        context["confirm_set_cancel"] = True
        self.set_cancel(cr, uid, ids, context)
        return {}
