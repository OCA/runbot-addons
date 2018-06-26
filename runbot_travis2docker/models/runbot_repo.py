# Copyright <2015> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api

DEFAULT_TRAVIS2DOCKER_IMAGE = 'vauxoo/odoo-80-image-shippable-auto'


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    is_travis2docker_build = fields.Boolean('Travis to docker build')
    travis2docker_test_disable = fields.Boolean('Test Disable?')
    travis2docker_image = fields.Char(
        default=lambda s: s._default_travis2docker_image(),
    )

    @api.model
    def _default_travis2docker_image(self):
        return DEFAULT_TRAVIS2DOCKER_IMAGE
