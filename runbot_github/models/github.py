# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
