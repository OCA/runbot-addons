# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import time
import xmlrpclib

from openerp.tests.common import TransactionCase

from openerp.tools.misc import mute_logger

_logger = logging.getLogger(__name__)


class TestRunbotJobs(TransactionCase):

    def setUp(self):
        super(TestRunbotJobs, self).setUp()
        self.build_obj = self.env['runbot.build']
        self.repo_obj = self.env['runbot.repo']
        self.branch_obj = self.env['runbot.branch']
        self.repo = self.repo_obj.search([
            ('is_travis2docker_build', '=', True)], limit=1)
        self.repo_domain = [('repo_id', '=', self.repo.id)]
        self.cron = self.env.ref('runbot.repo_cron')
        self.cron.write({'active': False})
        self.build = None

    def tearDown(self):
        super(TestRunbotJobs, self).tearDown()
        self.cron.write({'active': True})
        _logger.info('job_10_test_base log' +
                     open(os.path.join(self.build.path(), "logs",
                                       "job_10_test_base.txt")).read())
        _logger.info('job_20_test_all log' +
                     open(os.path.join(self.build.path(), "logs",
                                       "job_20_test_all.txt")).read())

    @mute_logger('openerp.addons.runbot.runbot')
    def wait_change_job(self, current_job, build,
                        loops=36, timeout=10):
        for loop in range(loops):
            _logger.info("Repo Cron to wait change of state")
            self.repo.cron()
            if build.job != current_job:
                break
            time.sleep(timeout)
        return build.job

    def test_jobs(self):
        'Create build and run all jobs'
        self.assertEqual(len(self.repo), 1, "Repo not found")
        _logger.info("Repo update to get branches")
        self.repo.update()
        branch = self.branch_obj.search(self.repo_domain + [
            ('branch_name', '=', 'fast-travis-oca')], limit=1)
        if not branch:
            # If the branch has a commit too old then runbot ignore it
            branch = self.branch_obj.create({
                'repo_id': self.repo.id,
                'name': 'refs/heads/fast-travis-oca',
            })
        self.assertEqual(len(branch), 1, "Branch not found")
        self.build_obj.search([('branch_id', '=', branch.id)]).unlink()
        self.build_obj.create({'branch_id': branch.id, 'name': 'HEAD'})
        # runbot module has a inherit in create method
        # but a "return id" is missed. Then we need to search it.
        # https://github.com/odoo/odoo-extra/blob/038fd3e/runbot/runbot.py#L599
        self.build = self.build_obj.search([('branch_id', '=', branch.id)],
                                           limit=1)
        self.assertEqual(len(self.build) == 0, False, "Build not found")

        if self.build.state == 'done' and self.build.result == 'skipped':
            # When the last commit of the repo is too old,
            # runbot will skip this build then we are forcing it
            self.build.force()

        self.assertEqual(
            self.build.state, u'pending', "State should be pending")

        _logger.info("Repo Cron to change state to pending -> testing")
        self.repo.cron()
        self.assertEqual(
            self.build.state, u'testing', "State should be testing")
        self.assertEqual(
            self.build.job, u'job_10_test_base',
            "Job should be job_10_test_base")
        new_current_job = self.wait_change_job(self.build.job, self.build)

        self.assertEqual(
            new_current_job, u'job_20_test_all',
            "Job should be job_20_test_all")
        new_current_job = self.wait_change_job(new_current_job, self.build)

        self.assertEqual(
            new_current_job, u'job_30_run',
            "Job should be job_30_run")
        self.assertEqual(
            self.build.state, u'running',
            "Job state should be running")

        user_ids = self.connection_test(self.build, 36, 10)
        self.assertEqual(
            self.build.state, u'running',
            "Job state should be running still")
        self.assertEqual(
            len(user_ids) >= 1, True, "Failed connection test")

        self.build.kill()
        self.assertEqual(
            self.build.state, u'done', "Job state should be done")

        self.assertEqual(
            self.build.result, u'ok', "Job result should be ok")

    def connection_test(self, build, attempts=1, delay=0):
        username = "admin"
        password = "admin"
        database_name = "openerp_test"
        port = build.port
        host = '127.0.0.1'
        user_ids = []
        for _ in range(attempts):
            try:
                sock_common = xmlrpclib.ServerProxy(
                    "http://%s:%d/xmlrpc/common" % (host, port))
                uid = sock_common.login(
                    database_name, username, password)
                sock = xmlrpclib.ServerProxy(
                    "http://%s:%d/xmlrpc/object" % (host, port))
                user_ids = sock.execute(
                    database_name, uid, password, 'res.users',
                    'search', [('login', '=', 'admin')])
                _logger.info("Trying connect... connected.")
                return user_ids
            except BaseException:
                _logger.info("Trying connect to build %s %s:%s... failed.",
                             build.sequence, host, port)
            time.sleep(delay)
        return user_ids
