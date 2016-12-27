# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re

from openerp import api, fields, models

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
