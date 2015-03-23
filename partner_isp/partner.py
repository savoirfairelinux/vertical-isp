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

import logging
import re
import unicodedata

from openerp.tools.translate import _
from openerp.osv import orm, fields
from openerp.addons.base.res.res_partner import get_unaccent_wrapper

_logger = logging.getLogger(__name__)


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _get_name_parts(self, name):
        """ Split name in parts """
        return re.findall(ur"\w+", name, re.UNICODE)

    def _check_customer_full_name(self, cr, uid, ids, context=None):
        for partner in self.browse(cr, uid, ids, context=None):
            if not partner.customer:
                continue
            if not len(self._get_name_parts(partner.name)) > 1:
                return False

        return True

    def _parent_is_reseller(self, cr, uid, ids, field_name, args,
                            context=None):
        res = {}

        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = (partner.parent_id and
                               partner.parent_id.is_reseller or False)

        return res

    def search(self, cr, user, args, offset=0, limit=None, order=None,
               context=None, count=False):
        for arg in args:
            if arg[0] == 'code' and arg[1] == 'startswith':
                arg[1] = '=ilike'
                arg[2] = '%s%%' % (arg[2], )

        return super(res_partner, self).search(cr, user, args,
                                               offset=offset,
                                               limit=limit,
                                               order=order,
                                               context=context,
                                               count=count)

    def _parent_is_reseller_search(self, cr, uid, ids, name, args,
                                   context=None):
        res = []
        partner_ids = self. search(
            cr, uid, [('customer', '=', True)], context=context)

        for partner in self.browse(cr, uid, partner_ids, context=context):
            if args[0][2] is False and not (
                    partner.parent_id is False or
                    partner.parent_id.is_reseller is False):
                res.append(partner.id)
            elif args[0][2] is True and (
                    partner.parent_id is not False and
                    partner.parent_id.is_reseller is True):
                res.append(partner.id)

        return [('id', 'in', res)]

    _columns = {
        'birthdate': fields.date('Birth date'),
        'representative': fields.char('Representative', size=64),
        'code': fields.char('Code', size=16),
        'representative_birthdate': fields.date('Representative birth date'),
        'is_reseller': fields.boolean('Reseller?'),
        'parent_is_reseller': fields.function(
            _parent_is_reseller,
            # fnct_search=_parent_is_reseller_search,
            type='boolean',
            string='Parent is reseller',
            store=True)
    }

    _constraints = [
        (_check_customer_full_name,
         _('You must provide a full name'), ['name']),
    ]

    _defaults = {
        'is_reseller': False,
        'user_id': lambda self, cr, uid, c: uid,
    }

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, int):
            ids = [ids]

        ret = super(res_partner, self).name_get(cr, uid, ids, context=context)
        ret1 = []

        for t in ret:
            partner = self.browse(cr, uid, t[0], context)
            if partner.customer is True and partner.code not in (False, ''):
                ret1.append((t[0], ' - '.join([partner.code, t[1]])))
            else:
                ret1.append(t)

        return ret1

    def name_search(self, cr, uid, name='', args=None,
                    operator='ilike', context=None, limit=100):
        if name and name.find(' - ') != -1:
            name = name.split(' - ')[1]

        # TAKEN FROM base/res/res_partner.py #
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):

            self.check_access_rights(cr, uid, 'read')
            where_query = self._where_calc(cr, uid, args, context=context)
            self._apply_ir_rules(cr, uid, where_query, 'read', context=context)
            from_clause, where_clause, where_clause_params = (
                where_query.get_sql())
            if where_clause:
                where_str = " WHERE %s AND " % (where_clause, )
            else:
                where_str = " WHERE "

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(cr)

            display_name = """
                CASE WHEN company.id IS NULL OR res_partner.is_company
                THEN {partner_name}
                ELSE {company_name} || ', ' || {partner_name}
                END
                """.format(partner_name=unaccent('res_partner.name'),
                           company_name=unaccent('company.name'))

            # Modified to add res_partner.representative
            query = """SELECT res_partner.id
                         FROM res_partner
                    LEFT JOIN res_partner company
                           ON res_partner.parent_id = company.id
                      {where} ({email} {operator} {percent}
                           OR res_partner.representative {operator} {percent}
                           OR {display_name} {operator} {percent})
                     ORDER BY {display_name}
                    """.format(where=where_str, operator=operator,
                               email=unaccent('res_partner.email'),
                               percent=unaccent('%s'),
                               display_name=display_name)

            where_clause_params += [search_name] * 3  # Nb of {percent} above
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            cr.execute(query, where_clause_params)
            ids = map(lambda x: x[0], cr.fetchall())

            if ids:
                return self.name_get(cr, uid, ids, context)
            else:
                return []

        return super(res_partner, self).name_search(
            cr, uid, name=name, args=args, operator=operator,
            context=context, limit=limit)

    def refresh_code(self, cr, uid, ids, name,
                     is_company=False,
                     is_reseller=False,
                     context=None):
        """Generates a partner code based on the following logic:

        [First family name initial] +
        [Second family name initial] +
        [Second name initial] +
        [First name initial] +
        [Incremental number]

        Ex:

        Carl Marx -> MC1
        Clark Manson -> MC2
        Jean-Philippe Tremblay -> TPJ1
        Joao Alfredo Gama Batista -> GBJA
        """
        if not name:
            return {}

        if isinstance(name, unicode):
            # unicodedata.normalize takes unicode, not str. Attempt to remove
            # accents if we got unicode, and refuse to guess if we did not.
            # Normally we should only be getting str if there were no special
            # characters in the name
            name = unicodedata.normalize('NFD', name).encode(
                'ascii', 'ignore').decode('ascii')
        initials = u"".join(
            item[0].upper() for item in self._get_name_parts(name))

        ret = {'value': None}
        seq = 1

        pos_list = []
        if len(initials) == 1:
            pos_list = [0]
        elif len(initials) == 2:
            pos_list = [1, 0]
        elif len(initials) == 3:
            pos_list = [2, 1, 0]
        elif len(initials) >= 4:
            pos_list = [2, 3, 0, 1]

        if is_reseller:
            prefix = u'RES'
        elif is_company:
            prefix = u'BUS'
        else:
            prefix = u''
        code = u'{}{}'.format(
            prefix,
            u''.join([w for y, w in sorted(zip(pos_list, initials))]),
        )

        while True:
            query = [('code', '=', code + str(seq)), ('customer', '=', True)]
            if not self.search(cr, uid, query, context=context):
                code = code + str(seq)
                break
            seq += 1
        ret['value'] = {'code': code}
        return ret

    def create(self, cr, uid, values, context=None):
        if 'code' not in values:
            values.update(
                self.refresh_code(
                    cr, uid, ids=None,
                    name=values['name'],
                    is_company=values.get('is_company'),
                    is_reseller=values.get('is_reseller'),
                    context=context,
                ).get('value', {})
            )

        return super(res_partner, self).create(
            cr, uid, values, context=context)
