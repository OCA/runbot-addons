# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests

from openerp import _, fields, models, api
from openerp.exceptions import ValidationError


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    is_travis2docker_build = fields.Boolean('Travis to docker build')
    travis2docker_test_disable = fields.Boolean('Test Disable?')
    weblate_url = fields.Char(default="https://weblate.vauxoo.com/api")
    weblate_token = fields.Char()

    @api.constrains('weblate_url', 'weblate_token')
    def weblate_validation(self):
        if not self.weblate_url or not self.weblate_token:
            return
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'mqt',
            'Authorization': 'Token %s' % self.weblate_token
        })
        response = session.get(self.weblate_url)
        response.raise_for_status()
        json = response.json()
        if 'projects' not in json:
            raise ValidationError(_('Response json bad formated'))