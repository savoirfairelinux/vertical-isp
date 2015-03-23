# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
###############################################################################

from openerp.tests.common import TransactionCase

from ..encrypted_credit_card import (
    obfuscate_cc,
)


class TestEncrypt(TransactionCase):
    def test_obfuscate(self):
        for number, expected in [
            ('5555555555554444', '5555-55XX-XXXX-4444'),
            ('5555-5555-5555-4444', '5555-55XX-XXXX-4444'),
            ('5555 5555 5555 4444', '5555-55XX-XXXX-4444'),
            ('5105105105105100', '5105-10XX-XXXX-5100'),
            ('4111111111111111', '4111-11XX-XXXX-1111'),
            ('4012888888881881', '4012-88XX-XXXX-1881'),
            ('4222222222222', '4222-22XX-X222-2'),
        ]:
            self.assertEquals(obfuscate_cc(number), expected)
