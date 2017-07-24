# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class RunbotRepo(models.Model):

    _inherit ='runbot.repo'

    is_traefik = fields.Boolean()

    @api.multi
    @api.constrains('is_traefik', 'nginx', 'is_travis2docker_build')
    def check_is_traefik(self):
        for record in self:
            if record.nginx:
                raise ValidationError(_(
                    'Traefik builds cannot also be Nginx builds.',
                ))
            if not record.is_travis2docker_build:
                raise ValidationError(_(
                    'Traefik builds must also be Travis2Docker builds.',
                ))

    @api.multi
    @api.onchange('is_traefik')
    def onchange_is_traefik(self):
        self.is_travis2docker_build = True
        self.nginx = False
