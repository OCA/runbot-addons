# -*- encoding: utf-8 -*-
# Copyrigh 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
