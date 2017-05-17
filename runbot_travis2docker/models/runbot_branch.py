# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from datetime import datetime

import requests

from openerp import fields, models, api


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    uses_weblate = fields.Boolean(help='Synchronize with Weblate')
    updated_weblate = fields.Datetime(help='Last update of weblate')
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

    @api.model
    def cron_weblate(self):
        for branch in self.search([('uses_weblate', '=', True)]):
            if (not branch.repo_id.weblate_token or
                    not branch.repo_id.weblate_url):
                continue
            current_date = (datetime.strptime(branch.updated_weblate,
                                              '%Y-%m-%d %H:%M:%S')
                            if branch.updated_weblate
                            else None)
            new_date = None
            url = branch.repo_id.weblate_url
            session = requests.Session()
            session.headers.update({
                'Accept': 'application/json',
                'User-Agent': 'runbot_travis2docker',
                'Authorization': 'Token %s' % branch.repo_id.weblate_token
            })
            projects = []
            page = 1
            while True:
                data = session.get('%s/projects/?page=%s' % (url, page)).json()
                projects.extend(data['results'] or [])
                if not data['next']:
                    break
                page += 1
            for project in projects:
                components = session.get('%s/projects/%s/components'
                                         % (url, project['slug'])).json()
                updated_branch = None
                for component in components['results']:
                    if (updated_branch and
                            updated_branch == component['branch']):
                        continue
                    if component['branch'] != branch['branch_name']:
                        continue
                    if project['name'] != branch.name_weblate:
                        continue
                    changes = session.get('%s/components/%s/%s/changes/'
                                          % (url, project['slug'],
                                             component['slug'])).json()
                    if not changes['results']:
                        continue
                    change = None
                    for record in changes['results']:
                        if record['action'] == 17:
                            change = record
                            break
                    if not change:
                        continue
                    date = datetime.strptime(
                        change['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    new_date = (date
                                if (not new_date or date > new_date)
                                else new_date)
                    if ((current_date and new_date and
                            current_date < new_date.replace(microsecond=0)) or
                            (not current_date and new_date)):
                        branch.write({'updated_weblate':
                                      new_date.strftime('%Y-%m-%d %H:%M:%S')})
                        self.env['runbot.build'].create({
                            'branch_id': branch.id,
                            'name': component['branch'],
                            'uses_weblate': True})
                        updated_branch = component['branch']

