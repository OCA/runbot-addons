# coding: utf-8
# © 2016 Vauxoo
#   Coded by: lescobar@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class Partner(models.Model):
    _name = "res.partner"
    _inherit = 'res.partner'
    # This change is made to the default partner will not receive mail, only
    # those that are explicitly marked as always, this will be marked through
    # a server action.
    notify_email = fields.Selection(default='none')
