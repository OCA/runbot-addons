# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import glob
import os
import shutil
import subprocess
import sys
import tempfile
from openerp import api, fields, models
from openerp.tools import file_open
from openerp.addons.runbot.runbot import lock, grep


class RunbotBuild(models.Model):
    _inherit = 'runbot.build'

    @api.multi
    def server(self, *parts):
        for this in self:
            if this.repo_id.uses_buildout:
                odoo_part = 'parts/%s' % this.repo_id.buildout_section
                if os.path.exists(this.path(odoo_part, 'odoo')):
                    return this.path(odoo_part, 'odoo', *parts)
                return this.path(odoo_part, 'openerp', *parts)
            else:
                return super(RunbotBuild, this).server(*parts)


    @api.multi
    def cmd(self):
        for this in self:
            if this.repo_id.uses_buildout:
                if not os.path.exists(this.path('datadir')):
                    os.mkdir(this.path('datadir'))
                cmd = [
                    sys.executable,
                    this.path('bin/start_%s') % this.repo_id.buildout_section,
                    '--xmlrpc-port=%d' % this.port,
                    '--data-dir', this.path('datadir'),
                    '--addons-path', this.server('addons'),
                ]
                if grep(this.server('tools/config.py'), 'no-xmlrpcs'):
                    cmd.append('--no-xmlrpcs')
                if grep(this.server('tools/config.py'), 'no-netrpc'):
                    cmd.append('--no-netrpc')
                if grep(this.server('tools/config.py'), 'log-db'):
                    cmd.append('--log-db=%s' % self.env.cr.dbname)
                return cmd, this.modules
            else:
                return super(RunbotBuild, this).cmd()

    @api.model
    def job_00_init(self, build, lock_path, log_path):
        if build.repo_id.uses_buildout and\
                not build.branch_id.buildout_version:
            build.github_status()
            buildout_build = build._get_buildout_build()
            if not buildout_build:
                return -2
            build._log('buildout', 'Using buildout %s@%s' % (
                buildout_build.branch_id.name,
                buildout_build.name,
            ))
            if not build._init_from_buildout(buildout_build):
                return -2
            buildout_file = build._adapt_buildout()
            if not buildout_file:
                return -2
            build._log('buildout', 'Running buildout')
            return build._spawn_buildout(
                [build.path('bin/buildout'), '-N', '-q', '-c', buildout_file],
                lock_path, log_path,
            )
        else:
            return super(RunbotBuild, self).job_00_init(
                build, lock_path, log_path
            )

    @api.model
    def job_10_test_base(self, build, lock_path, log_path):
        if build.repo_id.uses_buildout:
            if build.branch_id.buildout_version:
                return build._bootstrap_buildout(lock_path, log_path)
            available_modules = []
            # move modules from buildout repos
            for manifest in ['__openerp__.py', '__manifest__.py']:
                for module in glob.glob(
                    build.path('parts', '*', '*', manifest)
                ) + glob.glob(build.server('..', 'addons', '*', manifest)):
                    dirname = os.path.dirname(module)
                    basename = os.path.basename(dirname)
                    if os.path.exists(build.server('addons', basename)):
                        build._log(
                            'Building environment',
                            'Duplicate module "%s"' % basename
                        )
                        shutil.rmtree(
                            build.server('addons', basename),
                            ignore_errors=True
                        )
                    shutil.move(dirname, build.server('addons'))
                    available_modules.append(basename)
            modules_to_test = (
                (build.branch_id.modules or '') + ',' +
                (build.repo_id.modules or '')
            )
            modules_to_test = filter(None, modules_to_test.split(','))
            explicit_modules = set(modules_to_test)
            if build.repo_id.modules_auto == 'all':
                modules_to_test += available_modules

            build.write({
                'modules': ','.join(self.filter_modules(
                    modules_to_test, set(available_modules), explicit_modules,
                ))
            })
        return super(RunbotBuild, self).job_10_test_base(
            build, lock_path, log_path
        )

    @api.model
    def job_20_test_all(self, build, lock_path, log_path):
        if build.repo_id.uses_buildout and build.branch_id.buildout_version:
            build._log('buildout', 'Running buildout')
            return build._spawn_buildout(
                [build.path('bin/buildout'), '-N', '-q'],
                lock_path, log_path
            )
        return super(RunbotBuild, self).job_20_test_all(
            build, lock_path, log_path
        )

    @api.model
    def job_30_run(self, build, lock_path, log_path):
        if build.repo_id.uses_buildout and build.branch_id.buildout_version:
            if os.path.exists(
                build.path('bin/start_%s') % build.repo_id.buildout_section
            ):
                build._log('buildout', 'Buildout succeeded')
                build.write({'result': 'ok'})
            else:
                build._log('buildout', 'Buildout failed')
                build.write({'result': 'ko'})
            build.github_status()
            return -2
        return super(RunbotBuild, self).job_30_run(
            build, lock_path, log_path
        )

    @api.multi
    def _spawn_buildout(self, cmd, lock_path, log_path):
        self.ensure_one()
        out = open(log_path, "w")

        def preexec():
            os.setsid()
            os.closerange(3, os.sysconf("SC_OPEN_MAX"))
            lock(lock_path)

        return subprocess.Popen(
            [sys.executable] + cmd, stdout=out, stderr=out, cwd=self.path(),
            preexec_fn=preexec,
        ).pid

    @api.multi
    def _bootstrap_buildout(self, lock_path, log_path, delete_server=True):
        self.ensure_one()
        if delete_server:
            # self.checkout creates this directory, this interferes with the
            # buildout.
            shutil.rmtree(
                self.path('parts', self.repo_id.buildout_section),
                ignore_errors=True
            )
        # TODO: if this doesn't exist, download one
        self._log('buildout', 'Bootstrapping buildout')
        return self.spawn(
            [
                sys.executable, self.path('bootstrap.py'),
                # TODO: make this configurable
                '-c', self.path('buildout.cfg'),
            ],
            lock_path, log_path
        )

    @api.multi
    def _get_buildout_build(self):
        self.ensure_one()
        version = self.branch_id.name.split('/')[-1].split('-')[0]
        buildout_branch = self.env['runbot.branch'].search([
            ('repo_id', '=', self.repo_id.id),
            ('buildout_version', '=', version),
        ], order='buildout_default desc, name asc', limit=1)
        buildout_build = self.search([
            ('repo_id', '=', self.repo_id.id),
            ('state', '=', 'done'),
            ('result', '=', 'ok'),
            ('branch_id', '=', buildout_branch.id),
        ], order='create_date desc', limit=1)
        if not buildout_build:
            self._log(
                'buildout',
                'No working buildout branch found for %s in %s!' % (
                    version, buildout_branch.branch_name,
                )
            )
            self.write({
                'state': 'done',
                'result': 'ko',
            })
            self.github_status()
        return buildout_build

    @api.multi
    def _init_from_buildout(self, buildout_build):
        self.ensure_one()
        if os.path.isdir(self.path()):
            shutil.rmtree(self.path(), ignore_errors=True)
        if not os.path.isdir(buildout_build.path()):
            self._log(
                'buildout',
                'Buildout directory %s does not exist' % buildout_build.path()
            )
            return False
        self._log(
            'buildout', 'Copying buildout from %s' % buildout_build.path()
        )
        shutil.copytree(buildout_build.path(), self.path(), symlinks=True)
        # we don't care about the logs created during the build of the
        # buildout
        shutil.rmtree(self.path('logs'), ignore_errors=True)
        os.makedirs(self.path('logs'))
        return True

    @api.multi
    def _adapt_buildout(self):
        adaption_script = file_open(
            'runbot_buildout/__scripts__/adapt_buildout.py'
        )
        adaption_script.close()
        try:
            adapted_buildout = subprocess.check_output([
                sys.executable,
                self.path(
                    'bin/python_%s' % self.repo_id.buildout_section
                ),
                adaption_script.name,
                self.path('buildout.cfg'),
                self.repo_id.buildout_section,
                self.repo_id.name,
                self.name,
            ], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exception:
            self._log('buildout', exception.output)
            self.write({
                'state': 'done',
                'result': 'ko',
            })
            self.github_status()
            return False
        buildout_file = tempfile.NamedTemporaryFile(
            prefix='buildout', suffix='.cfg', dir=self.path(), delete=False,
        )
        buildout_file.write(adapted_buildout)
        buildout_file.close()
        return buildout_file.name

    @api.multi
    def _local_cleanup(self):
        # super will rm the branch's checkout from the file system if the build
        # is older than a week. We can't have that for the first build of a
        # buildout branch
        for branch in self.env['runbot.branch'].search([
                ('buildout_version', '!=', False),
        ]):
            self.search([
                    ('branch_id', '=', branch.id),
                    ('state', '=', 'done'),
                    ('result', '=', 'ok'),
            ], limit=1).write({
                'job_end': fields.Datetime.now(),
            })
        return super(RunbotBuild, self)._local_cleanup()
