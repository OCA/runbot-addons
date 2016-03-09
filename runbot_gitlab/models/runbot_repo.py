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
import json
import logging
import requests
import itertools
import urllib
import unicodedata
import dateutil
import operator

from openerp import models, fields, api, exceptions, release
from openerp.tools.translate import _

logger = logging.getLogger(__name__)

GITLAB_CI_API_URL = '%s/ci/api/v1/%s'
GITLAB_API_URL = '%s/api/v3/%s'


branch_name_subs = [
    (' ', '-'),
    (',', '-'),
    ('.', '-'),
    ('/', '-'),
    ('[', ''),
    (']', ''),
    ('#', ''),
]


def strip_accents(unicode_string):
    """Remove accents and greek letters from string

    :param unicode_string: String with possible accents
    :type unicode_string: unicode
    :return: String of unicode_string without accents
    :rtype: unicode
    """
    return ''.join(
        char for char in unicodedata.normalize('NFD', unicode_string)
        if not unicodedata.combining(char)
    )


def escape_branch_name(branch_name):
    for subs in branch_name_subs:
        branch_name = branch_name.replace(*subs)
    return urllib.quote_plus(strip_accents(branch_name))


def gitlab_api(func):
    """Decorator for functions which should be overwritten only if
    uses_gitlab is enabled in repo.
    """

    def gitlab_func(self, *args, **kwargs):
        if self.uses_gitlab:
            return func(self, *args, **kwargs)
        else:
            regular_func = getattr(super(RunbotRepo, self), func.func_name)
            return regular_func(*args, **kwargs)
    return gitlab_func


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    uses_gitlab = fields.Boolean(string='Use Gitlab')

    mr_only = fields.Boolean(
        string="MR Only",
        default=True,
        help="Build only merge requests and skip regular branches")

    sticky_protected = fields.Boolean(
        string="Sticky for Protected Branches",
        default=True,
        help="Set all protected branches on the repository as sticky")

    active_branches = fields.Boolean(
        string="Active Branches Only",
        default=False,
        help="Remove branches that are no longer present "
               "on the remote repository",
    )

    gitlab_base_url = fields.Char(
        'Gitlab base url', compute='_get_gitlab_params')
    gitlab_name = fields.Char(
        'Gitlab name', compute='_get_gitlab_params')

    @api.one
    @api.depends('base')
    def _get_gitlab_params(self):
        mo = re.search(r'([^/]+)(/(\d+))?/([^/]+)/([^/.]+)(\.git)?', self.base)
        if not mo:
            return
        domain = mo.group(1)
        port = mo.group(3)
        namespace = mo.group(4)
        name = mo.group(5)
        prefix = 'http' if self.base.startswith('http/') else 'https'
        if port:
            domain += ":%d" % int(port)
        domain = "%s://%s" % (prefix, domain)
        name = '%s/%s' % (namespace, name)
        self.gitlab_base_url = domain
        self.gitlab_name = name

    def _query_gitlab_api(self, path, get_data=None, post_data=None,
                          delete_data=None, put_data=None, ignore_errors=None):
        return self._query_gitlab(
            GITLAB_API_URL, path, get_data=get_data, post_data=post_data,
            delete_data=delete_data, put_data=put_data,
            ignore_errors=ignore_errors)

    @api.multi
    def _query_gitlab(self, base, path, get_data=None, post_data=None,
                      delete_data=None, put_data=None, ignore_errors=None):
        self.ensure_one()
        headers = {'PRIVATE-TOKEN': self.token}
        func = requests.get
        if post_data:
            func = requests.post
        elif delete_data:
            func = requests.delete
        elif put_data:
            func = requests.put
        response = func(
            base % (self.gitlab_base_url, path),
            params=get_data or {},
            data=post_data or delete_data or put_data or {},
            headers=headers)
        if response.status_code < 400:
            return json.loads(response.text)
        if not ignore_errors or response.status_code not in ignore_errors:
            logger.error(
                'Query %s resulted in code %s: %s',
                base % (self.gitlab_base_url, path),
                response.status_code, response.text)
        return None

    @api.one
    @gitlab_api
    def update(self):
        projects = self._query_gitlab_api('projects', get_data={
            'search': self.gitlab_name.split('/')[-1],
        })
        project = None
        for p in projects:
            if p['path_with_namespace'] == self.gitlab_name:
                project = p
                break
        if not project:
            raise exceptions.ValidationError(
                _('Project %s not found') % self.gitlab_name)

        branches = {}
        if not self.mr_only:
            for branch in self._query_gitlab_api(
                    'projects/%s/repository/branches' % project['id']):
                branches[branch['commit']['id']] = branch
        for merge_request in self._query_gitlab_api(
                'projects/%s/merge_requests' % project['id'],
                get_data={'state': 'opened'}):
            # strangely enough, we can't query the commits with
            # projects/%s/merge_request/%s/commits, so we fetch the
            # source branch and get its last commit
            branch = self._query_gitlab_api(
                'projects/%s/repository/branches/%s' % (
                    merge_request['source_project_id'],
                    merge_request['source_branch']))
            if not branch:
                continue
            branch['merge_request'] = merge_request
            branches[branch['commit']['id']] = branch

        builds_created = self.env['runbot.build'].browse([])

        # create or adapt builds
        for sha, branch in branches.iteritems():
            commit = branch['commit']
            date = dateutil.parser.parse(commit['committed_date'])
            try:
                author = commit['author']['name']
            except KeyError:
                author = commit.get('author_name')
            try:
                committer = commit['committer']['name']
            except KeyError:
                committer = commit.get('committer_name')

            branch_name = 'refs/heads/%s' % branch['name']

            # Create or get branch
            branch_ids = self.env['runbot.branch'].search([
                ('repo_id', '=', self.id),
                ('name', '=', branch_name),
            ])
            if not branch_ids:
                logger.debug('repo %s found new merge request or build %s',
                             self.name, sha)
                branch_ids = self.env['runbot.branch'].create({
                    'repo_id': self.id,
                    'name': branch_name,
                    'project_id': project['id'],
                    'merge_request_id':
                    branch.get('merge_request', {}).get('iid'),
                })
            else:
                # there's a chance this was a non-mr-branch before
                branch_ids.filtered(lambda x: not x.merge_request_id)\
                    .write({
                        'merge_request_id':
                        branch.get('merge_request', {}).get('iid'),
                    })
                # in this case, this branch's builds were skipped, undo that
                if self.mr_only:
                    self.env['runbot.build'].search([
                        ('branch_id', 'in', branch_ids.ids),
                        ('result', '=', 'skipped'),
                        ('state', '=', 'done'),
                    ], limit=1).force()
            # Create build if not found
            build_ids = self.env['runbot.build'].search([
                ('branch_id', 'in', branch_ids.ids),
                ('name', '=', sha),
            ])
            if not build_ids:
                logger.debug(
                    'repo %s merge request %s new build found commit %s',
                    branch_ids.repo_id.name,
                    branch_ids.name,
                    sha,
                )
                builds_created += self.env['runbot.build'].create({
                    'branch_id': branch_ids.id,
                    'name': sha,
                    'author': author,
                    'committer': committer,
                    'subject': commit['message'],
                    'date': fields.Date.to_string(date),
                    'modules': ', '.join(filter(
                        None, branch_ids.mapped('repo_id.modules'))),
                })

        self._update_gitlab_before_super(project, builds_created)

        super(RunbotRepo, self).update()

        self._update_gitlab_after_super(project, builds_created)

    @api.multi
    def _update_gitlab_after_super(self, project, builds_created):
        self.ensure_one()
        # skip builds if we created a new one
        self.env['runbot.build'].search([
            ('id', 'not in', builds_created.ids),
            ('branch_id', 'in', builds_created.mapped('branch_id').ids),
            ('state', '=', 'pending'),
        ]).skip()
        # super creates branches without a project_id, fix that
        self.env['runbot.branch'].search([
            ('repo_id', 'in', self.ids),
            ('project_id', '=', False),
        ]).write({'project_id': project['id']})

        if self.sticky_protected:
            # Put all protected branches as sticky
            all_branches = self._query_gitlab_api(
                'projects/%s/repository/branches' % project['id'])
            protected_branches = map(
                lambda x: 'refs/heads/%s' % x['name'],
                filter(operator.itemgetter('protected'), all_branches))

            self.env['runbot.branch'].search([
                ('repo_id', 'in', self.ids),
                ('name', 'in', protected_branches),
                ('sticky', '=', False),
            ]).write({'sticky': True})

        if self.mr_only:
            # Skip non-sticky non-merge proposal builds
            branches = self.env['runbot.branch'].search([
                ('sticky', '=', False),
                ('repo_id', 'in', self.ids),
                ('merge_request_id', '=', False),
            ])
            self.env['runbot.build'].search([
                ('branch_id', 'in', branches.ids)]).skip()

    @api.multi
    def _update_gitlab_before_super(self, project, builds_created):
        self.ensure_one()
        # Clean-up old MRs
        merge_requests = self._query_gitlab_api(
            'projects/%s/merge_requests' % project['id'],
            get_data={'state': 'closed'})
        self.env['runbot.branch'].search([
            ('merge_request_id', 'in', map(
                operator.itemgetter('iid'), merge_requests)),
        ]).unlink()

        if self.active_branches:
            # Clean old branches
            all_branches = self._query_gitlab_api(
                'projects/%s/repository/branches' % project['id'])
            remote_branches = map(
                lambda x: 'refs/heads/%s' % x['name'], all_branches)

            self.env['runbot.branch'].search([
                ('repo_id', '=', self.id),
                ('name', 'not in', remote_branches),
            ]).unlink()
