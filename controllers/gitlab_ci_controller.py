# Copyright <2017> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import http
from odoo.addons.runbot.controllers.hook import RunbotHook
from odoo.http import request

_logger = logging.getLogger(__name__)


class RunbotCIController(RunbotHook):

    @http.route(
        ['/runbot/hook_gitlab/<int:repo_id>', '/runbot/hook_gitlab/org'],
        type='json', auth="public", website=True, csrf=False)
    def hook_gitlab(self, repo_id=None, **post):
        if repo_id:
            return self.hook(repo_id, **post)
        data = request.jsonrequest
        event = data.get('object_kind')
        if event in ['push', 'merge_request']:
            # Compatible with gitlab version >=8.5 and <8.5
            project = data.get('project') or data.get('repository')
            ssh_url = project.get('git_ssh_url') or project.get('ssh_url')
            http_url = project.get('git_http_url') or project.get('http_url')
            repo_domain = ['|', '|', ('name', '=', ssh_url),
                           ('name', '=', http_url),
                           ('name', '=', http_url.rstrip('.git'))]
            repo = request.env['runbot.repo'].sudo().search(repo_domain,
                                                            limit=1)
            if repo:
                return self.hook(repo.id, **post)
        return ""
