# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import subprocess
import time
import xmlrpclib

from openerp.tests.common import TransactionCase


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

    def wait_change_job(self, current_job, build,
                        loops=36, timeout=10):
        for _ in range(loops):
            self.repo.cron()
            if build.job != current_job:
                break
            time.sleep(timeout)
        return build.job

    def test_jobs(self):
        'Create build and run all jobs'
        self.assertEqual(len(self.repo), 1, "Repo not found")
        self.repo.update()
        branch = self.branch_obj.search(self.repo_domain + [
            ('name', 'like', 'fast')], limit=1)
        self.assertEqual(len(branch), 1, "Branch not found")
        self.build_obj.search([('branch_id', '=', branch.id)]).unlink()

        self.repo.update()
        build = self.build_obj.search([
            ('branch_id', '=', branch.id)], limit=1)
        self.assertEqual(len(build) == 0, False, "Build not found")
        self.assertEqual(
            build.state, u'pending', "State should be pending")

        self.repo.cron()
        self.assertEqual(
            build.state, u'testing', "State should be testing")
        self.assertEqual(
            build.job, u'job_10_test_base',
            "Job should be job_10_test_base")
        new_current_job = self.wait_change_job(build.job, build)
        _logger.info(open(os.path.join(build.path(), "logs",
                                       "job_10_test_base.txt")).read())

        self.assertEqual(
            new_current_job, u'job_20_test_all',
            "Job should be job_20_test_all")
        new_current_job = self.wait_change_job(new_current_job, build)
        _logger.info(open(
            os.path.join(build.path(), "logs",
                         "job_20_test_all.txt")).read())

        self.assertEqual(
            new_current_job, u'job_30_run',
            "Job should be job_30_run")
        self.assertEqual(
            build.state, u'running',
            "Job state should be running")

        time.sleep(360)
        _logger.info(open(
            os.path.join(build.path(), "logs",
                         "job_30_run.txt")).read())

        self.assertEqual(
            build.state, u'running',
            "Job state should be running still")
        user_ids = self.connection_test(build)
        self.assertEqual(
            len(user_ids) >= 1, True, "Failed connection test")

        build.kill()
        self.assertEqual(
            build.state, u'done', "Job state should be done")

        self.assertEqual(
            build.result, u'ok', "Job result should be ok")

        self.assertTrue(
            self.docker_registry_test(build),
            "Docker image don't found in registry.",
        )

    def docker_registry_test(self, build):
        cmd = [
            "curl", "--silent",
            "localhost:5000/v2/"
            "vauxoo-dev-runbot_branch_remote_name_grp_feature2/tags/list",
        ]
        tag_list_output = subprocess.check_output(cmd)
        tag_build = build.docker_image_cache.split(':')[-1]
        if tag_build in tag_list_output:
            return True
        else:
            return False

    def connection_test(self, build):
        username = "admin"
        password = "admin"
        database_name = "openerp_test"
        port = build.port
        host = '127.0.0.1'
        sock_common = xmlrpclib.ServerProxy(
            "http://%s:%d/xmlrpc/common" % (host, port))
        uid = sock_common.login(
            database_name, username, password)
        sock = xmlrpclib.ServerProxy(
            "http://%s:%d/xmlrpc/object" % (host, port))
        user_ids = sock.execute(
            database_name, uid, password, 'res.users',
            'search', [('login', '=', 'admin')])
        return user_ids
