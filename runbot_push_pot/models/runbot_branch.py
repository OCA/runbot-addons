# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class RunbotBranch(models.Model):
    _inherit = 'runbot.branch'

    push_pot = fields.Boolean(
        default=False, help='Enable this on your stable branch to have runbot '
        'push new translatable strings to your repo. Note this will overwrite '
        'your existing pot file',
    )
