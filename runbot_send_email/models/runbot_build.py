# coding: utf-8
# © 2016 Vauxoo
#   Coded by: lescobar@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import re
from urlparse import urlparse

from openerp import api, fields, models, _

_logger = logging.getLogger(__name__)


class RunbotBuild(models.Model):
    _name = "runbot.build"
    _inherit = ['runbot.build', 'mail.thread']

    repo_link = fields.Char()
    pr_link = fields.Char()
    commit_link = fields.Char()
    repo_host = fields.Char()
    repo_owner = fields.Char()
    repo_project = fields.Char()
    status_build = fields.Char(compute='_status_build')
    host_name = fields.Char(compute='_host_name')
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
    def get_github_links(self):
        repo_git_regex = r"((git@|https://)([\w\.@]+)(/|:))" + \
            r"([~\w,\-,\_]+)/" + r"([\w,\-,\_]+)(.git){0,1}((/){0,1})"
        for rec in self:
            rec.repo_host, rec.repo_owner, rec.repo_project = '', '', ''

            match_object = re.search(repo_git_regex, rec.repo_id.name)
            if match_object:
                rec.repo_host = match_object.group(3)
                rec.repo_owner = match_object.group(5)
                rec.repo_project = match_object.group(6)
            rec.repo_link = "https://" + rec.repo_host + '/' + rec.repo_owner \
                + '/' + rec.repo_project
            rec.pr_link = rec.repo_link + rec.branch_id.name.replace(
                'refs/heads', '/tree').replace('refs', '')
            rec.commit_link = rec.repo_link + '/commit/' + rec.name[:8]

    @api.multi
    def _host_name(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for record in self:
            record.host_name = urlparse(base_url).hostname

    @api.multi
    def _branch_name(self):
        for record in self:
            if 'pull' in record.branch_id.name:
                branch = _(u"PR #{}").format(record.branch_id.branch_name)
            else:
                branch = record.branch_id.branch_name
            record.branch_name = branch

    @api.multi
    def _status_build(self):
        for record in self:
            status = 'Broken'
            if record.state == 'testing':
                status = 'Testing'
            elif record.state in ('running', 'done'):
                if record.result == 'ok':
                    status = 'Fixed'
            record.status_build = status

    @api.multi
    def _subject_email(self):
        for record in self:
            pr_reg = "(\\/pull\\/)"
            match_pr = re.search(pr_reg, record.branch_id.name)

            if match_pr:
                subject_temp = _(u"[runbot] {}/{}#{}")\
                    .format(record.repo_owner, record.repo_project,
                            record.branch_id.branch_name)
            else:
                subject_temp = _(u"[runbot] {}/{}#{} - {}")\
                    .format(record.repo_owner, record.repo_project,
                            record.branch_id.branch_name, record.name[:8])

            record.subject_email = subject_temp

    @api.multi
    def _webaccess_link(self):
        for record in self:
            html = "http://{}/?db={}-all"
            link = _(html).format(record.domain, record.dest)
            record.webaccess_link = link

    @api.multi
    def _logplainbase_link(self):
        for record in self:
            html = "/runbot/static/build/{}/logs/job_10_test_base.txt"
            link = _(html).format(record.dest)
            record.logplainbase_link = link

    @api.multi
    def _logplainall_link(self):
        for record in self:
            html = "/runbot/static/build/{}/logs/job_20_test_all.txt"
            link = _(html).format(record.dest)
            record.logplainall_link = link

    @api.multi
    def _log_link(self):
        for record in self:
            html = "/runbot/build/{}"
            link = _(html).format(record.id)
            record.log_link = link

    @api.multi
    def _ssh_link(self):
        for record in self:
            html = "ssh -p {} root@{}"
            link = _(html).format(record.port+1, record.host_name)
            record.ssh_link = link

    @api.multi
    def _doc_link(self):
        for record in self:
            link = '/runbot_doc/static/index.html'
            record.doc_link = link

    @api.multi
    def _dockerdoc_link(self):
        for record in self:
            link = 'https://github.com/Vauxoo/travis2docker/wiki'
            record.dockerdoc_link = link

    @api.multi
    def _configfile_link(self):
        for record in self:
            link = 'https://github.com/Vauxoo/travis2docker/wiki'
            record.configfile_link = link

    @api.multi
    def _shareissue_link(self):
        for record in self:
            link = 'https://github.com/Vauxoo/runbot-addons/issues/new'
            record.shareissue_link = link

    @api.multi
    def action_send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'runbot_send_email', 'runbot_send_notif')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
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
        partner_obj = self.env['res.partner']
        for record in self:
            name_build = record.dest
            email_to = record.committer_email
            partner_id = partner_obj.find_or_create(email_to)
            partner = partner_obj.browse(partner_id)
            if partner not in record.message_partner_ids:
                record.message_subscribe([partner.id])
            email_act = record.action_send_email()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                record.with_context(email_ctx).message_post_with_template(
                    email_ctx.get('default_template_id'))
                _logger.info('Sent email to: %s, Build: %s', email_to,
                             name_build)

    @api.multi
    def github_status(self):
        super(RunbotBuild, self).github_status()
        for record in self:
            record.get_github_links()
            record.send_email()
