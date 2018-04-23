# Copyright <2016> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class RunbotRepo(models.Model):

    _name = 'runbot.repo'
    _inherit = ['runbot.repo', 'mail.thread']

    def user_follow_unfollow(self):
        """follow/unfollow a repository with the user that has logged.
        """
        self.ensure_one()
        if self.env.user.partner_id not in self.message_partner_ids:
            self.message_subscribe_users(user_ids=[self.env.uid])
            return True
        self.message_unsubscribe_users(user_ids=[self.env.uid])
        return False

    @api.model
    def create(self, vals):
        """Skip add follower to user that creates this record
        """
        self_ctx = self.with_context(mail_create_nosubscribe=True)
        return super(RunbotRepo, self_ctx).create(vals)
