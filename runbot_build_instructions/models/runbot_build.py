# -*- encoding: utf-8 -*-
# Copyrigh 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import sys
import shutil

import openerp
from openerp.osv import orm, fields
from openerp.addons.runbot.runbot import mkdirs

_logger = logging.getLogger(__name__)
MAGIC_PID_RUN_NEXT_JOB = -2


def custom_build(func):
    """Decorator for functions which should be overwritten only if
    is_custom_build is enabled in repo.
    """
    def custom_func(self, cr, uid, ids, context=None):
        args = [
            ('id', 'in', ids),
            ('branch_id.repo_id.is_custom_build', '=', True)
        ]
        custom_ids = self.search(cr, uid, args, context=context)
        regular_ids = list(set(ids) - set(custom_ids))
        ret = None
        if regular_ids:
            regular_func = getattr(super(runbot_build, self), func.func_name)
            ret = regular_func(cr, uid, regular_ids, context=context)
        if custom_ids:
            assert ret is None
            ret = func(self, cr, uid, custom_ids, context=context)
        return ret
    return custom_func


class runbot_build(orm.Model):
    _inherit = "runbot.build"
    _columns = {
        'prebuilt': fields.boolean("Prebuilt"),
    }

    def job_00_init(self, cr, uid, build, lock_path, log_path):
        res = super(runbot_build, self).job_00_init(
            cr, uid, build, lock_path, log_path
        )
        if build.branch_id.repo_id.is_custom_build:
            build.pre_build(lock_path, log_path)
        build.prebuilt = True
        return res

    def job_10_test_base(self, cr, uid, build, lock_path, log_path):
        if build.branch_id.repo_id.skip_test_jobs:
            _logger.info('skipping job_10_test_base')
            return MAGIC_PID_RUN_NEXT_JOB
        else:
            return super(runbot_build, self).job_10_test_base(
                cr, uid, build, lock_path, log_path
            )

    def job_20_test_all(self, cr, uid, build, lock_path, log_path):
        if build.branch_id.repo_id.skip_test_jobs:
            _logger.info('skipping job_20_test_all')
            with open(log_path, 'w') as f:
                f.write('consider tests as passed: '
                        '.modules.loading: Modules loaded.')
            return MAGIC_PID_RUN_NEXT_JOB
        else:
            return super(runbot_build, self).job_20_test_all(
                cr, uid, build, lock_path, log_path
            )

    def sub_cmd(self, build, cmd):
        if not cmd:
            return []
        if isinstance(cmd, basestring):
            cmd = cmd.split()
        internal_vals = {
            'custom_build_dir': build.repo_id.custom_build_dir or '',
            'custom_server_path': build.repo_id.custom_server_path,
            'other_repo_path': build.repo_id.other_repo_id.path or '',
            'build_dest': build.dest,
        }
        return [i % internal_vals for i in cmd]

    def pre_build(self, cr, uid, ids, lock_path, log_path, context=None):
        """Run pre-build command if there is one
        Substitute path variables after splitting command to avoid problems
        with spaces in internal variables.
        Run command in build path to avoid relative path issues.
        """
        pushd = os.getcwd()
        try:
            for build in self.browse(cr, uid, ids, context=context):
                if build.prebuilt:
                    continue
                cmd = self.sub_cmd(build, build.repo_id.custom_pre_build_cmd)
                if not cmd:
                    continue
                os.chdir(build.path())
                self.spawn(cmd, lock_path, log_path)

        finally:
            os.chdir(pushd)

    @custom_build
    def checkout(self, cr, uid, ids, context=None):
        """Checkout in custom build directories if they are specified
        Do same as superclass except for git_export path.
        """
        for build in self.browse(cr, uid, ids, context=context):
            if build.prebuilt:
                continue
            # starts from scratch
            if os.path.isdir(build.path()):
                shutil.rmtree(build.path())

            # runbot log path
            mkdirs([build.path("logs")])

            # checkout branch
            build_path = build.path()
            custom_build_dir = build.repo_id.custom_build_dir
            if custom_build_dir:
                mkdirs([build.path(custom_build_dir)])
                build_path = os.path.join(build_path, custom_build_dir)
            build.repo_id.git_export(build.name, build_path)

    @custom_build
    def cmd(self, cr, uid, ids, context=None):
        """Get server start script from build config
        Overwrite superclass completely
        Specify database user in the case of custom config, to allow viewing
        after db has been created by Odoo (using current user).
        Disable multiworker
        """
        build = self.browse(cr, uid, ids[0], context=context)
        server_path = build.path(build.repo_id.custom_server_path)
        mods = build.repo_id.modules or "base"
        params = self.sub_cmd(build, build.repo_id.custom_server_params)
        # commandline
        cmd = [
            sys.executable,
            server_path,
            "--no-xmlrpcs",
            "--xmlrpc-port=%d" % build.port,
            "--db_user=%s" % openerp.tools.config['db_user'],
            "--workers=0",
        ] + params
        return cmd, mods
