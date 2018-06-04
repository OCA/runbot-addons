# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import psycopg2
from odoo import api, fields, models


class RunbotRepo(models.Model):
    _inherit = 'runbot.repo'

    preseed_database = fields.Char(
        help='Fill in the name of a database to use as template for the all '
        'build', copy=False,
    )
    preseed_database_module_ids = fields.Many2many(
        'runbot.preseed.database.module', string='Modules to install',
        help='Fill in some modules with long running tests like stock or '
        'accounting. Do not fill in modules here that should be tested.',
        copy=False,
    )
    preseed_database_build_id = fields.Many2one(
        'runbot.build', string='Preseed database build', ondelete='restrict',
        help='Select a build to use to generate the preseed database',
    )

    @api.constrains('preseed_database')
    def _check_preseed_database(self):
        for this in self:
            if not this.preseed_database:
                continue
            connection = psycopg2.connect('dbname=%s' % this.preseed_database)
            connection.close()
