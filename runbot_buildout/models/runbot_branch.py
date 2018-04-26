# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import re
from openerp import api, fields, models


class RunbotBranch(models.Model):
    _inherit = 'runbot.branch'

    buildout_default = fields.Boolean('Default buildout')
    buildout_version = fields.Char(
        compute='_compute_buildout_version', store=True,
    )
    buildout_section = fields.Char(
        'Alternative buildout section',
        help='If this branch uses another section then the repo, '
        'fill it in here',
    )
    buildout_branch_id = fields.Many2one(
        'runbot.branch', help='Default buildout branch',
        domain='[("repo_id", "=", repo_id)]',
    )

    @api.multi
    @api.depends(
        'name', 'repo_id.uses_buildout', 'repo_id.buildout_branch_pattern'
    )
    def _compute_buildout_version(self):
        for this in self:
            if not this.repo_id.uses_buildout:
                continue
            match = re.match(
                this.repo_id.buildout_branch_pattern, this.name.split('/')[-1],
            )
            if not match:
                continue
            this.update({'buildout_version': match.groupdict()['version']})
