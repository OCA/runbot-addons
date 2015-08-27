# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Samuel Lefever
#    Copyright 2015 Niboo SPRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
import openerp
from openerp.fields import Boolean
from openerp.models import api, Model
from openerp.addons.runbot.runbot import now
from openerp.addons.runbot.runbot import grep

_logger = logging.getLogger(__name__)


class RunbotRepo(Model):
    _inherit = 'runbot.repo'

    custom_demo_data = Boolean(
        'Load custom data', default=False,
        help="Load only the demo data from this repository")


class RunbotBuild(Model):
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
                openerp.tools.ustr(mods),
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
            openerp.tools.ustr(mods),
            '--stop-after-init',
            '--log-level=test',
            '--max-cron-threads=0'
        ]
        # reset job_start to an accurate job_20 job_time
        build.job_start = now()
        return self.spawn(cmd, lock_path, log_path, cpu_limit=2100)
