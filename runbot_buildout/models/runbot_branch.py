# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import re
from openerp import api, fields, models


class RunbotBranch(models.Model):
    _inherit = 'runbot.branch'

    buildout_default = fields.Boolean('Default buildout')
    buildout_version = fields.Char(
        'Buildout version', compute='_compute_buildout_version',
        store=True,
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
