# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class RunbotRepoDep(models.Model):
    _name = 'runbot.repo.dep'

    repo_src_id = fields.Many2one('runbot.repo', string='Repository',
                                  required=True, ondelete='cascade')
    repo_dst_id = fields.Many2one('runbot.repo', string='Repository',
                                  required=True, ondelete='cascade')
    reference = fields.Char('Reference', required=True,
                            default="refs/heads/master")


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    hosting = fields.Selection([], string='Hosting', required=True)
    username = fields.Char('Username')
    password = fields.Char('Password')
    dependency_nested_ids = fields.One2many('runbot.repo.dep', 'repo_src_id',
                                            string='Nested Dependency')
    base = fields.Char('Base URL', compute="_get_base", readonly=True)

    @api.multi
    def _get_base(self):
        for repo in self:
            name = re.sub(r'.+@', '', repo.name)
            name = re.sub(r'.git$', '', name)
            name = re.sub(r'https?:?\/\/', '', name)
            name = name.replace(':', '/')
            repo.base = name

    @api.onchange('name')
    def onchange_repository(self):
        if self.hosting or not self.name:
            return

        hosting_selection = self._columns['hosting'].selection
        hosting_list = [hosting[0] for hosting in hosting_selection]
        for hosting in hosting_list:
            if hosting in self.name:
                self.hosting = hosting
                return

    @api.multi
    def get_pull_request(self, pull_number):
        raise NotImplementedError("Should have implemented this")
