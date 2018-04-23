# Copyright <2016> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import threading
import unittest

from odoo import exceptions
from odoo.tests.common import TransactionCase
from odoo.tools import config, mute_logger

_logger = logging.getLogger(__name__)

SEND_REAL_EMAIL = (
    os.environ.get('EMAIL_PASSWORD') and os.environ.get('EMAIL_RECIPIENT') and
    os.environ.get('EMAIL_USER'))


class TestRunbotSendEmail(TransactionCase):
    """
    This create a runbot send email test
    """

    def setUp(self):
        """
        This add required environment variable for test
        """
        super(TestRunbotSendEmail, self).setUp()
        repo_name = 'https://github.com/owner/repo_name.git'
        branch_name = 'refs/heads/branch_name'
        self.repo = self.env['runbot.repo'].create({
            'name': repo_name,
            'modules_auto': 'repo',
            'mode': 'poll',
            'nginx': True,
        })
        self.branch = self.env['runbot.branch'].create({
            'repo_id': self.repo.id,
            'name': branch_name,
            'branch_name': 'branch_name',
            'sticky': False,
            'coverage': False,
        })
        recipient = os.environ.get('EMAIL_RECIPIENT', 'committer@testsend.com')
        self.partner = self.env.ref('base.user_demo').partner_id
        self.partner.email = recipient
        self.build = self.env['runbot.build'].create({
            'branch_id': self.branch.id,
            'name': 'fcb98eb195fc62fa49873f8f101f1738e38ea7c0',
            'author': 'Test Author',
            'author_email': 'author@testsend.com',
            'committer': 'Test Committer',
            'committer_email': recipient,
            'subject': '[TEST] Test message commit',
            'date': '2016-03-08 00:00:00',
            'state': 'running',
        })
        self.template = self.build.get_email_template()
        self.template.auto_delete = False
        if SEND_REAL_EMAIL:
            setattr(threading.currentThread(), 'testing', False)
            self.build.pool._init = False
            self.mail_server = self.env.ref(
                'runbot_send_email.runbot_send_ir_mail_server_demo')
            self.mail_server.write({
                'smtp_pass': os.environ['EMAIL_PASSWORD'],
                'smtp_user': os.environ['EMAIL_USER'],
                'sequence': 0,
            })

    def tearDown(self):
        """
        This method is overwrite because
        we need to reset values of setUp methods
        """
        super(TestRunbotSendEmail, self).tearDown()
        setattr(threading.currentThread(), 'testing', True)
        self.build.pool._init = True

    @unittest.skipIf(not SEND_REAL_EMAIL,
                     "If real values are not used then skip")
    def test_test_connection(self):
        """This makes the test smtp conection if EMAIL_PASSWORD env is set
        """
        with self.assertRaisesRegex(exceptions.except_orm,
                                    'Connection Test Succeeded!'):
            self.mail_server.test_smtp_connection()

    def test_send_email_result_ok(self):
        self.build.result = 'ok'
        self.build._github_status()
        mail = self.get_last_build_mail(self.build)
        self.assertIn("Build #%d is ok" % self.build.id, mail.body)

    def test_send_email_result_ko(self):
        self.build.result = 'ko'
        self.build._github_status()
        mail = self.get_last_build_mail(self.build)
        self.assertIn("Build #%d failed" % self.build.id, mail.body)

    def test_send_email_result_warn(self):
        self.build.result = 'warn'
        self.build._github_status()
        mail = self.get_last_build_mail(self.build)
        self.assertIn("Build #%d has warnings" % self.build.id, mail.body)

    def test_send_email_branch_pr(self):
        self.branch.write({'name': 'refs/pull/1'})
        self.build._github_status()
        mail = self.get_last_build_mail(self.build)
        self.assertIn("pull/1", mail.body)

    def test_user_follow_unfollow_runbot_build(self):
        """Test for the method user_follow_unfollow for the model runbot.build.
        """
        user = self.env['res.users'].browse(self.env.uid)
        result = self.build.user_follow_unfollow()
        self.assertTrue(result)
        self.assertIn(user.partner_id, self.build.message_partner_ids,
                      "Current user was not found as follower")
        self.assertIn(self.partner, self.build.message_partner_ids,
                      "The committer was not found as follower")
        result = self.build.user_follow_unfollow()
        self.assertFalse(result)
        self.assertNotIn(user.partner_id, self.build.message_partner_ids)

    def test_follow_committer_write(self):
        """Test that write method adds the committe as follower"""
        self.build.commmitter_email = False
        self.build.message_unsubscribe(self.build.message_partner_ids.ids)
        self.assertFalse(self.build.message_partner_ids)
        self.build.committer_email = self.partner.email
        self.assertEquals(self.build.message_partner_ids, self.partner)

    def test_user_follow_unfollow_runbot_repo(self):
        """Test for the method user_follow_unfollow for the model runbot.repo.
        """
        result = self.build.repo_id.user_follow_unfollow()
        self.assertTrue(result)
        user = self.env['res.users'].browse(self.env.uid)
        followers = self.build.repo_id.message_partner_ids
        self.assertIn(user.partner_id, followers)
        result = self.build.repo_id.user_follow_unfollow()
        self.assertFalse(result)
        self.assertFalse(self.build.repo_id.message_partner_ids)

    def get_last_build_mail(self, build):
        mail = self.env['mail.mail'].search([
            ('res_id', '=', build.id), ('model', '=', build._name),
        ], limit=1, order='id desc')
        if config.get('test_report_directory'):
            fpath = os.path.join(config['test_report_directory'],
                                 "%s.html" % self._testMethodName)
            with open(fpath, "w") as ftmp:
                ftmp.write(mail.body or '')
        return mail

    @mute_logger('odoo.addons.mail.models.mail_mail')
    def test_send_email(self):
        """Test for check if the email_to is filled correctly.
        """
        result = self.build.user_follow_unfollow()
        self.assertTrue(result)
        emails = self.build.message_partner_ids.mapped('email')
        self.assertTrue(emails)
        self.build.send_email()
        mail = self.get_last_build_mail(self.build)
        self.assertTrue(mail.body)
        self.assertEqual(sorted(mail.email_to.split(',')), sorted(emails))
