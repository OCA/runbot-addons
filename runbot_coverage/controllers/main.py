# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.addons.runbot import runbot


class RunbotController(runbot.RunbotController):
    def build_info(self, build):
        result = super(RunbotController, self).build_info(build)
        if build.repo_id.use_coverage:
            result['coverage'] = build.coverage
        return result
