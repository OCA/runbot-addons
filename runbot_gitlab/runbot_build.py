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

from openerp.osv import orm

from .runbot_repo import escape_branch_name


class runbot_build(orm.Model):
    _inherit = "runbot.build"

    def _get_dest(self, cr, uid, ids, field_name=None, arg=None, context=None):
        r = {}
        other_ids = []
        for build in self.browse(cr, uid, ids, context=context):
            if (build.branch_id.merge_request_id
                    or '/' not in build.branch_id.name):
                nickname = escape_branch_name(build.branch_id.name)
                r[build.id] = "%05d-%s-%s" % (
                    build.id, nickname, build.name[:6]
                )
            else:
                other_ids.append(build.id)
        if other_ids:
            r.update(super(runbot_build, self)._get_dest(
                cr, uid, other_ids, field_name, arg, context=context
            ))
        return r
