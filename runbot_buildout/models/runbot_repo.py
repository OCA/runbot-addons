# Copyright 2017-2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class RunbotRepo(models.Model):
    _inherit = 'runbot.repo'

    uses_buildout = fields.Boolean('Use buildouts')
    buildout_branch_pattern = fields.Char(
        'Pattern for buildout branches', required=True,
        default=r'buildout-(?P<version>\d+\.\d+)',
        help='A regex to recognize buildout branches within this repository. '
        'This must contain exactly one named group to parse the version this '
        'buildout is meant for. This is used to pick the correct buildout for '
        'building other branches',
    )
    buildout_section = fields.Char(
        'Buildout section', required=True,
        default='odoo',
        help='The buildout section you use to create your odoo instance'
    )
