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
from openerp import api, models, fields

from .runbot_repo import escape_branch_name


class runbot_build(models.Model):
    _inherit = "runbot.build"

    @api.depends('repo_id.uses_gitlab', 'branch_id', 'name')
    def _compute_dest(self):
        for build in self.filtered('repo_id.uses_gitlab'):
            nickname = escape_branch_name(build.branch_id.name)[:32].lower()
            build.dest = "%05d-%s-%s" % (
                build.id, nickname, build.name[:6]
            )
        others = self - self.filtered('repo_id.uses_gitlab')
        others_by_id = {o.id: o for o in others}
        for rec_id, dest in others._get_dest('dest', None).iteritems():
            others_by_id[rec_id].dest = dest

    dest = fields.Char('Dest', compute='_compute_dest')
    gitlab_build_id = fields.Integer(string='Gitlab build id', size=20)
    gitlab_runner_token = fields.Char()

    @api.multi
    def _prepare_gitlab_status_post(self, state):
        self.ensure_one()
        return {
            'state': state,
            'ref': self.branch_id.branch_name,
            'name': 'runbot',
            'target_url': '//%s/runbot/build/%s' % (
                self.repo_id.domain(),
                self.id,
            ),
        }

    @api.multi
    def github_status(self):
        gitlab_builds = self.filtered('repo_id.uses_gitlab')
        for this in gitlab_builds:
            state = 'pending'
            if this.state in ['testing']:
                state = 'running'
            if this.result in ['ok', 'warn']:
                state = 'success'
            if this.result in ['ko']:
                state = 'failed'
            if this.result in ['skipped', 'killed']:
                state = 'canceled'
            this.repo_id._query_gitlab_api(
                'projects/%s/statuses/%s' % (
                    this.branch_id.project_id,
                    this.name,
                ),
                post_data=this._prepare_gitlab_status_post(state)
                )
        return super(
            runbot_build, self - gitlab_builds).github_status()

    @api.multi
    def _log(self, func, message):
        result = super(runbot_build, self)._log(func, message)
        for this in self.filtered('gitlab_build_id'):
            this.repo_id._query_gitlab_ci(
                'builds/%s' % this.gitlab_build_id,
                put_data={
                    'token': this.gitlab_runner_token,
                    # consider adding the full all log here
                    'trace': '\n'.join(
                        self.env['ir.logging'].search([
                            ('build_id', 'in', this.ids),
                        ]).mapped(lambda l: '%s %s' % (l.func, l.message))),
                })
        return result
