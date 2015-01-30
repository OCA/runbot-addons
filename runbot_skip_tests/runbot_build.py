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

from openerp.osv import orm

import logging
_logger = logging.getLogger(__name__)


class runbot_build(orm.Model):
    _inherit = "runbot.build"

    def spawn(self, cmd, lock_path, log_path, cpu_limit=None, shell=False):
        """Remove "--test-enable" from cmd line"""
        cmd = [c for c in cmd if c != '--test-enable']
        return super(runbot_build, self).spawn(
            cmd,
            lock_path,
            log_path,
            cpu_limit=cpu_limit,
            shell=shell,
        )
