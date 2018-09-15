# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import os
import shutil
import signal
import time
import logging
from openerp.tests.common import TransactionCase
_logger = logging.getLogger(__file__)


def run_build(build):
    """run a build synchronously until it's finished"""
    counter = 0
    while build.state not in ['done', 'running']:
        counter += 1
        if counter % 5 == 0:
            _logger.info('Still busy running build %d', build)
        build._schedule()
        if build.pid:
            sig = (build.state == 'running') and signal.SIGKILL or 0
            try:
                os.kill(build.pid, sig)
            except OSError:
                break
            time.sleep(60)


class TestRunbotPreseedDatabase(TransactionCase):
    def test_runbot_preseed_database(self):
        repo = self.env['runbot.repo'].create({
            'name': 'https://github.com/oca/ocb',
            'modules_auto': 'none',
            'modules': 'base',
        })
        repo._update_git()

        branch = self.env['runbot.branch'].search([
            ('repo_id', '=', repo.id),
            ('name', '=', 'refs/heads/11.0'),
        ])
        build = self.env['runbot.build'].search([
            ('branch_id', '=', branch.id),
        ])
        run_build(build)
        cloned_build = build._force()

        # configure the repo to use this build as preseed build
        wizard = self.env['runbot.preseed.database.refresh'].with_context(
            active_model=repo._name,
            active_id=repo.id,
        ).new({
            'build_id': build.id,
        })
        wizard.onchange_build_id()
        self.assertTrue(wizard.preseed_database)
        wizard = self.env['runbot.preseed.database.refresh'].with_context(
            active_model=repo._name,
            active_id=repo.id,
        ).create({
            'build_id': build.id,
            'preseed_database': wizard.preseed_database,
        })
        wizard.action_get_modules()
        self.assertTrue(wizard.preseed_database_module_ids)
        wizard.action_write_result()
        build.refresh()
        self.assertEqual(build.state, 'pending')
        self.assertTrue(build.preseed_database)
        self.assertTrue(build.preseed_repo_ids)
        build.write({'state': 'done'})
        build._local_cleanup()
        wizard._refresh_preseed_database()
        self.assertEqual(build.state, 'pending')

        # let the build build
        run_build(build)
        # and be sure this uses our preseed database
        run_build(cloned_build)

        build._kill()
        cloned_build._kill()
        shutil.rmtree(repo.path, ignore_errors=True)
        repo.unlink()
