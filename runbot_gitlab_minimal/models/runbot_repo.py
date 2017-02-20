# -*- coding: utf-8 -*-
# Copyright <2017> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
import re
import urllib

import requests

from openerp import models, fields

_logger = logging.getLogger(__name__)


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
        - Report statutes
            input: URL_GITLABL/... instead of URL_GITHUB/statuses/...
            output: N/A
        """
        for repo in self.browse(cr, uid, ids, context=context):
            is_url_merge = False
            if not repo.token:
                continue
            try:
                match_object = re.search('([^/]+)/([^/]+)/([^/.]+(.git)?)',
                                         repo.base)
                if match_object:
                    project_name = (match_object.group(2) + '/' +
                                    match_object.group(3))
                    url = url.replace(':owner', match_object.group(2))
                    url = url.replace(':repo', match_object.group(3))
                    url = 'https://%s/api/v3%s' % (match_object.group(1),
                                                   url)
                    url = url.replace('/repos/', '/projects/')
                    url = url.replace(project_name,
                                      urllib.quote(project_name, safe=''))
                    if '/pulls/' in url:
                        urls = url.split('/pulls/')
                        url = urls[0] + '/merge_requests?iid=' + urls[1]
                        is_url_merge = True
                    session = requests.Session()
                    session.auth = (repo.token, 'x-oauth-basic')
                    session.headers.update({'PRIVATE-TOKEN': repo.token})
                    if payload:
                        if payload['state'] == 'pending':
                            payload['state'] = 'running'
                        if payload['state'] in ('error', 'failure'):
                            payload['state'] = 'failed'
                        response = session.post(url, data=payload)
                    else:
                        response = session.get(url)
                    response.raise_for_status()
                    json = response.json()
                    if is_url_merge:
                        json = json[0]
                        json['head'] = {'ref': json['target_branch']}
                        json['base'] = {'ref': json['source_branch']}
                    return json
            except Exception:
                if ignore_errors:
                    _logger.exception('Ignored gitlab error %s %r', url,
                                      payload)
                else:
                    raise
