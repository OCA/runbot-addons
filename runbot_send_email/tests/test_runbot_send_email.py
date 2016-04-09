# coding: utf-8
# © 2015 Vauxoo
#   Coded by: lescobar@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import threading

from lxml import etree

from openerp import exceptions
from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


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
        self.repo_obj = self.env['runbot.repo'].create({
            'name': repo_name,
            'modules_auto': 'repo',
            'mode': 'poll',
            'nginx': True,
        })
        self.branch_obj = self.env['runbot.branch'].create({
            'repo_id': self.repo_obj.id,
            'name': branch_name,
            'branch_name': 'branch_name',
            'sticky': False,
            'coverage': False,
        })
        recipient = os.environ.get('EMAIL_RECIPIENT', 'committer@testsend.com')
        self.build_obj = self.env['runbot.build'].create({
            'branch_id': self.branch_obj.id,
            'name': 'fcb98eb195fc62fa49873f8f101f1738e38ea7c0',
            'author': 'Test Author',
            'author_email': 'author@testsend.com',
            'committer': 'Test Committer',
            'committer_email': recipient,
            'subject': '[TEST] Test message commit',
            'date': '2016-03-08 00:00:00',
        })
        self.domain = [('repo_id', '=', self.repo_obj.id)]
        self.build = self.build_obj.search(self.domain)
        if os.environ.get('EMAIL_PASSWORD', False) and \
                os.environ.get('EMAIL_RECIPIENT', False) and \
                os.environ.get('EMAIL_USER', False):
            setattr(threading.currentThread(), 'testing', False)
            self.build.pool._init = False
            self.mail_server = self.env.ref(
                'runbot_send_email.runbot_send_ir_mail_server_demo')
            self.mail_server.write({
                'smtp_pass': os.environ.get('EMAIL_PASSWORD'),
                'smtp_user': os.environ.get('EMAIL_USER'),
                'sequence': 0,
            })
            # Added partner to set notify_email to always
        partner_obj = self.env['res.partner']
        partner_id = partner_obj.find_or_create(recipient)
        partner = partner_obj.browse(partner_id)
        partner.write({'notify_email': 'always'})

    def tearDown(self):
        """
        This method is overwrite because
        we need to reset values of setUp methods
        """
        super(TestRunbotSendEmail, self).tearDown()
        setattr(threading.currentThread(), 'testing', True)
        self.build.pool._init = True

    def test_10_test_connection(self):
        """
        This makes the test smtp conection if EMAIL_PASSWORD env is set
        """
        if os.environ.get('EMAIL_PASSWORD', False) and \
                os.environ.get('EMAIL_RECIPIENT', False) and \
                os.environ.get('EMAIL_USER', False):
            with self.assertRaisesRegexp(exceptions.except_orm,
                                         'Connection Test Succeeded!'):
                self.mail_server.test_smtp_connection()

    def test_20_send_email(self):
        """
        This test tries to send a runbot email with password
        """
        self.build.github_status()

    def test_30_send_email_result_ok(self):
        self.build = self.build.search(self.domain)
        self.build.write({'result': 'ok', 'state': 'done'})
        self.build.github_status()

    def test_30_send_email_result_ko(self):
        self.build = self.build.search(self.domain)
        self.build.write({'result': 'ko'})
        self.build.github_status()

    def test_30_send_email_result_warn(self):
        self.build = self.build.search(self.domain)
        self.build.write({'result': 'warn', 'state': 'done'})
        self.build.github_status()

    def test_40_send_email_state_testing(self):
        self.build = self.build.search(self.domain)
        self.build.write({'state': 'testing'})
        self.build.github_status()

    def test_50_send_email_brach_pr(self):
        self.branch_obj.write({'name': 'refs/pull/1'})
        self.build = self.build.search(self.domain)
        self.build.github_status()

    def test_60_coverage_value_error_form(self):
        self.env.ref('mail.email_compose_message_wizard_form').unlink()
        self.build.github_status()

    def test_70_coverage_value_error_template(self):
        self.env.ref('runbot_send_email.runbot_send_notif').unlink()
        with self.assertRaisesRegexp(etree.ParserError,
                                     'Document is empty'):
            self.build.github_status()
