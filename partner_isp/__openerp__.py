# -*- coding: utf-8 -*-

#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux Inc. (<www.savoirfairelinux.com>).
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
    'name': 'Partner for ISPs',
    'version': '1.0',
    'category': 'CRM',
    'description': """
    A partner suitable for ISP companies
    ====================================

    This module provides some minor modifications to the res.partner model
    including:

    * A customer code based on the customers name,
    * Required ZIP code, phone and e-mail fields,
    * A representative field,
    * A birthday field for contacts and representatives.
    * Put the language in the main partner form page
    * Make user_id (Sales Rep) field read-only and set to current user
    * Rename Mobile to Tel2
    """,
    'author': 'Savoir-faire Linux Inc.',
    'website': 'www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',
        'account_voucher',
        'invoice_print_report_balance_payment',
        'web_datetime_options',
    ],
    'data': [
        'account_data.xml',
        'partner_isp_data.xml',
        'reports.xml',
    ],
    'active': False,
    'installable': True,
}
