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

from openerp import models, api, fields

from .github import GithubHosting

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def github(func):
    """Decorator for functions which should be overwritten only if
    this repo is bitbucket-.
    """
    def github(self, *args, **kwargs):
        if self.hosting == 'github':
            return func(self, *args, **kwargs)
        else:
            regular_func = getattr(super(RunbotRepo, self), func.func_name)
            return regular_func(*args, **kwargs)
    return github


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    hosting = fields.Selection(selection_add=[('github', 'GitHub')])

    @api.multi
    @github
    def get_pull_request(self, pull_number):
        self.ensure_one()
        match = re.search('([^/]+)/([^/]+)/([^/.]+(.git)?)', self.base)

        if match:
            owner = match.group(2)
            repository = match.group(3)

            hosting = GithubHosting((self.username, self.password))

            return hosting.get_pull_request(owner, repository, pull_number)
