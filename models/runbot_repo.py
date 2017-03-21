# -*- coding: utf-8 -*-
# Copyright <2017> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
import re
import urllib

import requests

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


def _get_url(url, base):
    match_object = re.search('([^/]+)/([^/]+)/([^/.]+(.git)?)', base)
    if match_object:
        """When get is URL_GITHUB/api/v3/User/keys must be convert to
        URL_GITLAB/User.keys Because the api of gitlab required admin token
        for get the ssh keys
        https://docs.gitlab.com/ee/api/users.html#list-ssh-keys"""
        prefix = ('https://%s/api/v3%s'
                  if not url.endswith('/keys') else 'https://%s%s')
        project_name = (match_object.group(2) + '/' + match_object.group(3))
        url = url.replace(':owner', match_object.group(2))
        url = url.replace(':repo', match_object.group(3))
        url = prefix % (match_object.group(1), url)
        url = url.replace('/repos/', '/projects/')
        url = url.replace('/commits/', '/repository/commits/')
        url = url.replace(project_name, urllib.quote(project_name, safe=''))
        if url.endswith('/keys'):
            url = url.replace('users/', '').replace('/keys', '')
            url = url + '.keys'
        if '/pulls/' in url:
            urls = url.split('/pulls/')
            url = urls[0] + '/merge_requests?iid=' + urls[1]
    return url


def _get_session(token):
    session = requests.Session()
    session.auth = (token, 'x-oauth-basic')
    session.headers.update({'PRIVATE-TOKEN': token})
    return session


def custom_repo(func):
    """Decorator for functions which should be overwritten only if
    uses_gitlab is enabled in repo.
    """
    def custom_func(self, cr, uid, ids, *args, **kwargs):
        custom_ids = []
        regular_ids = []
        ret = None
        repos = self.browse(cr, uid, ids)
        for repo in repos:
            if repo.uses_gitlab:
                custom_ids.append(repo.id)
            else:
                regular_ids.append(repo.id)
            if custom_ids:
                ret = func(self, cr, uid, custom_ids, *args, **kwargs)
            if regular_ids:
                regular_func = getattr(super(RunbotRepo, self), func.func_name)
                ret = regular_func(cr, uid, regular_ids, *args, **kwargs)
        return ret
    return custom_func


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    uses_gitlab = fields.Boolean(help='Enable the ability to use gitlab '
                                      'instead of github')

    def git(self, cr, uid, ids, cmd, context=None):
        """Rewriting the parent method to avoid deleting the merge_request the
        gitlab"""
        if cmd == ['fetch', '-p', 'origin', '+refs/pull/*/head:refs/pull/*']:
            cmd.remove('-p')
        return super(RunbotRepo, self).git(cr, uid, ids, cmd, context=context)

    def update_git(self, cr, uid, repo, context=None):
        """Download the gitlab merge request references to work with the
        referrals of pull github"""
        if os.path.isdir(os.path.join(repo.path, 'refs')) and repo.uses_gitlab:
            repo.git(['fetch', '-p', 'origin',
                      '+refs/merge-requests/*/head:refs/pull/*'])
        return super(RunbotRepo, self).update_git(cr, uid, repo,
                                                  context=context)

    @custom_repo
    def github(self, cr, uid, ids, url, payload=None, ignore_errors=False,
               context=None):
        """This method is the same as the one in the odoo-extra/runbot.py
        file but with the translation of each request github to gitlab format
        - Get information from merge requests
            input: URL_GITLAB/projects/... instead of URL_GITHUB/repos/...
            output: res['base']['ref'] = res['gitlab_base_mr']
                    res['head']['ref'] = res['gitlab_head_mr']
        - Get user public keys
            input: URL_GITLAB/User.keys... instead of
                   URL_GITHUB/users/User/keys...
            output: res['author'] = {'login': data['username']}
                    res['commiter'] = {'login': data['username']}
        - Report statutes
            input: URL_GITLABL/... instead of URL_GITHUB/statuses/...
            output: N/A
        """
        for repo in self.browse(cr, uid, ids, context=context):
            if not repo.token:
                continue
            try:
                url = _get_url(url, repo.base)
                if not url:
                    return
                is_url_keys = url.endswith('.keys')
                session = _get_session(repo.token)
                if payload:
                    response = session.post(url, data=payload)
                else:
                    response = session.get(url)
                response.raise_for_status()
                json = (response.json() if not is_url_keys
                        else response._content)
                if 'merge_requests?iid=' in url:
                    json = json[0]
                    json['head'] = {'ref': json['target_branch']}
                    json['base'] = {'ref': json['source_branch']}
                if '/commits/' in url:
                    for own_key in ['author', 'committer']:
                        key_email = '%s_email' % own_key
                        if json[key_email]:
                            url = _get_url('/users?search=%s' %
                                           json[key_email],
                                           repo.base)
                            response = session.get(url)
                            response.raise_for_status()
                            data = response.json()
                            json[own_key] = {
                                'login':
                                len(data) and data[0]['username'] or {}
                            }
                if is_url_keys:
                    json = [{'key': ssh_rsa} for ssh_rsa
                             in json.split('\n')]
                return json
            except Exception:
                if ignore_errors:
                    _logger.exception('Ignored gitlab error %s %r', url,
                                      payload)
                else:
                    raise


class RunbotBuild(models.Model):
    _inherit = "runbot.build"

    def github_status(self, cr, uid, ids, context=None):
        runbot_domain = self.pool['runbot.repo'].domain(cr, uid)
        for build in self.browse(cr, uid, ids, context=context):
            is_merge_request = build.branch_id.branch_name.isdigit()
            source_project_id = False
            _url = _get_url('/projects/:owner/:repo/statuses/%s' % build.name,
                            build.repo_id.base)
            if not build.repo_id.uses_gitlab:
                super(RunbotBuild, self).github_status(cr, uid, ids,
                                                       context=context)
                continue
            if not build.repo_id.token:
                continue
            session = _get_session(build.repo_id.token)
            try:
                if is_merge_request:
                    url = _get_url('/projects/:owner/:repo/merge_requests/'
                                   '?iid=%s' % build.branch_id.branch_name,
                                   build.repo_id.base)
                    response = session.get(url)
                    response.raise_for_status()
                    json = response.json()[0]
                    source_project_id = json['source_project_id']
                    if source_project_id:
                        url = _get_url('/projects/%s' % source_project_id,
                                       build.repo_id.base)
                        response = session.get(url)
                        response.raise_for_status()
                        json = response.json()
                        base_url = (json['web_url'].replace('http://', '').
                                    replace('https://', ''))
                        _url = _get_url('/projects/:owner/:repo/statuses/%s' %
                                        build.name, base_url)
                desc = "runbot build %s" % (build.dest,)
                if build.state == 'testing':
                    state = 'running'
                elif build.state in ('running', 'done'):
                    state = 'failed'
                    if build.result == 'ok':
                        state = 'success'
                    if build.result == 'ko':
                        state = 'failed'
                    if build.result == 'skipped':
                        state = 'canceled'
                    if build.result == 'killed':
                        state = 'canceled'
                    desc += " (runtime %ss)" % (build.job_time,)
                else:
                    continue
                status = {
                    "state": state,
                    "target_url": "http://%s/runbot/build/%s" % (runbot_domain,
                                                                 build.id),
                    "description": desc,
                    "context": "ci/runbot"
                }
                _logger.debug("gitlab updating status %s to %s", build.name,
                              state)
                response = session.post(_url, status)
                response.raise_for_status()
            except Exception:
                _logger.exception('gitlab API error %s', url)


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    branch_url = fields.Char(compute='_get_branch_url')

    @api.multi
    def _get_branch_url(self):
        _branch_urls = super(RunbotBranch, self)._get_branch_url(None, None)
        for branch in self:
            if not branch.repo_id.uses_gitlab:
                branch.branch_url = _branch_urls[branch.id]
            else:
                if branch.branch_name.isdigit():
                    branch.branch_url = "https://%s/merge_requests/%s" % (
                        branch.repo_id.base, branch.branch_name)
                else:
                    branch.branch_url = ("https://%s/tree/%s" % (
                        branch.repo_id.base, branch.branch_name))
