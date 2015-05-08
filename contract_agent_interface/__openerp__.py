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

{
    'name': 'Contract management interface',
    'version': '1.0',
    'category': 'Contract Management',
    'description': """
    Creates a unified interface to manage contracts/facturation for customer
    service agents. The view is based on the partner/client view, with more
    tabs added for contracts, invoices, etc...
    """,
    'author': 'Savoir-faire Linux Inc.',
    'website': 'www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'depends': [
        'contract_isp',
        'contract_isp_invoice',
        'stock',
    ],
    'data': [
        'security/contract_agent_interface_security.xml',
        'security/ir.model.access.csv',
        'contract_agent_interface_data.xml',
        'wizard/confirm_view.xml',
    ],
    'active': False,
    'installable': True,
}
