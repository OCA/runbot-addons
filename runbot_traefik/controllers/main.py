# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

_logger = logging.getLogger(__name__)

try:
    from openerp.addons.runbot.runbot import RunbotController
except ImportError:
    _logger.info('Cannot find the `runbot` module in addons path.')


class RunbotController(RunbotController):

    def build_info(self, build):
        build_info = super(RunbotController, self).build_info(build)
        if build.repo_id.is_traefik:
            build_info['host'] = '%s.%s' % (
                build_info['host'], build.repo_id._domain(),
            )
        return build_info
