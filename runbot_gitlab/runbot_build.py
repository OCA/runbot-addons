# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2010 Savoir-faire Linux
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
##############################################################################

from openerp import models, fields, api


class runbot_build(models.Model):
    _inherit = "runbot.build"
    dest = fields.Char(
        string='Dest',
        compute='_get_dest',
        readonly=True,
        store=True,
    )

    @api.multi
    def _get_dest(self):
        default_builds = self.browse(
            [b.id for b in self if not b.branch_id.merge_request_id]
        )
        res = super(runbot_build, default_builds)._get_dest(
            field_name=None, arg=None
        )
        for build in self:
            self.dest = res.get(build.id, '')
