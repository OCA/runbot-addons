# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import glob
import logging
import os
import shutil

from openerp import api, models
from openerp.addons.runbot import runbot

_logger = logging.getLogger(__name__)


class RunbotBuild(models.Model):
    _inherit = "runbot.build"

    @api.multi
    def checkout(self):
        result = super(RunbotBuild, self).checkout()
        for build in self:
            for extra_repo in build.repo_id.dependency_nested_ids:
                extra_repo.repo_dst_id.git_export(
                    extra_repo.reference, build.path())

            modules_to_move = [
                os.path.dirname(module)
                for module in glob.glob(build.path('*/__openerp__.py'))
            ]

            for module in runbot.uniq_list(modules_to_move):
                basename = os.path.basename(module)
                if os.path.exists(build.server('addons', basename)):
                    build._log(
                        'Building environment',
                        'You have duplicate modules in your branches "%s"' %
                        basename
                    )
                    shutil.rmtree(build.server('addons', basename))
                shutil.move(module, build.server('addons'))

        return result

    @api.multi
    def github_status(self):
        """
        By default, we disable this feature.
        This method should be call only for github repo
        :return:
        """
        return
