# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import os
import shutil
import subprocess
import tempfile
from odoo.tests.common import SingleTransactionCase
from odoo.modules.module import get_resource_path


class TestRunbotBuildout(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        """Create a demo git repo in the file system and add it to runbot"""
        super().setUpClass()

        git_dir = tempfile.mkdtemp()

        def _git(*args):
            return subprocess.check_output(
                ('git', '-C', git_dir) + args, stderr=subprocess.STDOUT,
            )

        shutil.copy(
            get_resource_path('runbot_buildout', 'examples', 'buildout.cfg'),
            git_dir,
        )
        with open(
                os.path.join(git_dir, 'buildout.cfg'), 'a'
        ) as buildout_cfg:
            buildout_cfg.write(
                '\naddons = git %s parts/test 9.0\n' % git_dir,
            )

        _git('init')
        _git('checkout', '-b', 'buildout-9.0-testing')
        _git('add', '.')
        _git('commit', '-m', 'initial commit')

        cls.repo = cls.env['runbot.repo'].create({
            'name': git_dir,
            'uses_buildout': True,
        })

        cls.repo._update(cls.repo)
        cls.repo._scheduler(cls.repo.ids)

        _git('checkout', '--orphan', '9.0')
        _git('commit', '-m', 'initial commit')

    def test_00_buildout(self):
        """run a complete buildout"""
        branches = self.env['runbot.branch'].search([
            ('repo_id', '=', self.repo.id)
        ])
        self.assertTrue(branches)

        builds = self.env['runbot.build'].search([
            ('repo_id', '=', self.repo.id)
        ])
        self.assertTrue(builds)

        buildout_build = builds.filtered('branch_id.buildout_version')
        self.assertTrue(buildout_build)

        self.assertEqual(buildout_build.job, 'job_10_test_base')
        buildout_build._schedule()
        os.waitpid(buildout_build.pid, 0)
        buildout_build._schedule()
        self.assertEqual(buildout_build.job, 'job_20_test_all')
        os.waitpid(buildout_build.pid, 0)
        buildout_build._schedule()
        if buildout_build.state == 'running':
            os.waitpid(buildout_build.pid, 0)
            buildout_build._schedule()
        self.assertEqual(buildout_build.state, 'done')
        self.assertEqual(buildout_build.result, 'ok')
        buildout_build._local_cleanup()
        self.assertTrue(buildout_build.exists())

    def test_01_code(self):
        """run a build using the buildout built above"""
        self.repo._update(self.repo)
        builds = self.env['runbot.build'].search([
            ('repo_id', '=', self.repo.id)
        ])
        code_build = builds.filtered(
            lambda x: not x.branch_id.buildout_version
        )
        self.assertTrue(code_build)

        code_build._schedule()
        self.assertEqual(code_build.job, 'job_00_init')
        code_build._schedule()
        os.waitpid(code_build.pid, 0)
        self.assertEqual(code_build.job, 'job_01_run_buildout')
        code_build._schedule()
        os.waitpid(code_build.pid, 0)
        self.assertIn('parts/', code_build._server())
        self.assertTrue(os.path.exists(code_build._server()))
        cmd, modules = code_build._cmd()
        self.assertTrue(any('start_odoo' in c for c in cmd))
        self.assertFalse(modules)

    @classmethod
    def tearDownClass(cls):
        cls.env['runbot.build'].search([
            ('repo_id', '=', cls.repo.id),
        ])._kill()
        cls.repo.unlink()
        super().tearDownClass()
