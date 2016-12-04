# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Sylvain VanHoof, Samuel Lefever
#    Odoo, Open Source Management Solution
#    Copyright (C) 2010-2015 Eezee-It (<http://www.eezee-it.com>).
#    Copyright 2015 Niboo (<http://www.niboo.be>).
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
from openerp.addons.runbot_multiple_hosting.models import hosting


class GithubHosting(hosting.Hosting):
    API_URL = 'https://api.github.com'
    URL = 'https://github.com'

    def __init__(self, credentials):
        super(GithubHosting, self).__init__()

        token = (credentials, 'x-oauth-basic')
        self.session.auth = token
        self.session.headers.update(
            {'Accept': 'application/vnd.github.she-hulk-preview+json'}
        )

    @classmethod
    def get_branch_url(cls, owner, repository, branch):
        return cls.get_url('/%s/%s/tree/%s', owner, repository, branch)

    @classmethod
    def get_pull_request_url(cls, owner, repository, pull_number):
        return cls.get_url('/%s/%s/pull/%s', owner, repository, pull_number)

    def get_pull_request(self, owner, repository, pull_number):
        url = self.get_api_url('/repos/%s/%s/pulls/%s' % (owner, repository,
                                                          pull_number))
        response = self.session.get(url)
        return response.json()
