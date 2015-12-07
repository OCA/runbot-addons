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
from urllib import quote_plus
import urllib
import unicodedata

import requests
try:
    from gitlab3 import GitLab
except ImportError as exc:
    # don't fail at load if gitlab module is not available
    pass

from openerp import models, fields, api, exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

logger = logging.getLogger(__name__)

GITLAB_CI_SETTINGS_URL = '%s/api/v3/projects/%s/services/gitlab-ci'


branch_name_subs = [
    (' ', '-'),
    (',', '-'),
    ('.', '-'),
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


def get_gitlab_params(base):
    mo = re.search(r'([^/]+)(/(\d+))?/([^/]+)/([^/.]+)(\.git)?', base)
    if not mo:
        return
    domain = mo.group(1)
    port = mo.group(3)
    namespace = mo.group(4)
    name = mo.group(5)
    prefix = 'http' if base.startswith('http/') else 'https'
    if port:
        domain += ":%d" % int(port)
    domain = "%s://%s" % (prefix, domain)
    name = '%s/%s' % (namespace, name)
    return domain, name


def get_gitlab_project(base, token, project_id=None):
    """Retrieve gitlab project using either id or name

    :param str base: url base of project containing domain and project name
    :param str token: gitlab user's token
    :param int or None project_id: optional id of project to get
    :returns gitlab3.Project: Gitlab Project
    :raises exceptions.ValidationError: Repo couldn't be found by name or id
    """
    domain, name = get_gitlab_params(base)
    gl = GitLab(domain, token)
    if project_id:
        res = gl.project(project_id)
    else:
        res = gl.find_project(path_with_namespace=name)
    if not res:
        raise exceptions.ValidationError(
            _('Could not find repo with ') +
            (_("id=%d") % project_id if project_id else _("name=%s") % name)
        )
    return res


def set_gitlab_ci_conf(token, gitlab_url, runbot_domain, repo_id):
    if not token:
        raise models.except_orm(
            _('Error!'),
            _('Gitlab repo requires an API token from a user with '
              'admin access to repo.')
        )
    domain, name = get_gitlab_params(gitlab_url.replace(':', '/'))
    url = GITLAB_CI_SETTINGS_URL % (domain, quote_plus(name))
    project_url = "http://%s/gitlab-ci/%s" % (runbot_domain, repo_id)
    data = {
        "token": token,
        "project_url": project_url,
    }
    headers = {
        "PRIVATE-TOKEN": token,
    }
    requests.put(url, data=data, headers=headers)


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

    @api.model
    def create(self, vals):
        repo_id = super(RunbotRepo, self).create(vals)
        if self.uses_gitlab:
            set_gitlab_ci_conf(
                vals.get('token'),
                vals.get('name'),
                self.domain(),
                repo_id.id,
            )
        return repo_id

    @api.multi
    def write(self, vals):
        super(RunbotRepo, self).write(vals)
        if self.uses_gitlab:
            set_gitlab_ci_conf(
                vals.get('token', self.token),
                vals.get('name', self.name),
                self.domain(),
                self.id,
            )

    @api.one
    @gitlab_api
    def github(self, url, payload=None, ignore_errors=False, delete=False):
        if payload:
            logger.info(
                "Wanted to post payload %s at %s" % (url, payload)
            )
            r = {}
        elif delete:
            logger.info("Wanted to delete %s" % url)
            r = {}
        else:
            logger.info("Wanted to get %s" % url)
            r = {}
        return r

    @api.one
    @gitlab_api
    def update(self):

        branch_obj = self.env['runbot.branch']

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
            source_branch = source_project.branch(mr.source_branch)
            commit = source_branch.commit
            sha = commit['id']
            date = commit['committed_date']
            # TODO: TMP workaround for tzinfo bug
            # https://github.com/alexvh/python-gitlab3/issues/15
            date.tzinfo.dst = lambda _: None
            # In earlier versions of gitlab3, author and committer were a keys
            # newer versions have author_name and committer_name
            try:
                author = commit['author']['name']
            except KeyError:
                author = commit['author_name']
            try:
                committer = commit['committer']['name']
            except KeyError:
                committer = commit['committer_name']
            subject = commit['message']
            title = mr.title
            # Create or get branch
            branch_ids = branch_obj.search([
                ('repo_id', '=', self.id),
                ('project_id', '=', project.id),
                ('merge_request_id', '=', mr.iid),
            ])
            if branch_ids:
                branch_id = branch_ids[0]
            else:
                logger.debug('repo %s found new Merge Proposal %s',
                             self.name, title)
                branch_id = branch_obj.create({
                    'repo_id': self.id,
                    'name': title,
                    'project_id': project.id,
                    'merge_request_id': mr.iid,
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
        closed_mrs = branch_obj.search([
            ('merge_request_id', 'in', closed_mrs),
        ])

        for mr in closed_mrs:
            mr.unlink()

        if self.active_branches:
            # Clean old branches
            remote_branches = set(b.name for b in project.find_branch(
                find_all=True))

            old_branches = branch_obj.search([
                ('repo_id', '=', self.id),
                ('merge_request_id', '=', False),
                ('branch_name', 'not in', list(remote_branches)),
            ])
            old_branches.unlink()

        super(RunbotRepo, self).update()

        # Avoid TransactionRollbackError due to serialization issues
        self._cr.commit()
        self._cr.autocommit(True)

        if self.sticky_protected:
            # Put all protected branches as sticky
            protected_branches = set(b.name for b in project.find_branch(
                find_all=True, protected=True)
            )
            protected_branches.add(project.default_branch)

            sticky_protected_branches = branch_obj.search([
                ('branch_name', 'in', list(protected_branches)),
                ('sticky', '=', False),
            ])

            sticky_protected_branches.write({'sticky': True})

        if self.mr_only:
            # Skip non-sticky non-merge proposal builds
            branches = branch_obj.search([
                ('sticky', '=', False),
                ('repo_id', 'in', self.ids),
                ('project_id', '=', False),
                ('merge_request_id', '=', False),
            ])
            for build in self.env['runbot.build'].search([
                    ('branch_id', 'in', branches.ids)]):
                build.skip()
