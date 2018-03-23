# Copyright <2017> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import http
from odoo.http import request
from odoo.addons.runbot.controllers.hook import RunbotHook

_logger = logging.getLogger(__name__)


class RunbotCIController(RunbotHook):

    @http.route(['/runbot/hook_gitlab/<int:repo_id>',
                 '/runbot/hook_gitlab/org', '/runbot/hook/<int:repo_id>',
                 '/runbot/hook/org'])
    def hook(self, repo_id=None, **post):
        data = (request.jsonrequest if hasattr(request, 'jsonrequest') else
                json.loads(request.httprequest.stream.read()))
        event = data['object_kind'] if 'object_kind' in data else None
        repository = data['repository']
        if repo_id is None:
            if event in ['push', 'merge_request']:
                repo_domain = ['|', ('name', '=', repository['url']),
                               '|',
                               ('name', '=', repository['homepage']),
                               ('name', '=', repository['homepage'] + '.git')]
                repo = request.env['runbot.repo'].sudo().search(repo_domain,
                                                                limit=1)
                repo_id = repo.id
        return super(RunbotCIController, self).hook(repo_id, **post)
