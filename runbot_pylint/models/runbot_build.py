# -*- encoding: utf-8 -*-
##############################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: moylop260@vauxoo.com
############################################################################

"""
This module is used to create new fields in the inherited classes
to work with pylint from runbot
"""

import os
import stat
from itertools import ifilter, imap

from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval


# Max number of lines to create logs in database
MAX_LOG_LINES = 20


def get_depends(modules, addons_paths):
    """
    Get recursive depends from addons_paths and modules list
    :param str modules: comma separated list of modules
    :param str addons_paths: comma separated list of paths for modules
    :return set: Unsorted set of recursive dependencies of modules
    """
    modules = set(map(
        lambda mystr: mystr.strip(), (modules or '').split(",")))
    addons_paths = set(map(
        lambda mystr: mystr.strip(), (addons_paths or '').split(',')))
    visited = set()
    while modules != visited:
        module = (modules - visited).pop()
        visited.add(module)
        manifest_path = os.path.join(module, '__openerp__.py')
        try:
            manifest_filename = next(ifilter(
                os.path.isfile,
                imap(lambda p: os.path.join(p, manifest_path), addons_paths)
            ))
        except StopIteration:
            # For some reason the module wasn't found
            continue
        manifest = safe_eval(open(manifest_filename).read())
        modules.update(manifest.get('depends', []))
    return modules


class RunbotBuild(models.Model):

    """
    Added pylint_conf_path field,
    used by default the configuration of repository.
    """

    _inherit = "runbot.build"

    pylint_conf_path = fields.Char(
        help='Relative path to pylint conf file')

    @api.model
    def create(self, values):
        """
        This method set configuration of pylint.
        """
        if values.get('branch_id', False) \
           and 'pylint_conf_path' not in values:
            branch = self.env['runbot.branch'].browse(
                values['branch_id'])
            values.update({
                'pylint_conf_path': branch.repo_id.pylint_conf_path,
            })
        return super(RunbotBuild, self).create(values)

    @api.multi
    def get_repo_branch_name(self):
        """
        This method get all repo id and branch name from a build.
        Include dependency repo.
        return dict {repo.id = branch_name}
        """
        repo_branch_data = {}
        for build in self:
            hint_branches = set()
            for extra_repo in build.repo_id.dependency_ids:
                closest_name = build._get_closest_branch_name(extra_repo.id)[1]
                hint_branches.add(closest_name)
                repo_branch_data[extra_repo.id] = closest_name
            repo_branch_data[build.repo_id.id] = build.name
        return repo_branch_data

    @api.multi
    def get_modules_to_check_pylint(self):
        """
        This method get all modules to check pylint test.
        Using field runbot_repo.check_pylint check box and get modules list
        from branch with ls-tree.
        This method use build.modules too to get all depends from
        selected repo.
        """
        repo_pool = self.env['runbot.repo']
        modules_to_check_pylint = set()
        for build in self:
            # get ls-tree modules from repo.check_pylint==True
            repo_branch_name_data = build.get_repo_branch_name()
            for repo_id in repo_branch_name_data:
                repo = repo_pool.browse(repo_id)
                if repo.check_pylint:
                    branch_name = repo_branch_name_data[repo_id]
                    branch_ls = repo.get_module_list(branch_name)
                    modules_to_check_pylint |= set(branch_ls)

            # get all depends and sub-depends from modules
            _, modules = build.cmd()
            depends = get_depends(modules, build.server('addons'))

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
            build._log('pylint_script', 'No config file detected')
            return None
        path_pylint_conf = os.path\
            .join(os.path.split(build.server())[0],
                  build.pylint_conf_path)
        if not os.path.isfile(path_pylint_conf):
            build._log('pylint_script', 'No file found [%s]' %
                       path_pylint_conf)
            return None
        modules_to_check_pylint = build.get_modules_to_check_pylint()

        if not modules_to_check_pylint:
            build._log('pylint_script', 'No modules to check pylint found')
            return None

        build._log('pylint_script', "Modules set for pylint check: %s" %
                   ', '.join(modules_to_check_pylint))

        fname_pylint_run_sh = os.path.join(build.path(),
                                           'pylint_run.sh')
        with open(fname_pylint_run_sh, "w") as f_pylint_run_sh:
            f_pylint_run_sh.write("#!/bin/sh\n")
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
        res = super(RunbotBuild, self).job_30_run(
            cr, uid, build, lock_path, log_path)
        pylint_log = build.path('logs', 'job_15_pylint.txt')
        count = 0
        if not os.path.isfile(pylint_log):
            # If don't exists pylint log then you build don't have
            # this feature configurated.
            return res
        with open(pylint_log) as fpylint_log:
            # pylint has output of '****'
            # in first line of log when has fails.
            try:
                pylint_error = True if '****' in fpylint_log.next() \
                    else False
            except StopIteration:
                # If file is empty then don't has errors
                pylint_error = False
            if not pylint_error:
                # If don't has errors then exit
                return res
            # Reset pointer file to run normal loop
            fpylint_log.seek(0)
            for line in fpylint_log:
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
                if count >= MAX_LOG_LINES:
                    build._log(
                        'pylint_script', 'pylint have more than %d '
                        'errors. '
                        'Please check pylint full log file...' % MAX_LOG_LINES)
                    break
            if build.result == "ok":
                build.write({'result': 'warn'})
        return res
