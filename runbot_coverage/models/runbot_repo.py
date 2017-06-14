# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import sys
from openerp import api, fields, models


class RunbotRepo(models.Model):
    _inherit = 'runbot.repo'

    use_coverage = fields.Boolean('Coverage', default=False)
    coverage_config = fields.Char(
        'Configuration file',
        help='Your coveragerc relative to the build path.')
    coverage_command = fields.Char(
        'Coverage command',
        help='Fill in the absolute path to your coverage script. '
        'If you leave this empty, `coverage` in your $PATH will be '
        'expected')

    @api.multi
    def _coverage_command(self, command, *args):
        self.ensure_one()
        return (
            ['coverage'] if not self.coverage_command else [
                sys.executable,
                self.coverage_command,
            ]
        ) + [command] + (
            ['--rcfile', self.coverage_config] if self.coverage_config
            else []
        ) + list(args)
