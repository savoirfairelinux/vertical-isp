# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class ConfirmWizard(orm.TransientModel):
    _name = 'contract.isp.confirm_action'

    _columns = {
        'account_id': fields.many2one('account.analytic.account', 'Contract',
                                      required=True),
        'method': fields.char('Action', size=64, required=True),
    }

    def do_confirm(self, cr, uid, ids, context=None):
        context = context or {}
        account_obj = self.pool["account.analytic.account"]
        wizard = self.browse(cr, uid, ids[0], context=context)
        if wizard.method.startswith("_"):
            raise orm.except_orm(
                _("Invalid method name"),
                _("You are not allowed to use private methods"),
            )

        func = getattr(account_obj, wizard.method, None)
        if func is None:
            raise orm.except_orm(
                _("No such method %s") % (wizard.method),
                _("Make sure to pass a valid account.analytic.account "
                  "public method name"),
            )

        context[u"confirm_" + wizard.method] = True
        return func(cr, uid, [wizard.account_id.id], context=context)
