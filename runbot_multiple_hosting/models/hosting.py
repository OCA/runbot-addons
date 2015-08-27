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
