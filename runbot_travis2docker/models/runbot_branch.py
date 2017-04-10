# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    sync_weblate = fields.Boolean('Synchronize with Weblate')

    def cron_weblate(self, cr, uid, *args):
        for branch in self.search(cr, uid, [['sync_weblate', '=', True]]):
            build = self.pool['runbot.build']
            build_id = build.search(cr, uid, [['branch_id', '=', branch]],
                                    order='id DESC', limit=1)
            if build_id:
                build.force(cr, uid, build_id)
