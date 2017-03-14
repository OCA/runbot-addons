# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import operator
from openerp import http
from openerp.addons.runbot.runbot import RunbotController


class RunbotController(RunbotController):
    @http.route()
    def repo(self, repo=None, search='', limit='100', refresh='', **post):
        result = super(RunbotController, self).repo(
            repo=repo, search=search, limit=limit, refresh=refresh, **post)
        result.qcontext['repos'] = result.qcontext['repos']\
            .sorted(operator.itemgetter('sequence'))\
            .filtered('website_published')
        return result
