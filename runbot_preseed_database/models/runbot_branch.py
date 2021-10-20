# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class RunbotBranch(models.Model):
    _inherit = 'runbot.branch'

    preseed_database = fields.Char(
        help='Fill in the name of a database to use as template for the all '
        'build', copy=False,
    )
    preseed_database_module_ids = fields.Many2many(
        'runbot.preseed.database.module', string='Modules to install',
        copy=False,
    )
    preseed_database_build_id = fields.Many2one(
        'runbot.build', string='Preseed database build', ondelete='restrict',
        help='Select a build to use to generate the preseed database',
    )

    @api.constrains('preseed_database')
    def _check_preseed_database(self):
        self.env['runbot.repo']._check_preseed_database.__func__(self)
