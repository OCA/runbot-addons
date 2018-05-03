# -*- encoding: utf-8 -*-
# © 2010 - 2014 Savoir-faire Linux
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import inspect
from openerp import models


class RunbotBuild(models.Model):
    _inherit = "runbot.build"

    def spawn(self, cmd, lock_path, log_path, cpu_limit=None, shell=False):
        """Remove "--test-enable" from cmd line"""
        # but only if the user chose for it
        for frame, _, _, _, _, _ in inspect.stack():
            if 'build' in frame.f_locals:
                if frame.f_locals['build'].branch_id.repo_id.skip_test:
                    cmd = [c for c in cmd if c != '--test-enable']
                break
        return super(RunbotBuild, self).spawn(
            cmd,
            lock_path,
            log_path,
            cpu_limit=cpu_limit,
            shell=shell,
        )

    def job_10_test_base(self, cr, uid, build, lock_path, log_path):
        if build.branch_id.repo_id.skip_build:
            build.write({'result': 'ok', 'state': 'done'})
            return -2
        return super(RunbotBuild, self).job_10_test_base(
            cr, uid, build, lock_path, log_path
        )

    def job_20_test_all(self, cr, uid, build, lock_path, log_path):
        if build.branch_id.repo_id.skip_build:
            build.write({'result': 'ok', 'state': 'done'})
            return -2
        return super(RunbotBuild, self).job_20_test_all(
            cr, uid, build, lock_path, log_path
        )

    def job_30_run(self, cr, uid, build, lock_path, log_path):
        if build.branch_id.repo_id.skip_build:
            build.write({'result': 'ok', 'state': 'done'})
            return -2
        return super(RunbotBuild, self).job_30_run(
            cr, uid, build, lock_path, log_path
        )
