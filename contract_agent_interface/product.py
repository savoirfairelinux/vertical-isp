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
import openerp.addons.decimal_precision as dp


class product(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'standard_price': fields.float(
            'Cost', digits_compute=dp.get_precision('Product Price'),
            help="Cost price of the product used for standard stock valuation "
                 "in accounting and used as a base price on purchase orders.",
            groups="base.group_user,contract_isp.group_isp_agent")
    }
