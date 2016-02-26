# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    is_travis2docker_build = fields.Boolean('Travis to docker build')
    use_docker_cache = fields.Boolean()
    docker_registry_server = fields.Char(
        help="Docker registry server to centralize all docker push cache "
        "images and docker pull cache images. E.g. localhost:5000. "
        "If is empty won't push it. "
        "Don't Use this feature if you use just one runbot server.")
