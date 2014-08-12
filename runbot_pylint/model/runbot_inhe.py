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
import sys

class runbot_repo(osv.osv):

    _inherit = 'runbot.repo'

    _columns = {
        'pylint_config': fields.many2one('pylint.conf', string = 'Pylint Config'),
        'path_to_test': fields.char(string = "Path to test"),
    }

class runbot_build(osv.osv):
    _inherit = "runbot.build"
    
    def job_30_run(self, cr, uid, build, lock_path, log_path, args=None):
        #~ logger = logging.getLogger('runbot-job') #TODO show in the log server which is running
        res = super(runbot_build, self).job_30_run(cr, uid, build, lock_path, log_path)
        errors = []
        paths_to_test = []
        ignore = []
        build_openerp_path_base = os.path.join(build.path(),"openerp") #os.path.join
        if build.repo_id and build.repo_id.pylint_config:
            for err in build.repo_id.pylint_config.error_ids:
                errors.append("-e")
                errors.append(err.code)
            #~ logger.info("running pylint tests...")
            if build.repo_id.path_to_test:
                for path_str in build.repo_id.path_to_test.split(","):
                    if os.path.exists(os.path.join(build_openerp_path_base, path_str)):
                        paths_to_test.append(os.path.join(build_openerp_path_base, path_str))
                    #~ else:
                    #~ logger.info("not exists path [%s]" % (build_openerp_path_base + path_str))
            else:
                if os.path.exists(build_openerp_path_base):
                    paths_to_test.append(build_openerp_path_base)
                #~ else:
                #~ logger.info("not exists path [%s]" % (build_openerp_path))
            sys.path.append(build_openerp_path_base)
            if build.repo_id.pylint_config.ignore:
                ignore.append("--ignore=" + build.repo_id.pylint_config.ignore)
            self.pool.get("pylint.conf")._run_test_pylint(cr, uid, errors, paths_to_test, build.path(), ignore)
        return res
