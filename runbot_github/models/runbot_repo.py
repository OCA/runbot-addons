# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re

from openerp import api, fields, models

from .github import GithubHosting

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
