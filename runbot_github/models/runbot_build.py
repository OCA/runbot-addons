# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, models


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
            regular_func = getattr(super(RunbotBuild, self), func.func_name)
            return regular_func(*args, **kwargs)
    return github


class RunbotBuild(models.Model):
    _inherit = "runbot.build"

    @api.multi
    @github
    def github_status(self):
        return super(RunbotBuild, self).github_status()
