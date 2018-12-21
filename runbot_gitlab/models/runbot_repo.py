# Copyright <2017> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re
import urllib.parse

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


def _get_url(url, base):
    """When get is URL_GITHUB/api/v4/User/keys must be convert to
    URL_GITLAB/User.keys Because the api of gitlab required admin token
    for get the ssh keys
    https://docs.gitlab.com/ee/api/users.html#list-ssh-keys"""
    match_object = re.search('([^/]+)/([^/]+)/([^/.]+(.git)?)', base)
    if match_object:
        prefix = ('https://%s/api/v4%s'
                  if not url.endswith('/keys') else 'https://%s%s')
        project_name = (match_object.group(2) + '/' + match_object.group(3))
        url = url.replace(':owner', match_object.group(2))
        url = url.replace(':repo', match_object.group(3))
        url = prefix % (match_object.group(1), url)
        url = url.replace('/repos/', '/projects/')
        url = url.replace('/commits/', '/repository/commits/')
        url = url.replace(project_name,
                          urllib.parse.quote(project_name, safe=''))
        if url.endswith('/keys'):
            url = url.replace('users/', '').replace('/keys', '')
            url = url + '.keys'
        if '/pulls/' in url:
            urls = url.split('/pulls/')
            url = urls[0] + '/merge_requests/' + urls[1]
    return url


def _get_session(token):
    session = requests.Session()
    session.auth = (token, 'x-oauth-basic')
    session.headers.update({'PRIVATE-TOKEN': token})
    return session


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    uses_gitlab = fields.Boolean(help='Enable the ability to use gitlab '
                                      'instead of github')
    warnings_are_errors = fields.Boolean(
        'Treat warnings as errors',
        default=True, help='When runbot reports warnings, report that as '
        'error to gitlab',
    )

    def _git(self, cmd):
        """Rewriting the parent method to get merge_request from gitlab"""
        repos_gitlab = self.filtered('uses_gitlab')
        for repo_gitlab in repos_gitlab:
            cmd_gitlab = cmd.copy()
            if ('fetch' in cmd_gitlab
                    and cmd_gitlab[-1] == '+refs/pull/*/head:refs/pull/*'):
                cmd_gitlab.pop()
                cmd_gitlab.append('+refs/merge-requests/*/head:refs/pull/*')
            return super(RunbotRepo, repos_gitlab)._git(cmd_gitlab)
        return super(RunbotRepo, self - repos_gitlab)._git(cmd)

    def _github(self, url, payload=None, ignore_errors=False):
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
                    res['committer'] = {'login': data['username']}
        - Report statutes
            input: URL_GITLABL/... instead of URL_GITHUB/statuses/...
            output: N/A
        """
        records_gitlab = self.filtered('uses_gitlab')
        for repo in records_gitlab.filtered('token'):
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
                        else response.text)
                if 'merge_requests/' in url:
                    json['head'] = {
                        'ref': json['source_branch'],
                        # github api returns a label like
                        # 'source-project-name:source-branch-name' the closest
                        # we got in gitlab api is
                        # 'source_project_id:source_branch'
                        # (without additional http/db requests)
                        'label': '%s:%s' % (
                            json['source_project_id'], json['source_branch']),
                    }
                    json['base'] = {'ref': json['target_branch']}
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
                                'login': data and data[0]['username'] or ''
                            }
                if is_url_keys:
                    json = [{'key': ssh_rsa} for ssh_rsa in json.split('\n')]
                return json
            except Exception:
                if ignore_errors:
                    _logger.exception('Ignored gitlab error %s %r', url,
                                      payload)
                else:
                    raise
        return super(RunbotRepo, self - records_gitlab)._github(
            url, payload=payload, ignore_errors=ignore_errors)
