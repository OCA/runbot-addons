# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re
import simplejson
import logging
from gitlab3 import GitLab
from openerp import models, fields, api

logger = logging.getLogger(__name__)


def gitlab_api(func):
    """Decorator for functions which should be overwritten only if
    uses_gitlab is enabled in repo.
    """
    def gitlab_func(self, *args, **kwargs):
        if self.uses_gitlab:
            return func(self, *args, **kwargs)
        else:
            regular_func = getattr(super(runbot_repo, self), func.func_name)
            return regular_func(self, *args, **kwargs)
    return gitlab_func


class runbot_repo(models.Model):
    _inherit = "runbot.repo"
    uses_gitlab = fields.Boolean('Use Gitlab')

    @api.one
    @gitlab_api
    def github(self, url, payload=None, delete=False):
        mo = re.search('([^/]+)/([^/]+)/([^/.]+)(\.git)?', self.base)
        if not mo:
            return
        domain = mo.group(1)
        owner = mo.group(2)
        name = mo.group(3)
        url = url.replace(':owner', owner)
        url = url.replace(':repo', name)
        url = 'https://api.%s%s' % (domain, url)
        gl = GitLab("https://%s" % domain, self.token)
        if payload:
            logger.exception("Wanted to post payload %s at %s" % (url, payload))
            # r = gl._post(url, data=simplejson.dumps(payload))
            r = {}
        elif delete:
            logger.exception("Wanted to delete %s" % url)
            # r = gl._delete(url)
            r = {}
        else:
            logger.exception("Wanted to get %s" % url)
            # r = gl.find_project(path_with_namespace="%s/%s" % (owner, name))
            # r = gl._get(url)
            r = {}
        return r
