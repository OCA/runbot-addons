# Copyright <2017> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    # pylint: disable=method-compute
    branch_url = fields.Char(compute='_get_branch_url')

    @api.depends('branch_name')
    def _get_branch_url(self):
        super(RunbotBranch, self)._get_branch_url()
        for branch in self.filtered('repo_id.uses_gitlab'):
            if branch.branch_name.isdigit():
                branch.branch_url = "https://%s/merge_requests/%s" % (
                    branch.repo_id.base, branch.branch_name)
            else:
                branch.branch_url = ("https://%s/tree/%s" % (
                    branch.repo_id.base, branch.branch_name))
