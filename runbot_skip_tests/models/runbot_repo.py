# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class RunbotRepo(models.Model):
    _inherit = 'runbot.repo'

    skip_test = fields.Boolean(
        'Skip tests', default=True,
        help='This removes --test-enable from the odoo commandline, '
        'allowing you to browse a built instance without waiting for tests')
    skip_build = fields.Boolean(
        'Skip builds', default=False,
        help='This stops building after a repository is pulled. '
        'Use this if you only need this repository as a dependency of '
        'something else')
