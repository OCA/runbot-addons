# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
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

import os

import logging
_logger = logging.getLogger(__name__)

from openerp import models, api, SUPERUSER_ID


class RunbotRepo(models.Model):
    """Aggressively clean filesystem databases and processes."""
    _inherit = "runbot.repo"

    def __init__(self, pool, cr):
        """On reinitialisation of db, mark all builds as done"""
        super(RunbotRepo, self).__init__(pool, cr)
        runbot_build = pool['runbot.build']
        ids = pool['runbot.build'].search(cr, SUPERUSER_ID, [])
        runbot_build.write(cr, SUPERUSER_ID, ids, {'state': 'done'})

    @api.model
    def cron(self):
        """Overcharge cron, add clean up subroutine before the general cron."""
        self.clean_up()
        return super(RunbotRepo, self).cron()

    def clean_up(self):
        """Examines the build directory, identify leftover builds then
        call the cleans: filesystem, database, process

        Leftover builds will have state done
        """
        build_root = os.path.join(self.root(), 'build')
        build_dirs = set(os.listdir(build_root))
        valid_builds = [b.dest for b in self.env['runbot.build'].search([
            ('dest', 'in', list(build_dirs)),
            ('state', '!=', 'done')
        ])]
        for pattern in build_dirs.difference(valid_builds):
            _logger.info("Runbot Janitor Cleaning up Residue: %s" % pattern)
            self.clean_up_database(pattern)
            self.clean_up_process(pattern)
            self.clean_up_filesystem(pattern)

    def clean_up_database(self, pattern):
        """Drop all databases whose names match the directory names matching
        the pattern.

        :param pattern:string
        """
        pass

    def clean_up_process(self, pattern):
        """Kill processes which run executables in those directories or are
        connected to databases matching the directory names matching
        the pattern.

        :param pattern: string
        """
        pass

    def clean_up_filesystem(self, pattern):
        """Delete the directory and its contents matching the pattern.

        :param pattern: string
        """
        pass
