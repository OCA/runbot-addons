# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Sylvain VanHoof, Samuel Lefever
#    Odoo, Open Source Management Solution
#    Copyright (C) 2010-2015 Eezee-It (<http://www.eezee-it.com>).
#    Copyright 2015 Niboo (<http://www.niboo.be>).
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
import re
import logging
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
