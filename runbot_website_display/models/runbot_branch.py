# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class RunbotBranch(models.Model):
    _inherit = 'runbot.branch'

    website_published = fields.Boolean(default=True)
