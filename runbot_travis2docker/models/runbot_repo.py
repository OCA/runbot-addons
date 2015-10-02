# coding: utf-8
from openerp import fields, models


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    is_travis2docker_build = fields.Boolean('Travis to docker build')
