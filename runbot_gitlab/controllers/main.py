# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import http
from openerp.addons.runbot.runbot import RunbotController


class RunbotController(RunbotController):
    @http.route()
    def repo(self, repo=None, search='', limit='100', refresh='', **post):
        '''sort branches with MRs first after sticky ones'''
        result = super(RunbotController, self).repo(
            repo=repo, search=search, limit=limit, refresh=refresh, **post)
        if 'branches' in result.qcontext:
            result.qcontext['branches'] = sorted(
                result.qcontext['branches'],
                lambda x, y: cmp(x['branch'].name, y['branch'].name)
                if x['branch'].sticky == y['branch'].sticky and
                bool(x['branch'].merge_request_id) ==
                bool(y['branch'].merge_request_id)
                else -1
                if x['branch'].sticky and x['branch'].merge_request_id or
                x['branch'].sticky and not y['branch'].sticky or
                not y['branch'].sticky and x['branch'].merge_request_id
                else 1)
        return result
