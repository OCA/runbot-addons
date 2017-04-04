# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Allow old api because is based original methods are old api from odoo
# pylint: disable=old-api7-method-defined

from openerp import models


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    def _get_branch_quickconnect_url(self, cr, uid, ids, fqdn, dest,
                                     context=None):
        """Remove debug=1 because is too slow
        Remove database default name because is used openerp_test from MQT
        """
        res = super(RunbotBranch, self)._get_branch_quickconnect_url(
            cr, uid, ids, fqdn, dest, context=context)
        for branch in self.browse(cr, uid, ids, context=context):
            if branch.repo_id.is_travis2docker_build:
                dbname = "db=%s-all&" % dest
                res[branch.id] = res[branch.id].replace(dbname, "").replace(
                    "?debug=1", "")
        return res
