# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    sync_weblate = fields.Boolean('Synchronize with Weblate')

    @api.model
    def cron_weblate(self):
        for branch in self.search([('sync_weblate', '=', True)]):
            self.env['runbot.build'].create({'branch_id': branch.id,
                                             'name': 'HEAD',
                                             'sync_weblate': True})
