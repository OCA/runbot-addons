# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2010 Savoir-faire Linux
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
import logging
from gitlab3 import GitLab
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

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
            return regular_func(*args, **kwargs)
    return gitlab_func


def get_gitlab_project(base, token, id=None):
    mo = re.search('([^/]+)(/(\d+))/([^/]+)/([^/.]+)(\.git)?', base)
    if not mo:
        return
    domain = mo.group(1)
    port = mo.group(3)
    namespace = mo.group(4)
    name = mo.group(5)
    prefix = 'http' if base.startswith('http/') else 'https'
    if port:
        domain += ":%d" % int(port)
    gl = GitLab("%s://%s" % (prefix, domain), token)
    if id:
        return gl.project(id)
    return gl.find_project(path_with_namespace='%s/%s' % (namespace, name))


class runbot_repo(models.Model):
    _inherit = "runbot.repo"
    uses_gitlab = fields.Boolean('Use Gitlab')

    @api.one
    @gitlab_api
    def github(self, url, payload=None, delete=False):
        project = get_gitlab_project(self.base, self.token)
        if payload:
            logger.exception(
                "Wanted to post payload %s at %s" % (url, payload)
            )
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

    @api.one
    @gitlab_api
    def update(self):
        project = get_gitlab_project(self.base, self.token)

        merge_requests = project.find_merge_request(
            find_all=True
        )
        # Find new MRs and new builds
        for mr in project.find_merge_request(
                find_all=True,
                cached=merge_requests,
                state='opened'):
            source_project = get_gitlab_project(
                self.base, self.token, mr.source_project_id
            )
            name = mr.source_branch
            source_branch = source_project.branch(name)
            commit = source_branch.commit
            sha = commit['id']
            date = commit['committed_date']
            # TODO: TMP workaround for tzinfo bug
            # https://github.com/alexvh/python-gitlab3/issues/15
            date.tzinfo.dst = lambda _: None
            author = commit['author']['name']
            committer = commit['committer']['name']
            subject = commit['message']
            title = mr.title
            # Create or get branch
            branch_ids = self.env['runbot.branch'].search([
                ('repo_id', '=', self.id),
                ('project_id', '=', project.id),
                ('merge_request_id', '=', mr.id),
            ])
            if branch_ids:
                branch_id = branch_ids[0]
            else:
                logger.debug('repo %s found new Merge Proposal %s',
                             self.name, title)
                branch_id = self.env['runbot.branch'].create({
                    'repo_id': self.id,
                    'name': title,
                    'project_id': project.id,
                    'merge_request_id': mr.id,
                })
            # Create build (and mark previous builds as skipped) if not found
            build_ids = self.env['runbot.build'].search([
                ('branch_id', '=', branch_id.id),
                ('name', '=', sha),
            ])
            if not build_ids:
                logger.debug(
                    'repo %s merge request %s new build found commit %s',
                    branch_id.repo_id.name,
                    branch_id.name,
                    sha,
                )
                self.env['runbot.build'].create({
                    'branch_id': branch_id.id,
                    'name': sha,
                    'author': author,
                    'committer': committer,
                    'subject': subject,
                    'date': date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'modules': branch_id.repo_id.modules,
                })

        # Clean-up old MRs
        closed_mrs = list(i.id for i in project.find_merge_request(
            find_all=True,
            cached=merge_requests,
            state='closed'
        ))

        closed_mrs = self.env['runbot.branch'].search([
            ('merge_request_id', 'in', closed_mrs),
        ])

        for mr in closed_mrs:
            mr.unlink()

        super(runbot_repo, self).update()

        # Skip non-sticky non-merge proposal builds
        branches = self.env['runbot.branch'].search([
            ('sticky', '=', False),
            ('repo_id', 'in', [i.id for i in self]),
            ('project_id', '=', False),
            ('merge_request_id', '=', False),
        ])
        for build in self.env['runbot.build'].search([
                ('branch_id', 'in', [b.id for b in branches])]):
            build.skip()
