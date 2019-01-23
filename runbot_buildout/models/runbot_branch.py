# Copyright 2017-2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import re
from openerp import api, fields, models


PYTHON2 = '/usr/bin/python2'
PYTHON3 = '/usr/bin/python3'


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

    @api.multi
    def get_interpreter(self):
        """Determine python version to use from buildout version or name.

        Odoo versions before 11.0 run on python2. Later versions on python3.
        """
        self.ensure_one()
        name = self.buildout_version or \
            self.branch_id.pull_head_name or self.branch_id.name
        firstint = re.compile(r'\d+')
        major = firstint.search(name)
        if not major:
            return PYTHON2  # If for some reason version not found.
        version = int(major.group(0))
        if version < 11:
            return PYTHON2
        return PYTHON3
