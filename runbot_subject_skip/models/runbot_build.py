# Copyright <2018> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import api, models

SKIP_WORDS = ['[ci skip]', '[skip ci]']
SKIP_WORDS_RE = re.compile("|".join(map(re.escape, SKIP_WORDS)))


class RunbotBuild(models.Model):
    _inherit = "runbot.build"

    def subject_skip(self):
        """Skip build if there is a commit message with one SKIP_WORDS"""
        for build in self.filtered(lambda b:
                                   SKIP_WORDS_RE.search(b.subject.lower())):
            build._log('subject_skip', 'The commit message skipped this build')
            build._skip()

    @api.model
    def create(self, values):
        build = super().create(values)
        build.subject_skip()
        return build
