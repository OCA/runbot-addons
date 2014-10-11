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
This module is used to create new fields in the inherited classes
to work with pylint from runbot
"""
from openerp.osv import fields, osv
import logging
import os
import stat
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


def get_depends(modules, addons_paths, depends=None):
    """
    Get recursive depends from addons_paths and modules list
    """
    if depends is None:
        depends = []
    for module in (modules or '').split(','):
        if module not in depends:
            depends.append(module)
            for addons_path in (addons_paths or '').split(','):
                addons_path = addons_path.strip()
                fname_openerp = os.path.join(addons_path, module,
                                             '__openerp__.py')
                if os.path.isfile(fname_openerp):
                    module_depends_list = safe_eval(
                        open(fname_openerp, "r").read()).get('depends', [])
                    if module_depends_list:
                        module_depends_str = ','.join(module_depends_list)
                        get_depends(module_depends_str, addons_paths,
                                    depends=depends)
    return depends


class RunbotRepo(osv.osv):

    """
    Added pylint_conf_path field to use a configuration
      of pylint by repository,
      to use for each build of repository.
    """

    _inherit = 'runbot.repo'

    _columns = {
        'pylint_conf_path': fields.char('Pylint conf path',
                                        help='Relative path to pylint'
                                        ' conf file'),
        'check_pylint': fields.boolean('Check pylint',
                                       help='Check pylint to modules'
                                       ' of this repo'),
    }

    def get_module_list(self, cr, uid, ids, treeish, context=None):
        """
        Get module list from a repo with a treeish (sha, tag or branch name)
        """
        if not ids:
            return True
        if isinstance(ids, (int, long)):
            ids = [ids]
        repo_paths_list = []
        for repo in self.browse(cr, uid, ids, context=context):
            command_git = ['ls-tree', treeish, '--name-only']
            # get addons list from main repo
            repo_paths_str = repo.git(command_git +
                                      ['addons/', 'openerp/addons/'])
            if not repo_paths_str:
                # get addons list from module repo
                repo_paths_str = repo.git(command_git)
            repo_paths_list = repo_paths_str and\
                repo_paths_str.rstrip().split('\n') or []
            repo_paths_list = [os.path.basename(module)
                               for module in repo_paths_list]
        return repo_paths_list


class RunbotBuild(osv.osv):

    """
    Added pylint_conf_path field,
    used by default the configuration of repository.
    """

    _inherit = "runbot.build"

    _columns = {
        'pylint_conf_path': fields.char('pylint conf path',
                                        help='Relative path to pylint'
                                        ' conf file'),
    }

    def _create(self, cr, user, values, context=None):
        """
        This method set configuration of pylint.
        """
        if values.get('branch_id', False)\
           and 'pylint_conf_path' not in values.keys():
            branch_id = self.pool.get('runbot.branch').\
                browse(cr, user, values['branch_id'])
            values.update({
                'pylint_conf_path':
                    branch_id.repo_id and branch_id.repo_id.pylint_conf_path
            })
        return super(RunbotBuild, self)._create(cr, user, values,
                                                context=context)

    # job_10_test_base = \
    #    lambda self, cr, uid, build, lock_path, log_path, args=None:\
    #    build.checkout()

    def get_repo_branch_name(self, cr, uid, ids, context=None):
        """
        This method get all repo id and branch name from a build.
        Include dependency repo.
        return dict {repo.id = branch_name}
        """
        if not ids:
            return True
        if isinstance(ids, (int, long)):
            ids = [ids]
        repo_branch_data = {}
        for build in self.browse(cr, uid, ids, context=context):
            hint_branches = set()
            for extra_repo in build.repo_id.dependency_ids:
                closest_name = build.get_closest_branch_name(
                    extra_repo.id, hint_branches)
                hint_branches.add(closest_name)
                repo_branch_data[extra_repo.id] = closest_name
            repo_branch_data[build.repo_id.id] = build.name
        return repo_branch_data

    def get_modules_to_check_pylint(self, cr, uid, ids, context=None):
        """
        This method get all modules to check pylint test.
        Using field runbot_repo.check_pylint check box and get modules list
        from branch with ls-tree.
        This method use build.modules too to get all depends from
        selected repo.
        """
        if not ids:
            return True
        if isinstance(ids, (int, long)):
            ids = [ids]
        repo_pool = self.pool['runbot.repo']
        modules_to_check_pylint = set()
        for build in self.browse(cr, uid, ids, context=context):
            # get ls-tree modules from repo.check_pylint==True
            repo_branch_name_data = build.get_repo_branch_name()
            for repo_id in repo_branch_name_data:
                repo = repo_pool.browse(cr, uid, repo_id, context=context)
                if repo.check_pylint:
                    branch_name = repo_branch_name_data[repo_id]
                    branch_ls = repo.get_module_list(branch_name)
                    modules_to_check_pylint |= set(branch_ls)

            # get all depends and sub-depends from modules
            _, modules = build.cmd()
            depends = set(get_depends(modules, build.server('addons')))

            # get all modules to check pylint intersection with modules depends
            modules_to_check_pylint = list(depends & modules_to_check_pylint)
        return modules_to_check_pylint

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
        if args is None:
            args = {}
        build._log('pylint_script', 'Start pylint script')
        if not build.pylint_conf_path:
            build._log('pylint_script', 'Not config file detected')
            return None
        path_pylint_conf = os.path\
            .join(os.path.split(build.server())[0],
                  build.pylint_conf_path)
        if not os.path.isfile(path_pylint_conf):
            build._log('pylint_script', 'Not file found [%s]' %
                       (path_pylint_conf))
            return None
        modules_to_check_pylint = build.get_modules_to_check_pylint()

        if not modules_to_check_pylint:
            build._log('pylint_script', 'Not modules to check pylint found')
            return None
        fname_pylint_run_sh = os.path.join(build.path(),
                                           'pylint_run.sh')
        with open(fname_pylint_run_sh, "w") as f_pylint_run_sh:
            f_pylint_run_sh.write("#!/bin/bash\n")
            f_pylint_run_sh.write("export PYTHONPATH="
                                  "$PYTHONPATH:%s\n" %
                                  (build.server()))
            for module_to_check_pylint in modules_to_check_pylint:
                cmd = "pylint --rcfile=%s %s" % \
                      (path_pylint_conf,
                       os.path.join(build.server('addons'),
                                    module_to_check_pylint))
                f_pylint_run_sh.write(cmd + '\n')

            # TODO: Add check pdb and print sentence check in
            #       other local script
            fname_custom_pylint_run = os.path.join(
                build.path(), "check_ast/check_print_and_pdb.py")
            if os.path.isfile(fname_custom_pylint_run):
                for module_to_check_pylint in modules_to_check_pylint:
                    cmd = "%s %s" % (fname_custom_pylint_run,
                                     os.path.join(build.server('addons'),
                                                  module_to_check_pylint))
                    f_pylint_run_sh.write(cmd + '\n')

        # change mode to execute
        fpylint_stat = os.stat(fname_pylint_run_sh)
        os.chmod(fname_pylint_run_sh, fpylint_stat.st_mode | stat.S_IEXEC)
        return build.spawn([fname_pylint_run_sh],
                           lock_path, log_path, cpu_limit=2100)

    def job_30_run(self, cr, uid, build, lock_path, log_path):
        """
        Inherit method to make logs from pylint errors
        """
        res = super(RunbotBuild, self).job_30_run(cr, uid, build, lock_path,
                                                  log_path)
        pylint_log = build.path('logs', 'job_15_pylint.txt')
        pylint_error = False
        max_log_lines = 20
        count = 0
        if os.path.isfile(pylint_log):
            with open(pylint_log, "r") as fpylint_log:
                for line in fpylint_log.xreadlines():
                    if not pylint_error and '****' in line:
                        pylint_error = True
                    if pylint_error:
                        self.pool['ir.logging'].create(cr, uid, {
                            'build_id': build.id,
                            'level': 'WARNING',
                            'type': 'runbot',
                            'name': 'odoo.runbot',
                            'message': line,
                            'path': 'runbot',
                            'func': 'pylint result',
                            'line': '0',
                        })
                        count += 1
                        if count >= max_log_lines:
                            build._log('pylint_script', 'pylint has many'
                                       ' errors. Please check pylint full'
                                       ' log file...')
                            break
        if pylint_error and build.result == "ok":
            build.write({'result': 'warn'})
        return res
