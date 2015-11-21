# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import time
import sys

import openerp
from openerp import fields, models
from openerp.addons.runbot_build_instructions.runbot_build \
    import MAGIC_PID_RUN_NEXT_JOB
from openerp.addons.runbot.runbot import (
    grep, rfind, run, _re_error, _re_warning)

from travis2docker.git_run import GitRun
from travis2docker.travis2docker import main as t2d

_logger = logging.getLogger(__name__)


def custom_build(func):
    # TODO: Make this method more generic for re-use in all custom modules
    """Decorator for functions which should be overwritten only if
    is_travis2docker_build is enabled in repo.
    """
    def custom_func(self, cr, uid, ids, context=None):
        args = [
            ('id', 'in', ids),
            ('branch_id.repo_id.is_travis2docker_build', '=', True)
        ]
        custom_ids = self.search(cr, uid, args, context=context)
        regular_ids = list(set(ids) - set(custom_ids))
        ret = None
        if regular_ids:
            regular_func = getattr(super(RunbotBuild, self), func.func_name)
            ret = regular_func(cr, uid, regular_ids, context=context)
        if custom_ids:
            assert ret is None
            ret = func(self, cr, uid, custom_ids, context=context)
        return ret
    return custom_func


class RunbotBuild(models.Model):
    _inherit = 'runbot.build'

    dockerfile_path = fields.Char()
    docker_image = fields.Char()
    docker_container = fields.Char()

    def get_docker_image(self, cr, uid, build, context=None):
        git_obj = GitRun(build.repo_id.name, '')
        image_name = git_obj.owner + '-' + git_obj.repo + ':' + \
            build.name[:7] + '_' + os.path.basename(build.dockerfile_path)
        return image_name.lower()

    def get_docker_container(self, cr, uid, build, context=None):
        return "build_%d" % (build.sequence)

    def job_10_test_base(self, cr, uid, build, lock_path, log_path):
        'Build docker image'
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self).job_10_test_base(
                cr, uid, build, lock_path, log_path)
        if not build.docker_image or not build.dockerfile_path \
                or build.result == 'skipped':
            _logger.info('docker build skipping job_10_test_base')
            return MAGIC_PID_RUN_NEXT_JOB
        cmd = [
            'docker', 'build',
            "--no-cache",
            "-t", build.docker_image,
            build.dockerfile_path,
        ]
        return self.spawn(cmd, lock_path, log_path)

    def job_20_test_all(self, cr, uid, build, lock_path, log_path):
        'create docker container'
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self).job_20_test_all(
                cr, uid, build, lock_path, log_path)
        if not build.docker_image or not build.dockerfile_path \
                or build.result == 'skipped':
            _logger.info('docker build skipping job_20_test_all')
            return MAGIC_PID_RUN_NEXT_JOB
        run(['docker', 'rm', '-f', build.docker_container])
        cmd = [
            'docker', 'run', '-e', 'INSTANCE_ALIVE=1',
            '-e', 'RUNBOT=1',
            '-p', '%d:%d' % (build.port, 8069),
            '--name=' + build.docker_container, '-t',
            build.docker_image,
        ]
        return self.spawn(cmd, lock_path, log_path)

    def job_30_run(self, cr, uid, build, lock_path, log_path):
        'Run docker container with odoo server started'
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self).job_30_run(
                cr, uid, build, lock_path, log_path)
        if not build.docker_image or not build.dockerfile_path \
                or build.result == 'skipped':
            _logger.info('docker build skipping job_30_run')
            return MAGIC_PID_RUN_NEXT_JOB

        # Start copy and paste from original method (fix flake8)
        log_all = build.path('logs', 'job_20_test_all.txt')
        log_time = time.localtime(os.path.getmtime(log_all))
        v = {
            'job_end': time.strftime(
                openerp.tools.DEFAULT_SERVER_DATETIME_FORMAT, log_time),
        }
        if grep(log_all, ".modules.loading: Modules loaded."):
            if rfind(log_all, _re_error):
                v['result'] = "ko"
            elif rfind(log_all, _re_warning):
                v['result'] = "warn"
            elif not grep(
                build.server("test/common.py"), "post_install") or grep(
                    log_all, "Initiating shutdown."):
                v['result'] = "ok"
        else:
            v['result'] = "ko"
        build.write(v)
        build.github_status()
        # end copy and paste from original method

        cmd = ['docker', 'start', '-i', build.docker_container]
        return self.spawn(cmd, lock_path, log_path)

    @custom_build
    def checkout(self, cr, uid, ids, context=None):
        """Save travis2docker output"""
        to_be_skipped_ids = ids
        for build in self.browse(cr, uid, ids, context=context):
            branch_short_name = build.branch_id.name.replace(
                'refs/heads/', '', 1).replace('refs/pull/', 'pull/', 1)
            t2d_path = os.path.join(build.repo_id.root(), 'travis2docker')
            sys.argv = [
                'travisfile2dockerfile', build.repo_id.name,
                branch_short_name, '--root-path=' + t2d_path]
            try:
                path_scripts = t2d()
            except BaseException:  # TODO: Add custom exception to t2d
                path_scripts = []
            for path_script in path_scripts:
                df_content = open(os.path.join(
                    path_script, 'Dockerfile')).read()
                if 'ENV TESTS=1' in df_content:
                    build.dockerfile_path = path_script
                    build.docker_image = self.get_docker_image(cr, uid, build)
                    build.docker_container = self.get_docker_container(
                        cr, uid, build)
                    if build.id in to_be_skipped_ids:
                        to_be_skipped_ids.remove(build.id)
                    break
        if to_be_skipped_ids:
            _logger.info('Dockerfile without TESTS=1 env. '
                         'Skipping builds %s', to_be_skipped_ids)
            self.skip(cr, uid, to_be_skipped_ids, context=context)

    @custom_build
    def cleanup(self, cr, uid, ids, context=None):
        for build in self.browse(cr, uid, ids, context=context):
            if build.docker_container:
                run(['docker', 'rm', '-f', build.docker_container])
                run(['docker', 'rmi', '-f', build.docker_image])
