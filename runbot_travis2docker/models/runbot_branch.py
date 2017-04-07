# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    sync_weblate = fields.Boolean('Synchronize with Weblate')

    def cron_weblate(self, uid, *args):
        for branch in self.search(uid, args, [['sync_weblate', '=', True]]):
            pass
