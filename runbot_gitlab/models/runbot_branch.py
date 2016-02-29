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
from openerp import api, models, fields


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"
    project_id = fields.Char('VCS Project')
    merge_request_id = fields.Char('Merge Request')
    branch_url = fields.Char(compute='_compute_branch_url')

    @api.multi
    def _compute_branch_url(self):
        """For gitlab branches get gitlab MR formatted branches

        If not an MR (such as a main branch or github repo) call super
        function
        """
        gitlab_branches = self.filtered('repo_id.uses_gitlab')
        for branch in gitlab_branches:
            if branch.merge_request_id:
                branch.branch_url = "%s/%s/merge_requests/%s" % (
                    branch.repo_id.gitlab_base_url,
                    branch.repo_id.gitlab_name,
                    branch.merge_request_id,
                )
            else:
                branch.branch_url = "%s/%s/tree/%s" % (
                    branch.repo_id.gitlab_base_url,
                    branch.repo_id.gitlab_name,
                    branch.branch_name,
                )

        others = self - gitlab_branches
        others_by_id = {o.id: o for o in others}
        for rec_id, branch_url in others._get_branch_url('branch_url', None)\
                .iteritems():
            others_by_id[rec_id].branch_url = branch_url
