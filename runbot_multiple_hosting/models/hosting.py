# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests


class Hosting(object):
    def __init__(self):
        self.session = requests.Session()

    @classmethod
    def get_api_url(cls, endpoint):
        return '%s%s' % (cls.API_URL, endpoint)

    @classmethod
    def get_url(cls, endpoint, *args):
        tmp_endpoint = endpoint % tuple(args)
        return '%s%s' % (cls.URL, tmp_endpoint)

    def update_status_on_commit(self, owner, repository, commit_hash, status):
        raise NotImplementedError("Should have implemented this")
