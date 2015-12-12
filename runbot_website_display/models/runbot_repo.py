# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class RunbotRepo(models.Model):
    _inherit = 'runbot.repo'

    _order = 'sequence asc'

    sequence = fields.Integer()
    website_published = fields.Boolean(default=True)
