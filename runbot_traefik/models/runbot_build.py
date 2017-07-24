# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models


class RunbotBuild(models.Model):

    _inherit ='runbot.build'

    @api.multi
    def _get_traefik_domain(self):
        self.ensure_one()
        domain = self.env['runbot.repo']._domain()
        return '%s.%s' % (self.dest, domain)

    @api.multi
    def _get_domain(self, field_name, arg):
        results = super(RunbotBuild, self)._get_domain(field_name, arg)
        for build in self.filtered(lambda r: r.repo_id.is_traefik):
            results[build.id] = self._get_traefik_domain()

    @api.multi
    def _get_run_cmd(self):
        cmd = super(RunbotBuild, self)._get_run_cmd()
        cmd += [
            '-l', 'traefik.domain=%s' % self.env['runbot.repo']._domain(),
            '-l', 'traefik.alias.fqdn=%s' % self._get_traefik_domain(),
            '-l', 'traefik.enable=true',
            '-l', 'traefik.frontend.passHostHeader=true',
            '-l', 'traefik.port=8069',
        ]
        return cmd
