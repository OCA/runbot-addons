#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: vauxoo consultores (info@vauxoo.com)
#
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

import argparse
from openerp.osv import fields, osv
import logging
import subprocess
import os
import openerp.tools as tools
logger = logging.getLogger('runbot-job')

class runbot_repo(osv.osv):

    _inherit = 'runbot.repo'

    _columns = {
        'pylint_config': fields.many2one('pylint.conf', string = 'Pylint Config'),
    }

class runbot_build(osv.osv):
    _inherit = "runbot.build"
    
    def job_30_run(self, cr, uid, build, lock_path, log_path, args=None):
        logger = logging.getLogger('runbot-job')
        res = super(runbot_build, self).job_30_run(cr, uid, build, lock_path, log_path)
        errors = []
        if build.repo_id and build.repo_id.pylint_config:
            for err in build.repo_id.pylint_config.error_ids:
                errors.append("-e")
                errors.append(err.code)
            logger.info("running pylint tests...")
            build_openerp_path=build.path()+'/odoo.py'
            self.pool.get("pylint.conf")._run_test_pylint(cr, uid, errors, build_openerp_path)
        return res
