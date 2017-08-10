# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import http
from openerp.http import request
from openerp.addons.runbot import runbot


class RunbotController(runbot.RunbotController):
    def build_info(self, build):
        result = super(RunbotController, self).build_info(build)
        result['buildout_version'] = build.branch_id.buildout_version
        return result

    @http.route(
        ["/runbot/build/<model('runbot.build'):build>/rerun_buildout"],
        type='http', auth="public", methods=['POST'], csrf=False,
    )
    def build_rerun_buildout(self, build, **post):
        if build.sudo().branch_id.buildout_version:
            build.sudo().write({
                'state': 'testing',
                'result': False,
                'job': 'job_10_test_base',
            })
        return http.local_redirect('/runbot/repo/%s' % build.repo_id.id)
