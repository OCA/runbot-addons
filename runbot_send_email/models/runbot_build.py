# coding: utf-8
# © 2016 Vauxoo
#   Coded by: lescobar@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from urlparse import urlparse

from openerp import api, fields, models, _

_logger = logging.getLogger(__name__)


class RunbotBuild(models.Model):
    _name = "runbot.build"
    _inherit = ['runbot.build', 'mail.thread']

    host_name = fields.Char(compute='_host_name')
    repo_name = fields.Char(compute='_repo_name')
    branch_name = fields.Char(compute='_branch_name')
    subject_email = fields.Char(compute='_subject_email')
    webaccess_link = fields.Char(compute='_webaccess_link')
    logplainbase_link = fields.Char(compute='_logplainbase_link')
    logplainall_link = fields.Char(compute='_logplainall_link')
    log_link = fields.Char(compute='_log_link')
    ssh_link = fields.Char(compute='_ssh_link')
    doc_link = fields.Char(compute='_doc_link')
    dockerdoc_link = fields.Char(compute='_dockerdoc_link')
    configfile_link = fields.Char(compute='_configfile_link')
    shareissue_link = fields.Char(compute='_shareissue_link')

    @api.multi
    def _host_name(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        self.host_name = urlparse(base_url).hostname

    @api.multi
    def _repo_name(self):
        descrip = self.repo_id.name.replace('.git', '').replace(
                                'https://github.com/', '').replace('/', ' / ')
        self.repo_name = descrip

    @api.multi
    def _branch_name(self):
        if self.branch_id.name.find("pull") >= 0:
            branch = _(u"PR #{}").format(self.branch_id.branch_name)
        else:
            branch = self.branch_id.branch_name
        self.branch_name = branch

    @api.multi
    def _subject_email(self):
        status = 'Broken'
        if self.state == 'testing':
            status = 'Testing'
        elif self.state in ('running', 'done'):
            if self.result == 'ok':
                status = 'Fixed'

        self.subject_email = _(u"[runbot] {}: {} - {} - {}").format(status,
                                                            self.dest,
                                                            self.branch_name,
                                                            self.repo_name)

    @api.multi
    def _webaccess_link(self):
        html = "http://{}/?db={}-all"
        link = _(html).format(self.domain, self.dest)
        self.webaccess_link = link

    @api.multi
    def _logplainbase_link(self):
        html = "http://{}/runbot/static/build/{}/logs/job_10_test_base.txt"
        link = _(html).format(self.host, self.dest)
        self.logplainbase_link = link

    @api.multi
    def _logplainall_link(self):
        html = "http://{}/runbot/static/build/{}/logs/job_20_test_all.txt"
        link = _(html).format(self.host, self.dest)
        self.logplainall_link = link

    @api.multi
    def _log_link(self):
        html = "/runbot/build/{}"
        link = _(html).format(self.id)
        self.log_link = link

    @api.multi
    def _ssh_link(self):
        html = "ssh -p {} root@{}"
        link = _(html).format(self.port+1, self.host_name)
        self.ssh_link = link

    @api.multi
    def _doc_link(self):
        link = '/runbot_doc/static/index.html'
        self.doc_link = link

    @api.multi
    def _dockerdoc_link(self):
        link = 'https://github.com/Vauxoo/travis2docker/wiki'
        self.dockerdoc_link = link

    @api.multi
    def _configfile_link(self):
        link = 'https://github.com/Vauxoo/travis2docker/wiki'
        self.configfile_link = link

    @api.multi
    def _shareissue_link(self):
        link = 'https://github.com/Vauxoo/runbot-addons/issues/new'
        self.shareissue_link = link

    @api.multi
    def action_send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                                                        'runbot_send_email',
                                                        'runbot_send_notif')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail',
                                    'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'runbot',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def send_email(self):
        name_build = self.dest
        email_to = self.committer_email
        partner_obj = self.env['res.partner']
        partner_id = partner_obj.find_or_create(email_to)
        partner = partner_obj.browse(partner_id)
        if partner not in self.message_partner_ids:
            self.message_subscribe([partner.id])
        email_act = self.action_send_email()
        if email_act and email_act.get('context'):
            email_ctx = email_act['context']
            self.with_context(email_ctx).message_post_with_template(
                                                    email_ctx.get(
                                                        'default_template_id'))
            _logger.info('Sent email to: %s, Build: %s', email_to, name_build)
        return True

    @api.multi
    def github_status(self):
        super(RunbotBuild, self).github_status()
        self.send_email()
