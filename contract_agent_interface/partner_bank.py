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

from openerp.osv import fields, orm


class PartnerBank(orm.Model):
    _name = 'res.partner.bank'
    _inherit = 'res.partner.bank'

    def _get_active(self, cr, uid, ids, field_name, arg, context):
        res = {}
        context = context or {}
        context["active_test"] = False
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = obj.active
        return res

    _columns = {
        'is_active': fields.function(
            _get_active,
            type="bool",
            method=True,),

    }
