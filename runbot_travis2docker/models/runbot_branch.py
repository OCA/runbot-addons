# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import os

import requests
import subprocess

from odoo import fields, models, api, tools


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    uses_weblate = fields.Boolean(help='Synchronize with Weblate')
    name_weblate = fields.Char(compute='_compute_name_weblate', store=True)

    @api.multi
    @api.depends('repo_id.name', 'branch_name', 'uses_weblate')
    def _compute_name_weblate(self):
        for branch in self:
            name = branch.repo_id.name.replace(':', '/')
            name = re.sub('.+@', '', name)
            name = re.sub('.git$', '', name)
            name = re.sub('^https://', '', name)
            name = re.sub('^http://', '', name)
            match = re.search(
                r'(?P<host>[^/]+)/(?P<owner>[^/]+)/(?P<repo>[^/]+)', name)
        if match:
            name = ("%(host)s:%(owner)s/%(repo)s (%(branch)s)" %
                    dict(match.groupdict(), branch=branch['branch_name']))
        branch.name_weblate = name

    @tools.ormcache('ssh')
    def _ssh_keyscan(self, ssh):
        """This function execute the command 'ssh-keysan' to avoid the question
        when the command git fetch is excecuted.
        The question is like to:
            'Are you sure you want to continue connecting (yes/no)?'"""
        cmd = ['ssh-keyscan', '-p']
        match = re.search(
            r'(ssh\:\/\/\w+@(?P<host>[a-zA-Z0-9_.-]+))(:{0,1})'
            r'(?P<port>(\d+))?', ssh)
        if not match:
            return False
        data = match.groupdict()
        cmd.append(data['port'] or '22')
        cmd.append(data['host'])
        with open(os.path.expanduser('~/.ssh/known_hosts'), 'a+') as hosts:
            new_keys = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            for key in new_keys.stdout:
                if [line for line in hosts if (line.strip('\n') ==
                                               key.strip('\n'))]:
                    continue
                hosts.write(key + '\n')
        return True

    @tools.ormcache('url', 'token')
    def get_weblate_projects(self, url, token):
        """Find all projects and components that are on weblate url.
        The cache is handled by @tools.ormcache annotation if the url and token
        were already searched"""
        projects = []
        items = []
        page = 1
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'runbot_travis2docker',
            'Authorization': 'Token %s' % token
        })
        while True:
            response = session.get('%s/projects/?page=%s' % (url, page))
            response.raise_for_status()
            data = response.json()
            items.extend(data['results'])
            if not data['next']:
                break
            page += 1
        for project in items:
            components = []
            page = 1
            while True:
                response = session.get('%s/projects/%s/components/?page=%s'
                                       % (url, project['slug'], page))
                response.raise_for_status()
                data = response.json()
                components.extend(data['results'] or [])
                if not data['next']:
                    break
                page += 1
            project['components'] = components
            response = session.get('%s/projects/%s/repository'
                                   % (url, project['slug']))
            response.raise_for_status()
            data = response.json()
            if data['needs_commit']:
                response = session.post('%s/projects/%s/repository'
                                        % (url, project['slug']),
                                        {'operation': 'commit'})
                response.raise_for_status()
            projects.append(project)
        return projects

    @api.model
    def cron_weblate(self):
        for branch in self.search([('uses_weblate', '=', True)]):
            if (not branch.repo_id.weblate_token or
                    not branch.repo_id.weblate_url or
                    not branch.repo_id.weblate_ssh):
                continue
            cmd = ['git', '--git-dir=%s' % branch.repo_id.path]
            projects = self.get_weblate_projects(branch.repo_id.weblate_url,
                                                 branch.repo_id.weblate_token)
            for project in projects:
                updated_branch = None
                for component in project['components']:
                    if ((updated_branch and
                            updated_branch == component['branch']) or
                            (component['branch'] != branch['branch_name']) or
                            (project['name'] != branch.name_weblate)):
                        continue
                    has_build = self.env['runbot.build'].search(
                        [('branch_id', '=', branch.id),
                         ('state', 'in', ('pending', 'running', 'testing')),
                         ('name', '=', component['branch']),
                         ('uses_weblate', '=', True)])
                    if has_build:
                        continue
                    component = [item for item in project['components']
                                 if item['git_export']]
                    if len(component) != 1:
                        continue
                    component = component[0]
                    remote = 'wl-%s-%s' % (project['slug'], component['slug'])
                    url_repo = '/'.join([
                        branch.repo_id.weblate_ssh, project['slug'],
                        component['slug']])
                    try:
                        subprocess.check_output(cmd + ['remote', 'add', remote,
                                                       url_repo])
                    except subprocess.CalledProcessError:
                        pass
                    self._ssh_keyscan(branch.repo_id.weblate_ssh)
                    subprocess.check_output(cmd + ['fetch', remote])
                    diff = subprocess.check_output(
                        cmd + ['diff',
                               '%(branch)s..%(remote)s/%(branch)s'
                               % {'branch': branch['branch_name'],
                                  'remote': remote}, '--stat'])
                    if not diff:
                        continue
                    branch.force_weblate()
                    updated_branch = component['branch']
        # The cache must be deleted to query the weblate API next time and get
        # the latest changes
        self.clear_caches()

    @api.multi
    def force_weblate(self):
        for record in self:
            self.env['runbot.build'].create({
                'branch_id': record.id,
                'name': record.branch_name,
                'uses_weblate': True})
