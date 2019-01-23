# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import SingleTransactionCase

from odoo.addons.runbot_buildout.models.runbot_branch import (
    PYTHON2, PYTHON3)


class TestRunbotBranch(SingleTransactionCase):

    def test_branch_functions(self):
        """Create 9.0 and 11.0 buildout branch, then check python version."""
        repo_model = self.env['runbot.repo']
        branch_model = self.env['runbot.branch']
        repo = repo_model.create({
            'name': '/tmp/doesnotmatter',
            'buildout_branch_pattern': 'buildout-(?P<version>\\d+\\.\\d+)',
            'buildout_section': 'odoo',
            'uses_buildout': True})
        branch_09 = branch_model.create({
            'name': 'refs/heads/buildout-9.0-testing',
            'repo_id': repo.id,
            'branch_name': 'buildout-9.0-testing'})
        self.assertEqual(branch_09.buildout_version, '9.0')
        self.assertEqual(branch_09.get_interpreter(), PYTHON2)
        branch_11 = branch_model.create({
            'name': 'refs/heads/buildout-11.0-testing',
            'repo_id': repo.id,
            'branch_name': 'buildout-11.0-testing'})
        self.assertEqual(branch_11.buildout_version, '11.0')
        self.assertEqual(branch_11.get_interpreter(), PYTHON3)
