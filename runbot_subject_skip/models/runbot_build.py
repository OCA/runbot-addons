# Copyright <2018> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

SKIP_WORDS = ['[ci skip]', '[skip ci]']


class RunbotBuild(models.Model):
    _inherit = "runbot.build"

    def subject_skip(self):
        """Skip build if there is a commit message with one SKIP_WORDS"""
        for build in self:
            subject = build.subject.lower()
            for word in SKIP_WORDS:
                if word in subject:
                    build._log('subject_skip',
                               'The commit message skip this build with '
                               'the word "%s"' % word)
                    build._skip()

    @api.model
    def create(self, values):
        build = super().create(values)
        build.subject_skip()
        return build
