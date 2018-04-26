# Copyright <2015> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
import subprocess
import time
import xmlrpc.client
import mock

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, Warning as UserError
from odoo.tools.misc import mute_logger

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
        self.cron = self.env.ref('runbot.runbot_repo_cron')
        self.cron.write({'active': False})
        self.build = None

    @mute_logger('odoo.addons.runbot.models.repo')
    def test_00_no_weblate_token(self):
        token = self.repo.weblate_token
        self.repo.weblate_token = None
        self.assertEqual(self.repo.weblate_validation(), None)
        self.assertEqual(self.repo.cron_weblate(), None)
        self.repo.weblate_token = token

    @mock.patch('requests.Session.get')
    def test_10_ok_weblate_validation(self, response):

        class Response(object):

            def raise_for_status(self):
                pass

            def json(self):
                return {'projects': []}

        response.return_value = Response()
        self.assertRaises(UserError, self.repo.weblate_validation)

    @mock.patch('requests.Session.get')
    def test_20_ko_weblate_validation(self, response):

        class Response(object):

            def raise_for_status(self):
                pass

            def json(self):
                return {}

        response.return_value = Response()
        self.assertRaises(ValidationError, self.repo.weblate_validation)

    @mute_logger('odoo.addons.runbot.models.repo')
    def test_30_cron_weblate(self):
        self.assertEqual(self.repo.cron_weblate(), None)

    def tearDown(self):
        super(TestRunbotJobs, self).tearDown()
        if not self.build:
            return
        self.cron.write({'active': True})
        _logger.info('job_10_test_base log' +
                     open(os.path.join(self.build._path(), "logs",
                                       "job_10_test_base.txt")).read())
        _logger.info('job_20_test_all log' +
                     open(os.path.join(self.build._path(), "logs",
                                       "job_20_test_all.txt")).read())

    def wait_change_job(self, current_job, build,
                        loops=60, timeout=15):
        for loop in range(loops):
            _logger.info("Repo Cron to wait change of state")
            self.repo._cron()
            if build.job != current_job:
                break
            time.sleep(timeout)
        return build.job

    @mute_logger('odoo.addons.runbot.models.repo')
    def test_jobs(self):
        'Create build and run all jobs'
        self.assertEqual(len(self.repo), 1, "Repo not found")
        _logger.info("Set a max age to get too old branches in order to avoid"
                     " ignore the branch without changes")
        self.env['ir.config_parameter'].sudo().set_param(
            "runbot.runbot_max_age", 365*10)
        _logger.info("Repo update to get branches")
        self.repo._update(self.repo)
        branch = self.branch_obj.search(self.repo_domain + [
            ('branch_name', '=', 'fast-travis-oca')], limit=1)
        self.assertTrue(branch, "Branch not found")
        _logger.info("Clean current builds")
        self.build_obj.search([('branch_id', '=', branch.id)]).unlink()
        # branch.write({'uses_weblate', True})  # Weblate is down :(
        self.repo._update(self.repo)
        self.build = self.build_obj.search([('branch_id', '=', branch.id)])
        self.assertTrue(len(self.build) == 1, "More than one builds created")
        self.assertEqual(
            self.build.state, u'pending', "State should be pending")

        _logger.info("Downloading docker image...")
        subprocess.call(['docker', 'pull', self.repo.travis2docker_image])
        _logger.info("...Docker image downloaded")

        _logger.info("Repo Cron to change state to pending -> testing")
        self.repo._cron()
        # self.build.write({'uses_weblate': True})  # Weblate is down :(
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
        self.assertTrue(
            len(user_ids) >= 1, "Failed connection test")

        self.repo._cron()
        self.assertTrue(self.build.docker_executed_commands,
                        "docker_executed_commands should be True")
        time.sleep(5)
        try:
            output = subprocess.check_output([
                "docker", "exec", self.build.docker_container,
                "/etc/init.d/ssh", "status"])
        except subprocess.CalledProcessError:
            output = b''
        self.assertIn(b'sshd is running', output, "SSH should be running")

        self.build._kill()
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
                sock_common = xmlrpc.client.ServerProxy(
                    "http://%s:%d/xmlrpc/common" % (host, port))
                uid = sock_common.login(
                    database_name, username, password)
                sock = xmlrpc.client.ServerProxy(
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
