# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class RunbotPreseedDatabaseModule(models.Model):
    _name = 'runbot.preseed.database.module'
    _description = 'Preseed database module'

    name = fields.Char(required=True)
