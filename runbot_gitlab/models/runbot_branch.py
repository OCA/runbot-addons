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

from openerp import models, fields


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"
    project_id = fields.Integer('VCS Project', select=1)
    merge_request_id = fields.Integer('Merge Request', select=1)

    def _get_branch_url(self, cr, uid, ids, field_name, arg, context=None):
        """For gitlab branches get gitlab MR formatted branches

        If not an MR (such as a main branch or github repo) call super
        function
        """
        r = {}
        other_branch_ids = []
        for branch in self.browse(cr, uid, ids, context=context):
            if branch.merge_request_id:
                r[branch.id] = "https://%s/merge_requests/%s" % (
                    branch.repo_id.base,
                    branch.merge_request_id,
                )
            else:
                other_branch_ids.append(branch.id)
        r.update(
            super(RunbotBranch, self)._get_branch_url(
                cr, uid, other_branch_ids, field_name, arg, context=context
            )
        )
        return r
