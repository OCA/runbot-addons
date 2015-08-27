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
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    branch_url = fields.Char('Branch url', compute='_get_branch_url',
                             readonly=1)

    @api.multi
    def is_pull_request(self):
        self.ensure_one()
        return re.match(r'^\d+$', self.branch_name) is not None

    @api.multi
    def _get_branch_url(self):
        for branch in self:
            owner, repository = branch.repo_id.base.split('/')[1:]

            if branch.is_pull_request():
                branch.branch_url = branch.get_pull_request_url(
                    owner, repository, branch.branch_name)
            else:
                branch.branch_url = branch.get_branch_url(
                    owner, repository, branch.branch_name)

    @api.multi
    def _get_pull_info(self):
        raise NotImplementedError("Should have implemented this")

    @api.multi
    def get_pull_request_url(self, owner, repository, branch):
        raise NotImplementedError("Should have implemented this")

    @api.multi
    def get_branch_url(self, owner, repository, pull_number):
        raise NotImplementedError("Should have implemented this")
