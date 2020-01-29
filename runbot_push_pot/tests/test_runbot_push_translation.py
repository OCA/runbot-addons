# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import mock
import os
import shutil
import subprocess
import tempfile
import time
import odoo
from odoo.tests.common import TransactionCase


class TestRunbotPushTranslation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Create a demo git repo in the file system and add it to runbot"""
        super().setUpClass()

        cls.git_dir = tempfile.mkdtemp()

        def _git(*args):
            return subprocess.check_output(
                ('git', '-C', cls.git_dir) + args, stderr=subprocess.STDOUT,
            )

        cls._git = lambda *args: _git(*args[1:])

        module_dir = os.path.join(cls.git_dir, 'runbot_push_pot')
        os.mkdir(module_dir)
        with open(
                os.path.join(module_dir, '__manifest__.py'), 'a'
        ) as manifest:
            manifest.write('{}')
        with open(
                os.path.join(module_dir, '__init__.py'), 'a'
        ):
            pass

        _git('init')
        _git('checkout', '-b', '11.0')
        _git('add', '.')
        _git('commit', '-m', 'initial commit')

        # make the repo bare to allow pusing to it
        cls.git_dir = os.path.join(cls.git_dir, '.git')
        _git('config', 'core.bare', 'true')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.git_dir)
        super().tearDownClass()

    def test_runbot_push_translation(self):
        repo = self.env['runbot.repo'].create({
            'name': self.git_dir,
        })

        repo._update(repo)
        repo._scheduler()
        build = self.env['runbot.build'].search([('repo_id', '=', repo.id)])
        build._checkout()
        build.branch_id.write({'push_pot': True})

        # we just need to intercept the call where our code would call the
        # server to export our translations on the commandline
        def export_translations(command, **kwargs):
            with open(command[-4], 'wb') as translations:
                odoo.tools.trans_export(
                    None, command[-2:], translations, 'tgz',
                    self.env.cr,
                )

        # as the module didn't have a pot file before, this will add it
        with tempfile.TemporaryDirectory() as run_dir, mock.patch(
            'subprocess.check_call', side_effect=export_translations,
        ):
            pid = build._job_29_export_translations(
                build,
                os.path.join(run_dir, 'lock_file'),
                os.path.join(run_dir, 'log_file'),
            )
            os.waitpid(pid, 0)

        log = self._git('log').decode('utf8')
        self.assertIn('[UPD] updated translations from runbot', log)

        # pull changes to runbot's checkout
        repo._update(repo)
        # sleep a while to be sure enough time passed to generate a
        # different timestamp
        time.sleep(1)

        # subsequent calls shouldn't change anything
        with tempfile.TemporaryDirectory() as run_dir, mock.patch(
            'subprocess.check_call', side_effect=export_translations,
        ):
            pid = build._job_29_export_translations(
                build,
                os.path.join(run_dir, 'lock_file'),
                os.path.join(run_dir, 'log_file'),
            )
            os.waitpid(pid, 0)

        self.assertEqual(log, self._git('log').decode('utf8'))
