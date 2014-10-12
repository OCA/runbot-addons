# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

import logging
from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)


class runbot_repo(orm.Model):
    _inherit = "runbot.repo"
    _columns = {
        'is_custom_build': fields.boolean('Custom Build'),
        'custom_build_dir': fields.char(
            'Custom Build Directory',
            help="Relative directory where repo will be checked out"
        ),
        'custom_server_path': fields.char(
            'Custom Server Path',
            help="Relative path of starter script",
        ),
        'custom_server_params': fields.char(
            'Custom Server Flags', help="""\
Arguments to add to the openerp script
- Use %(custom_build_dir)s for relative custom build directory.
- Use %(custom_server_path)s for relative custom server path.
""",
        ),
        'custom_pre_build_cmd': fields.char(
            'Custom Pre-build Command', help="""\
- Use %(custom_build_dir)s for relative custom build directory.
- Use %(custom_server_path)s for relative custom server path.
"""),
    }
