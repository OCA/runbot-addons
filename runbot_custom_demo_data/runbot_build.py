# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models, tools

from openerp.addons.runbot.runbot import now
from openerp.addons.runbot.runbot import grep

_logger = logging.getLogger(__name__)


class RunbotRepo(models.Model):
    _inherit = 'runbot.repo'

    custom_demo_data = fields.Boolean(
        'Load custom data', default=False,
        help="Load only the demo data from this repository")


class RunbotBuild(models.Model):
    _inherit = "runbot.build"

    @api.model
    def job_15_install_all(self, build, lock_path, log_path):
        """
        Install needed modules and dependencies without any demo data
        """
        if build.repo_id.custom_demo_data:
            build._log('install_all', 'Start install all modules')
            self.pg_createdb("%s-all" % build.dest)
            cmd, mods = build.cmd()
            if grep(build.server("tools/config.py"), "test-enable"):
                cmd.append("--test-enable")
            cmd += [
                '-d',
                '%s-all' % build.dest,
                '-i',
                tools.ustr(mods),
                '--without-demo=all',
                '--stop-after-init',
                '--log-level=test',
                '--max-cron-threads=0'
            ]
            # reset job_start to an accurate job_15 job_time
            build.job_start = now()
            return self.spawn(cmd, lock_path, log_path, cpu_limit=2100)

    @api.model
    def job_20_test_all(self, build, lock_path, log_path):
        """
        Avoid the creation of the database if the job 15 was runned
        """
        build._log('test_all', 'Start test all modules')
        if not build.repo_id.custom_demo_data:
            self.pg_createdb("%s-all" % build.dest)
        cmd, mods = build.cmd()
        if grep(build.server("tools/config.py"), "test-enable"):
            cmd.append("--test-enable")
        cmd += [
            '-d',
            '%s-all' % build.dest,
            '-i',
            tools.ustr(mods),
            '--stop-after-init',
            '--log-level=test',
            '--max-cron-threads=0'
        ]
        # reset job_start to an accurate job_20 job_time
        build.job_start = now()
        return self.spawn(cmd, lock_path, log_path, cpu_limit=2100)
