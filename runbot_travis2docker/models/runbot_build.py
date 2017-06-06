# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Allow old api because is based original methods are old api from odoo
# pylint: disable=old-api7-method-defined

import logging
import os
import requests
import time
import sys

import openerp
from openerp import fields, models
from openerp.tools import config
from openerp.addons.runbot_build_instructions.models.runbot_build \
    import MAGIC_PID_RUN_NEXT_JOB
from openerp.addons.runbot.runbot import (
    grep, rfind, run, _re_error, _re_warning)

try:
    from travis2docker.git_run import GitRun
except ImportError:
    GitRun = None
try:
    from travis2docker.cli import main as t2d
except ImportError:
    t2d = None

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
    uses_weblate = fields.Boolean(help='Synchronize with weblate', copy=False)
    docker_executed_commands = fields.Boolean(
        help='True: Executed "docker exec CONTAINER_BUILD custom_commands"',
        readonly=True, copy=False)

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
            "--no-cache", '--pull',
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
        run(['docker', 'rm', '-vf', build.docker_container])
        pr_cmd_env = [
            '-e', 'TRAVIS_PULL_REQUEST=' +
            build.branch_id.branch_name,
            '-e', 'CI_PULL_REQUEST=' + build.branch_id.branch_name,
        ] if 'refs/pull/' in build.branch_id.name else [
            '-e', 'TRAVIS_PULL_REQUEST=false',
        ]
        travis_branch = build._get_closest_branch_name(
            build.repo_id.id
        )[1].split('/')[-1]
        wl_cmd_env = []
        if build.uses_weblate and 'refs/pull' not in build.branch_id.name:
            wl_cmd_env.extend([
                '-e', 'WEBLATE=1',
                '-e', ('WEBLATE_TOKEN=%s' %
                       build.branch_id.repo_id.weblate_token),
                '-e', ('WEBLATE_HOST=%s' %
                       build.branch_id.repo_id.weblate_url)
            ])
            if build.branch_id.repo_id.weblate_languages:
                wl_cmd_env.extend([
                    '-e', 'LANG_ALLOWED=%s' %
                    build.branch_id.repo_id.weblate_languages
                ])
            if build.branch_id.repo_id.token:
                wl_cmd_env.extend([
                    '-e', 'GITHUB_TOKEN=%s' % build.branch_id.repo_id.token])
        cmd = [
            'docker', 'run',
            '-e', 'INSTANCE_ALIVE=1',
            '-e', 'TRAVIS_BRANCH=' + travis_branch,
            '-e', 'TRAVIS_COMMIT=' + build.name,
            '-e', 'RUNBOT=1',
            '-e', 'UNBUFFER=0',
            '-e', 'START_SSH=1',
            '-e', 'TEST_ENABLE=%d' % (
                not build.repo_id.travis2docker_test_disable),
            '-p', '%d:%d' % (build.port, 8069),
            '-p', '%d:%d' % (build.port + 1, 22),
        ] + pr_cmd_env + wl_cmd_env
        cmd.extend(['--name=' + build.docker_container, '-t',
                    build.docker_image])
        logdb = cr.dbname
        if config['db_host'] and not travis_branch.startswith('7.0'):
            logdb = 'postgres://%s:%s@%s/%s' % (
                config['db_user'], config['db_password'],
                config['db_host'], cr.dbname,
            )
        cmd += ['-e', 'SERVER_OPTIONS="--log-db=%s"' % logdb]
        return self.spawn(cmd, lock_path, log_path)

    def job_21_coverage(self, cr, uid, build, lock_path, log_path):
        if (not build.branch_id.repo_id.is_travis2docker_build and
                hasattr(super(RunbotBuild, self), 'job_21_coverage')):
            return super(RunbotBuild, self).job_21_coverage(
                cr, uid, build, lock_path, log_path)
        _logger.info('docker build skipping job_21_coverage')
        return MAGIC_PID_RUN_NEXT_JOB

    def job_30_run(self, cr, uid, build, lock_path, log_path):
        'Run docker container with odoo server started'
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self).job_30_run(
                cr, uid, build, lock_path, log_path)
        if (not build.docker_image or not build.dockerfile_path or
                build.result == 'skipped'):
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
            repo_name = build.repo_id.name
            if not any((repo_name.startswith('https://'),
                        repo_name.startswith('ssh://'),
                        repo_name.startswith('git@'),
                        )):
                repo_name = 'https://' + repo_name
            sys.argv = [
                'travisfile2dockerfile', repo_name,
                branch_short_name, '--root-path=' + t2d_path,
                '--exclude-after-success',
            ]
            try:
                path_scripts = t2d()
            except BaseException:  # TODO: Add custom exception to t2d
                path_scripts = []
            for path_script in path_scripts:
                df_content = open(os.path.join(
                    path_script, 'Dockerfile')).read()
                if ' TESTS=1' in df_content or ' TESTS="1"' in df_content or \
                        " TESTS='1'" in df_content:
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
    def _local_cleanup(self, cr, uid, ids, context=None):
        for build in self.browse(cr, uid, ids, context=context):
            if build.docker_container:
                run(['docker', 'rm', '-f', build.docker_container])
                run(['docker', 'rmi', '-f', build.docker_image])

    def get_ssh_keys(self, cr, uid, build, context=None):
        response = build.repo_id.github(
            "/repos/:owner/:repo/commits/%s" % build.name, ignore_errors=True)
        if not response:
            return
        keys = ""
        for own_key in ['author', 'committer']:
            try:
                ssh_rsa = build.repo_id.github('/users/%(login)s/keys' %
                                               response[own_key])
                keys += '\n' + '\n'.join(rsa['key'] for rsa in ssh_rsa)
            except (TypeError, KeyError, requests.RequestException):
                _logger.debug("Error fetching %s", own_key)
        return keys

    def schedule(self, cr, uid, ids, context=None):
        res = super(RunbotBuild, self).schedule(cr, uid, ids, context=context)
        for build in self.browse(cr, uid, ids, context=context):
            if not all([build.state == 'running', build.job == 'job_30_run',
                        not build.docker_executed_commands,
                        build.repo_id.is_travis2docker_build]):
                continue
            build.write({'docker_executed_commands': True})
            run(['docker', 'exec', '-d', '--user', 'root',
                 build.docker_container, '/etc/init.d/ssh', 'start'])
            ssh_keys = self.get_ssh_keys(cr, uid, build, context=context) or ''
            f_extra_keys = os.path.expanduser('~/.ssh/runbot_authorized_keys')
            if os.path.isfile(f_extra_keys):
                with open(f_extra_keys) as fobj_extra_keys:
                    ssh_keys += "\n" + fobj_extra_keys.read()
            ssh_keys = ssh_keys.strip(" \n")
            if ssh_keys:
                run(['docker', 'exec', '-d', '--user', 'odoo',
                     build.docker_container,
                     "bash", "-c", "echo '%(keys)s' | tee -a '%(dir)s'" % dict(
                         keys=ssh_keys, dir="/home/odoo/.ssh/authorized_keys"),
                     ])
        return res
