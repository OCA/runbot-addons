# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Allow old api because is based original methods are old api from odoo
# pylint: disable=old-api7-method-defined

import logging
import os
import requests
import subprocess
import time
import sys

from odoo import fields, models
from odoo.tools import config
from odoo.addons.runbot.common import grep, rfind, time2str
from odoo.addons.runbot.models.build import _re_error, _re_warning

try:
    from travis2docker.git_run import GitRun
except ImportError:
    GitRun = None
try:
    from travis2docker.cli import main as t2d
except ImportError:
    t2d = None

_logger = logging.getLogger(__name__)

MAGIC_PID_RUN_NEXT_JOB = -2


class RunbotBuild(models.Model):
    _inherit = 'runbot.build'

    dockerfile_path = fields.Char()
    docker_image = fields.Char()
    docker_container = fields.Char()
    uses_weblate = fields.Boolean(help='Synchronize with weblate', copy=False)
    docker_executed_commands = fields.Boolean(
        help='True: Executed "docker exec CONTAINER_BUILD custom_commands"',
        readonly=True, copy=False)

    def _get_docker_image(self):
        self.ensure_one()
        git_obj = GitRun(self.repo_id.name, '')
        image_name = git_obj.owner + '-' + git_obj.repo + ':' + \
            self.name[:7] + '_' + os.path.basename(self.dockerfile_path)
        return image_name.lower()

    def _get_docker_container(self):
        self.ensure_one()
        return "build_%d" % (self.sequence)

    def _job_10_test_base(self, build, lock_path, log_path):
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self)._job_10_test_base(
                build, lock_path, log_path)
        build._log('test_base', 'Start test base module runbot_travis2docker')
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
        return self._spawn(cmd, lock_path, log_path, cpu_limit=1200)

    def _job_20_test_all(self, build, lock_path, log_path):
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self)._job_20_test_all(
                build, lock_path, log_path)
        if not build.docker_image or not build.dockerfile_path \
                or build.result == 'skipped':
            _logger.info('docker build skipping job_20_test_all')
            return MAGIC_PID_RUN_NEXT_JOB
        subprocess.call(['docker', 'rm', '-vf', build.docker_container])
        return self._spawn(
            build._get_run_cmd(), lock_path, log_path, cpu_limit=1200,
        )

    def _job_21_coverage(self, build, lock_path, log_path):
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self)._job_21_coverage(
                build, lock_path, log_path)
        _logger.info('docker build skipping job_21_coverage')
        return MAGIC_PID_RUN_NEXT_JOB

    def _job_30_run(self, build, lock_path, log_path):
        if not build.branch_id.repo_id.is_travis2docker_build:
            return super(RunbotBuild, self)._job_30_run(
                build, lock_path, log_path)
        if (not build.docker_image or not build.dockerfile_path or
                build.result == 'skipped'):
            _logger.info('docker build skipping job_30_run')
            return MAGIC_PID_RUN_NEXT_JOB

        # Start copy and paste from original method (fix flake8)
        build._log('run', 'Start running build %s' % build.dest)
        log_all = build._path('logs', 'job_20_test_all.txt')
        log_time = time.localtime(os.path.getmtime(log_all))
        v = {
            'job_end': time2str(log_time),
        }
        if grep(log_all, ".modules.loading: Modules loaded."):
            if rfind(log_all, _re_error):
                v['result'] = "ko"
            elif rfind(log_all, _re_warning):
                v['result'] = "warn"
            elif not grep(build._server("test/common.py"), "post_install") or \
                    grep(log_all, "Initiating shutdown."):
                v['result'] = "ok"
        else:
            v['result'] = "ko"
        build.write(v)
        build._github_status()
        # end copy and paste from original method

        cmd = ['docker', 'start', '-i', build.docker_container]
        return self._spawn(cmd, lock_path, log_path, cpu_limit=None)

    def _checkout(self):
        builds = self.filtered('branch_id.repo_id.is_travis2docker_build')
        super(RunbotBuild, self - builds)._checkout()
        to_be_skipped_ids = builds
        for build in builds:
            branch_short_name = build.branch_id.name.replace(
                'refs/heads/', '', 1).replace('refs/pull/', 'pull/', 1)
            t2d_path = os.path.join(build.repo_id._root(), 'travis2docker')
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
                '--docker-image=%s' % build.repo_id.travis2docker_image,
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
                    build.docker_image = build._get_docker_image()
                    build.docker_container = build._get_docker_container()
                    if build in to_be_skipped_ids:
                        to_be_skipped_ids -= build
                    break
        if to_be_skipped_ids:
            _logger.info('Dockerfile without TESTS=1 env. '
                         'Skipping builds %s', to_be_skipped_ids.ids)
            to_be_skipped_ids._skip()

    def _local_cleanup(self):
        builds = self.filtered('branch_id.repo_id.is_travis2docker_build')
        super(RunbotBuild, self - builds)._local_cleanup()
        for build in builds:
            if build.docker_container:
                subprocess.call(['docker', 'rm', '-f', build.docker_container])
                subprocess.call(['docker', 'rmi', '-f', build.docker_image])

    def _get_ssh_keys(self):
        self.ensure_one()
        response = self.repo_id._github(
            "/repos/:owner/:repo/commits/%s" % self.name, ignore_errors=True)
        if not response:
            return
        keys = ""
        for own_key in ['author', 'committer']:
            try:
                ssh_rsa = self.repo_id._github('/users/%(login)s/keys' %
                                               response[own_key])
                keys += '\n' + '\n'.join(rsa['key'] for rsa in ssh_rsa)
            except (TypeError, KeyError, requests.RequestException):
                _logger.debug("Error fetching %s", own_key)
        return keys

    def _schedule(self):
        res = super(RunbotBuild, self)._schedule()
        for build in self:
            if not all([build.state == 'running', build.job == 'job_30_run',
                        not build.docker_executed_commands,
                        build.repo_id.is_travis2docker_build]):
                continue
            time.sleep(10)
            build.docker_executed_commands = True
            subprocess.call([
                'docker', 'exec', '-d', '--user', 'root',
                build.docker_container, '/etc/init.d/ssh', 'start'])
            ssh_keys = self._get_ssh_keys() or ''
            f_extra_keys = os.path.expanduser('~/.ssh/runbot_authorized_keys')
            if os.path.isfile(f_extra_keys):
                with open(f_extra_keys) as fobj_extra_keys:
                    ssh_keys += "\n" + fobj_extra_keys.read()
            ssh_keys = ssh_keys.strip(" \n")
            if ssh_keys:
                subprocess.call([
                    'docker', 'exec', '-d', '--user', 'odoo',
                    build.docker_container,
                    "bash", "-c", "echo '%(keys)s' | tee -a '%(dir)s'" % dict(
                        keys=ssh_keys, dir="/home/odoo/.ssh/authorized_keys"),
                ])
        return res

    def _get_run_cmd(self):
        """Returns the docker run command for this build.

        Use this in child modules to append to the command sent to Odoo.
        """
        self.ensure_one()

        pr_cmd_env = [
            '-e', 'TRAVIS_PULL_REQUEST=' +
            self.branch_id.branch_name,
            '-e', 'CI_PULL_REQUEST=' + self.branch_id.branch_name,
        ] if 'refs/pull/' in self.branch_id.name else [
            '-e', 'TRAVIS_PULL_REQUEST=false',
        ]
        travis_branch = self._get_closest_branch_name(
            self.repo_id.id
        )[1].split('/')[-1]
        wl_cmd_env = []
        if self.uses_weblate and 'refs/pull' not in self.branch_id.name:
            wl_cmd_env.extend([
                '-e', 'WEBLATE=1',
                '-e', ('WEBLATE_TOKEN=%s' %
                       self.branch_id.repo_id.weblate_token),
                '-e', ('WEBLATE_HOST=%s' %
                       self.branch_id.repo_id.weblate_url),
                '-e', ('WEBLATE_SSH=%s' %
                       self.branch_id.repo_id.weblate_ssh)])
            if self.branch_id.repo_id.weblate_languages:
                wl_cmd_env.extend([
                    '-e', 'LANG_ALLOWED=%s' %
                    self.branch_id.repo_id.weblate_languages
                ])
            if self.branch_id.repo_id.token:
                wl_cmd_env.extend([
                    '-e', 'GITHUB_TOKEN=%s' % self.branch_id.repo_id.token])
        cmd = [
            'docker', 'run',
            '-e', 'INSTANCE_ALIVE=1',
            '-e', 'TRAVIS_BRANCH=' + travis_branch,
            '-e', 'TRAVIS_COMMIT=' + self.name,
            '-e', 'RUNBOT=1',
            '-e', 'UNBUFFER=0',
            '-e', 'START_SSH=1',
            '-e', 'TEST_ENABLE=%d' % (
                not self.repo_id.travis2docker_test_disable),
            '-p', '%d:%d' % (self.port, 8069),
            '-p', '%d:%d' % (self.port + 1, 22),
        ] + pr_cmd_env + wl_cmd_env
        cmd.extend(['--name=' + self.docker_container, '-t',
                    self.docker_image])
        logdb = self.env.cr.dbname
        if config['db_host'] and not travis_branch.startswith('7.0'):
            logdb = 'postgres://%s:%s@%s/%s' % (
                config['db_user'], config['db_password'],
                config['db_host'], self.env.cr.dbname,
            )
        cmd += ['-e', 'SERVER_OPTIONS="--log-db=%s"' % logdb]

        return cmd

    def _get_run_extra(self):
        """Use this in child modules to append into the run arguments.

        Returns:
            list: Additional arguments to add into docker run command.
        """
        return []
