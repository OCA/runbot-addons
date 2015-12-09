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
    project_id = fields.Integer('VCS Project', select=1)
    merge_request_id = fields.Integer('Merge Request', select=1)
    branch_url = fields.Char(compute='_compute_branch_url')

    def _compute_branch_url(self):
        """For gitlab branches get gitlab MR formatted branches

        If not an MR (such as a main branch or github repo) call super
        function
        """
        for branch in self.filtered('merge_request_id'):
            if branch.merge_request_id:
                branch.branch_url = "%s/%s/merge_requests/%s" % (
                    branch.repo_id.gitlab_base_url,
                    branch.repo_id.gitlab_name,
                    branch.merge_request_id,
                )
        others = self - self.filtered('merge_request_id')
        others_by_id = {o.id: o for o in others}
        for rec_id, branch_url in others._get_branch_url('branch_url', None)\
                .iteritems():
            others_by_id[rec_id].branch_url = branch_url
