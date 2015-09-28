# coding: utf-8

import logging
import os
import sys

from openerp import fields, models
from openerp.addons.runbot_build_instructions.runbot_build \
    import MAGIC_PID_RUN_NEXT_JOB
from openerp.addons.runbot.runbot import run

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

    def get_docker_image(self, cr, uid, build, context=None):
        git_obj = GitRun(build.repo_id.name, '')
        image_name = git_obj.owner + '-' + git_obj.repo + ':' + \
            build.name[:7] + '_' + os.path.basename(build.dockerfile_path)
        return image_name.lower()

    def job_10_test_base(self, cr, uid, build, lock_path, log_path):
        'Build docker image'
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self).job_10_test_base(
                cr, uid, build, lock_path, log_path)
        cmd = [
            'docker', 'build', "--no-cache",
            "-t", build.docker_image,
            build.dockerfile_path
        ]
        return self.spawn(cmd, lock_path, log_path)

    def job_20_test_all(self, cr, uid, build, lock_path, log_path):
        'create docker container'
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self).job_20_test_all(
                cr, uid, build, lock_path, log_path)
        if not build.dockerfile_path:
            _logger.info(
                'skipping job_20_test_all: '
                'Dockerfile without TESTS=1 env')
            return MAGIC_PID_RUN_NEXT_JOB
        run(['docker', 'rm', '-f', '%d' % build.id])
        cmd = [
            'docker', 'run', '-e', 'INSTANCE_ALIVE=1',
            '-p', '%d:%d' % (build.port, 8069),
            '--name=%d' % (build.id), '-it', build.docker_image,
        ]
        # Todo: Add log path volume
        return self.spawn(cmd, lock_path, log_path)

    def job_30_run(self, cr, uid, build, lock_path, log_path):
        'Run docker container with odoo server started'
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self).job_30_run(
                cr, uid, build, lock_path, log_path)
        cmd = ['docker', 'start', '-i', '%d' % build.id]
        return self.spawn(cmd, lock_path, log_path)

    @custom_build
    def checkout(self, cr, uid, ids, context=None):
        """Save travis2docker output"""
        for build in self.browse(cr, uid, ids, context=context):
            branch_short_name = build.branch_id.name.replace(
                'refs/heads/', '', 1).replace('refs/pull/', 'pull/', 1)
            t2d_path = os.path.join(build.repo_id.root(), 'travis2docker')
            sys.argv = [
                'travisfile2dockerfile', build.repo_id.name,
                branch_short_name, '--root-path=' + t2d_path]
            path_scripts = t2d()
            for path_script in path_scripts:
                df_content = open(os.path.join(
                    path_script, 'Dockerfile')).read()
                if 'ENV TESTS=1' in df_content:
                    build.dockerfile_path = path_script
                    build.docker_image = self.get_docker_image(cr, uid, build)

    # TODO: Add custom_build to drop and kill
