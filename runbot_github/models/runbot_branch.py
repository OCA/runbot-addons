# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, models
from .github import GithubHosting

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def github(func):
    """Decorator for functions which should be overwritten only if
    this repo is bitbucket-.
    """
    def github(self, *args, **kwargs):
        if self.repo_id.hosting == 'github':
            return func(self, *args, **kwargs)
        else:
            regular_func = getattr(super(RunbotBranch, self), func.func_name)
            return regular_func(*args, **kwargs)
    return github


class RunbotBranch(models.Model):
    _inherit = "runbot.branch"

    @api.multi
    @github
    def _get_pull_info(self):
        self.ensure_one()
        repo = self.repo_id
        if repo.token and self.name.startswith('refs/pull/'):
            pull_number = self.name[len('refs/pull/'):]
            return repo.get_pull_request(pull_number) or {}
        return {}

    @api.multi
    @github
    def get_pull_request_url(self, owner, repository, branch):
        self.ensure_one()

        return GithubHosting.get_pull_request_url(owner, repository, branch)

    @api.multi
    @github
    def get_branch_url(self, owner, repository, pull_number):
        self.ensure_one()

        return GithubHosting.get_branch_url(owner, repository, pull_number)
