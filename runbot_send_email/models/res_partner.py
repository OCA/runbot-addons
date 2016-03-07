# coding: utf-8
# © 2016 Vauxoo
#   Coded by: lescobar@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class Partner(models.Model):
    _name = "res.partner"
    _inherit = 'res.partner'

    notify_email = fields.Selection(default='none')
