# Copyright <2018> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestRunbotSkipBuild(TransactionCase):

    def test_skip_build(self):
        """Test the [ci skip] feature"""
        repo = self.env["runbot.repo"].create({
            "name": "https://github.com/ORG/REPO.git",
        })
        branch = self.env["runbot.branch"].create({
            "name": "refs/heads/master",
            "repo_id": repo.id,
        })
        build = self.env["runbot.build"].create({
            "name": "HEAD",
            "branch_id": branch.id,
            "subject": "Test [ci skip] feature",
        })
        self.assertEqual(
            build.state, 'done', "State should be done")
        self.assertEqual(
            build.result, 'skipped', "Result should be skipped")
        build = self.env["runbot.build"].create({
            "name": "HEAD",
            "branch_id": branch.id,
            "subject": "Test no ci skip feature",
        })
        self.assertEqual(
            build.state, 'pending', "State should be pending")
        self.assertNotEqual(
            build.result, 'skipped', "Result shouldn't be skipped")
