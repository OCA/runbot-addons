# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models


class RunbotBuild(models.Model):

    _inherit = 'runbot.build'

    host = fields.Char(
        compute='_compute_host',
        inverse='_inverse_host',
    )
    _host = fields.Char()

    @api.multi
    @api.depends('_host')
    def _compute_host(self):
        for record in self:
            host = record._host or ''
            if record.repo_id.is_traefik:
                host = '%s.%s' % (
                    host, record.repo_id._domain(),
                )
            record.host = host

    @api.multi
    def _inverse_host(self):
        for record in self:
            host = record._host or ''
            if record.repo_id.is_traefik:
                host = host.split(record.repo_id._domain())
                host = host[0]
            record._host = host

    @api.multi
    def _get_traefik_domain(self):
        self.ensure_one()
        domain = self.repo_id._domain()
        return '%s.%s' % (self.dest, domain)

    @api.multi
    def _get_domain(self, field_name, arg):
        results = super(RunbotBuild, self)._get_domain(field_name, arg)
        for build in self.filtered(lambda r: r.repo_id.is_traefik):
            results[build.id] = self._get_traefik_domain()

    @api.multi
    def _get_run_cmd(self):
        cmd = super(RunbotBuild, self)._get_run_cmd()
        if self.repo_id.is_traefik:
            cmd += [
                '-l', 'traefik.domain=%s' % self.repo_id._domain(),
                '-l', 'traefik.alias.fqdn=%s' % self._get_traefik_domain(),
                '-l', 'traefik.enable=true',
                '-l', 'traefik.frontend.passHostHeader=true',
                '-l', 'traefik.port=8069',
            ]
        return cmd
