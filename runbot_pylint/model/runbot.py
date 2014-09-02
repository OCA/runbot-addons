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
"""
This module is used to create new fields in the inherited classes.
"""
from openerp.osv import fields, osv
import logging
import os

_logger = logging.getLogger(__name__)
list_no_rep = {}
list_dependences = []

class RunbotRepo(osv.osv):
    """
    Added pylint_config field to use a configuration of pylint by repository,
    to use for each build of repository.
    """

    _inherit = 'runbot.repo'

    _columns = {
        'pylint_config': fields.many2one('pylint.conf',
                                         string='Pylint Config'),
        'check_pylint': fields.boolean(string='Check pylint'),
    }


class RunbotBuild(osv.osv):
    """
    Added pylint_config field, used by default the configuration of repository.
    """

    _inherit = "runbot.build"

    _columns = {
        'pylint_config': fields.many2one('pylint.conf',
                                         string='Pylint Config'),
    }

    def create(self, cr, uid, values, context=None):
        """
        This method set configuration of pylint.
        """
        new_id = super(RunbotBuild, self).create(cr, uid, values,
                                                             context=context)
        if values.get('branch_id', False) and not values\
                                                    .has_key('pylint_config'):
            branch_id = self.pool.get('runbot.branch').browse(cr, uid,
                                                         values['branch_id'])
            self.write(
                cr, uid, [new_id],
                 {'pylint_config': branch_id.repo_id and \
                 branch_id.repo_id.pylint_config and \
                 branch_id.repo_id.pylint_config.id or False}, context=context)
        return new_id

    def get_module_depends(self, cr, uid, build_id, module, context=None):
        dict_tmp = {}
        build = self.browse(cr, uid, [build_id], context=context)[0]
        base_path = build.server('addons')
        mod_openerp = os.path.join(base_path, module, '__openerp__.py')
        file_openerp = open(mod_openerp)
        text_file = file_openerp.read()
        list_depends = eval(text_file).get('depends', False)
        file_openerp.close()
        for depend in list_depends:
            if not os.path.join(base_path, depend) in list_dependences:
                list_dependences.append(os.path.join(base_path, depend))
            list_dependences.extend([element for element in self.get_module_depends(cr, uid, build_id, depend) if element not in list_dependences])
        return list_dependences

    def get_repo_build_paths(self, cr, uid, build_id, repo_id, filter=None, isdir=True, check_module_depends=True, context=None):
        if filter is None:
            filter = []
        repo_pool = self.pool['runbot.repo']
        repo = repo_pool.browse(cr, uid, [repo_id], context=context)[0]
        build = self.browse(cr, uid, [build_id], context=context)[0]
        #TODO: Add version or sha and replace by master
        version_build = build.branch_id and build.branch_id.branch_base_name or build.branch_id.branch_name
        import pdb;pdb.set_trace()
        command_git = ['ls-tree', version_build, '--name-only']
        if repo.type == 'main':
            command_git.append('addons/')
        repo_paths_str = repo.git(command_git)
        repo_paths_list = repo_paths_str and repo_paths_str.rstrip().replace('addons/', '').split('\n') or []
        paths = []
        if repo_paths_list:
            #if repo.type == 'main':
            base_path = build.server('addons')
            if base_path:
                for repo_path in repo_paths_list:
                    repo_full_path = os.path.join(base_path, repo_path)
                    if os.path.isdir(repo_full_path) and isdir:
                        paths.append( repo_full_path )
                    elif os.path.isfile(repo_full_path) and \
                           (os.path.splitext(repo_full_path)[1] in filter or not filter):
                        paths.append( repo_full_path )
        return paths

    def job_01_pylint(self, cr, uid, build, lock_path, log_path, args=None):
        #TODO: Comment this function. Uncomment only to test pylint script fast.
        build._log('pylint_script', 'Start pylint script before all test')
        build.checkout()
        return self.job_15_pylint(cr, uid, build, lock_path, log_path, args=args)

    def job_15_pylint(self, cr, uid, build, lock_path, log_path, args=None):
        """
        This method is used to run pylint test, getting parameters of the
        pylint configuration, the parameters errors and files to ignore has
        send in list structures to method _run_test_pylint.

        :param build: object build of runbot.
        :param lock_path: path of lock file, this parameter is string.
        :param log_path: path of log file, this parameter is string, where are
                            has saved the log of test.
        :param args: this parameter not is required, not is used.
        """
        if args == None:
            args = {}
        build._log('pylint_script', 'Start pylint script')
        params_extra = []
        errors = []
        #~ paths_to_test = []
        ignore = []
        result = False
        dep = []
        repo_paths = []
        repo_depen = []
        if build.pylint_config:
            if build.pylint_config.conf_file:
                path_pylint_conf = os.path\
                    .join(os.path.split(build.server())[0], \
                    build.pylint_config.conf_file)

                if build.repo_id.check_pylint:
                    repo_paths = self.get_repo_build_paths(cr, uid, build.id, \
                        build.repo_id.id, filter=['.py'])
                    print repo_paths, 'EEEEEEEEEEEEEEEEEEEEEEEEEEEe'
                
                for module in build.modules.split(','):
                    dep = self.get_module_depends(cr, uid, build.id, module)
                if repo_paths and dep:
                    repo_paths = set(repo_paths)
                    dep = set(dep)
                    repo_depen = list(repo_paths&dep)
                    print repo_depen, 'TTTTTTTTTTTTTTTTTTTTTTT'
                if os.path.isfile(path_pylint_conf):
                    params_extra.append("--rcfile=" + path_pylint_conf)
                else:
                    _logger.warning("rcfile %s not found"%( path_pylint_conf ))
            if build.pylint_config.error_ids:
                errors.append("-d")
                errors.append("all")
                for err in build.pylint_config.error_ids:
                    errors.append("-e")
                    errors.append(err.code)
            _logger.info("running pylint tests...")
            if not repo_depen:
                if os.path.exists(build.server()):
                    paths_to_test.append(build.server())
                else:
                    _logger.info("not exists path [%s]" % (build.server()))
                #~ for path_str in build.pylint_config.\
                #~ path_to_test.strip(' ').split(","):
                    #~ if os.path.exists(os.path.join(build.server(), path_str)):
                        #~ paths_to_test.append(
                            #~ os.path.join(build.server(), path_str))
                    #~ else:
                        #~ _logger.info("not exists path [%s]" % (
                            #~ os.path.join(build.server(), path_str), ))
            #~ else:
                #~ if os.path.exists(build.server()):
                    #~ paths_to_test.append(build.server())
                #~ else:
                    #~ _logger.info("not exists path [%s]" % (build.server()))
            if build.pylint_config.ignore:
                ignore.append("--ignore=" + build.pylint_config.ignore)

            result = self.pool.get("pylint.conf")._run_test_pylint(
                cr, uid, errors, repo_depen, build.server(), ignore,
                log_path, lock_path, params_extra)
            if build.pylint_config and build.pylint_config.check_print or \
                 build.pylint_config and build.pylint_config.check_pdb:
                self.pool.get("pylint.conf")._search_print_pdb(cr,
                                                     uid, build, repo_depen)
        return result
