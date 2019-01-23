# Copyright 2017-2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import glob
import os
import requests
import shutil
import subprocess
import tempfile
try:
    from anybox.recipe.odoo.base import BaseRecipe
    from zc.buildout.buildout import Buildout
except ImportError:
    BaseRecipe = object
    Buildout = object
from multiprocessing import Process
from odoo import api, fields, models
from odoo.addons.runbot.common import lock, grep


MAGIC_PID_RUN_NEXT_JOB = -2


class RunbotBuild(models.Model):
    _inherit = 'runbot.build'

    buildout_section = fields.Char(
        compute=lambda self: [
            this.update({
                'buildout_section':
                this.branch_id.buildout_section or
                this.branch_id.repo_id.buildout_section
            })
            for this in self
        ],
    )

    @api.multi
    def _server(self, *l, **kw):
        self.ensure_one()
        if not self.repo_id.uses_buildout:
            return super(RunbotBuild, self)._server(*l, **kw)
        odoo_part = 'parts/%s' % self.buildout_section
        if os.path.exists(self._path(odoo_part, 'odoo')):
            return self._path(odoo_part, 'odoo', *l, **kw)
        return self._path(odoo_part, 'openerp', *l, **kw)

    @api.multi
    def _cmd(self):
        self.ensure_one()
        if self.repo_id.uses_buildout:
            if not os.path.exists(self._path('datadir')):
                os.mkdir(self._path('datadir'))
            cmd = [
                self._path('bin/start_%s') % self.buildout_section,
                '--xmlrpc-port=%d' % self.port,
                '--data-dir', self._path('datadir'),
                '--addons-path', self._server('addons'),
            ]
            if grep(self._server('tools/config.py'), 'no-xmlrpcs'):
                cmd.append('--no-xmlrpcs')
            if grep(self._server('tools/config.py'), 'no-netrpc'):
                cmd.append('--no-netrpc')
            if grep(self._server('tools/config.py'), 'log-db'):
                cmd.append('--log-db=%s' % self.env.cr.dbname)
            return cmd, self.modules
        else:
            return super(RunbotBuild, self)._cmd()

    @api.model
    def _job_00_init(self, build, lock_path, log_path):
        if build.repo_id.uses_buildout and\
                not build.branch_id.buildout_version:
            # this is a normal code branch, find a working buildout
            # for it and build it
            build._github_status()
            buildout_build = build._get_buildout_build()
            if not buildout_build:
                return MAGIC_PID_RUN_NEXT_JOB
            build._log('buildout', 'Using buildout %s@%s' % (
                buildout_build.branch_id.name,
                buildout_build.name,
            ))
            return build._init_from_buildout(buildout_build)
        else:
            # for jobs not using buildout at all or for cloning
            # a branch containing a buildout
            return super(RunbotBuild, self)._job_00_init(
                build, lock_path, log_path
            )

    @api.model
    def _job_01_run_buildout(self, build, lock_path, log_path):
        # run this only for normal code branches in a buildout repo
        if not build.repo_id.uses_buildout or\
                build.branch_id.buildout_version:
            return MAGIC_PID_RUN_NEXT_JOB
        buildout_file = build._adapt_buildout()
        if not buildout_file:
            return MAGIC_PID_RUN_NEXT_JOB
        build._log('buildout', 'Running buildout')
        return build._spawn_buildout(
            [
                build._path('bin/buildout'), '-N', '-q',
                '-c', buildout_file,
            ],
            lock_path, log_path,
        )

    @api.model
    def _job_10_test_base(self, build, lock_path, log_path):
        if build.repo_id.uses_buildout:
            if build.branch_id.buildout_version:
                return build._bootstrap_buildout(lock_path, log_path)
            if not self._check_buildout_success(build):
                build.write({
                    'state': 'done',
                })
                build._log(
                    'buildout',
                    open(build._path('logs', 'job_01_run_buildout.txt')).read()
                )
                return MAGIC_PID_RUN_NEXT_JOB
            available_modules = []
            repo_modules = []
            parts_path = build._get_buildout_parts_path()
            # move modules from buildout repos
            for manifest in ['__openerp__.py', '__manifest__.py']:
                for module in glob.glob(
                    build._path('parts', '*', '*', manifest)
                ) + glob.glob(build._server('..', 'addons', '*', manifest)):
                    dirname = os.path.dirname(module)
                    basename = os.path.basename(dirname)
                    if os.path.exists(build._server('addons', basename)):
                        build._log(
                            'Building environment',
                            'Duplicate module "%s"' % basename
                        )
                        shutil.rmtree(
                            build._server('addons', basename),
                            ignore_errors=True
                        )
                    shutil.move(dirname, build._server('addons'))
                    available_modules.append(basename)
                    if '/%s/' % parts_path in dirname:
                        repo_modules.append(basename)
            explicit_modules = (
                (build.branch_id.modules or '') + ',' +
                (build.repo_id.modules or '')
            )
            explicit_modules = set(filter(None, explicit_modules.split(',')))
            if build.repo_id.modules_auto == 'all':
                modules_to_test = set(available_modules)
            elif build.repo_id.modules_auto == 'repo':
                modules_to_test = set(repo_modules)
            else:
                modules_to_test = set(explicit_modules)

            build.write({
                'modules': ','.join(self._filter_modules(
                    modules_to_test, available_modules, explicit_modules,
                )),
            })
        return super(RunbotBuild, self)._job_10_test_base(
            build, lock_path, log_path
        )

    @api.model
    def _job_20_test_all(self, build, lock_path, log_path):
        if build.repo_id.uses_buildout and build.branch_id.buildout_version:
            build._log('buildout', 'Running buildout')
            return build._spawn_buildout(
                [build._path('bin/buildout'), '-N', '-q'],
                lock_path, log_path
            )
        return super(RunbotBuild, self)._job_20_test_all(
            build, lock_path, log_path
        )

    @api.model
    def _job_30_run(self, build, lock_path, log_path):
        if build.repo_id.uses_buildout and build.branch_id.buildout_version:
            if self._check_buildout_success(build):
                build.write({'result': 'ok'})
                return self._spawn(
                    'for part in %s/*; do git -C $part repack -a --threads=1; '
                    'done' % (
                        build._path('parts')
                    ), lock_path, log_path, shell=True,
                    env=build._get_buildout_environment(),
                )
            return MAGIC_PID_RUN_NEXT_JOB
        return super(RunbotBuild, self)._job_30_run(
            build, lock_path, log_path
        )

    @api.model
    def _check_buildout_success(self, build):
        result = None
        if os.path.exists(
            build._path('bin/start_%s') % build.buildout_section
        ):
            build._log('buildout', 'Buildout succeeded')
            result = True
        else:
            build._log('buildout', 'Buildout failed')
            build.write({'result': 'ko'})
            result = False
        if not result:
            build._github_status()
        return result

    @api.multi
    def _spawn_buildout(self, cmd, lock_path, log_path):
        self.ensure_one()

        def preexec():
            os.setsid()
            os.closerange(3, os.sysconf("SC_OPEN_MAX"))
            lock(lock_path)

        with open(log_path, "w") as out:
            return subprocess.Popen(
                cmd, stdout=out, stderr=out, cwd=self._path(),
                preexec_fn=preexec, close_fds=False,
                env=self._get_buildout_environment(),
            ).pid

    @api.multi
    def _bootstrap_buildout(self, lock_path, log_path, delete_server=True):
        self.ensure_one()
        if delete_server:
            # self.checkout creates this directory, this interferes with the
            # buildout.
            shutil.rmtree(
                self._path('parts', self.buildout_section),
                ignore_errors=True
            )
        bootstrap_file = self.env['ir.config_parameter'].get_param(
            'runbot_buildout.bootstrap_file', 'bootstrap.py',
        )
        if not os.path.exists(self._path(bootstrap_file)):
            with open(self._path(bootstrap_file), 'w') as bootstrap:
                bootstrap.write(
                    requests.get(
                        'https://raw.githubusercontent.com/buildout/buildout/'
                        'master/bootstrap/bootstrap.py'
                    ).text
                )
        self._log('buildout', 'Bootstrapping buildout')
        return self._spawn(
            [
                self.branch_id.get_interpreter(),
                self._path(bootstrap_file),
                '-c', self._path('buildout.cfg'),
                '--allow-site-packages',
                '--setuptools-version=39.2.0',
                '--buildout-version=2.12.1',
            ],
            lock_path, log_path
        )

    @api.multi
    def _get_buildout_environment(self):
        self.ensure_one()
        build_environment = dict(os.environ)
        previous_build = self.search([
            ('state', '=', 'done'),
            ('result', '=', 'ok'),
            ('branch_id', '=', self.branch_id.id),
            ('id', '!=', self.id),
        ], order='create_date desc', limit=1)
        if previous_build:
            build_environment['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = ':'.join([
                ':'.join(glob.glob(
                    previous_build._path('parts', '*', '.git', 'objects')
                )),
                build_environment.get('GIT_ALTERNATE_OBJECT_DIRECTORIES', ''),
            ])
        return build_environment

    @api.multi
    def _get_buildout_build(self):
        self.ensure_one()
        buildout_branch = self.branch_id.buildout_branch_id
        version = None
        if not buildout_branch:
            pi = self.branch_id._get_pull_info()
            version = (
                pi and pi['base']['ref'] or self.branch_id.name
            ).split('/')[-1].split('-')[0]
            buildout_branch = self.env['runbot.branch'].search([
                ('repo_id', '=', self.repo_id.id),
                ('buildout_version', '=', version),
            ], order='buildout_default desc, name asc')
            if buildout_branch.filtered('buildout_default'):
                buildout_branch = buildout_branch.filtered('buildout_default')
        buildout_build = self.search([
            ('repo_id', '=', self.repo_id.id),
            ('state', '=', 'done'),
            ('result', '=', 'ok'),
            ('branch_id', 'in', buildout_branch.ids),
        ], order='create_date desc', limit=1)
        if not buildout_build:
            self._log(
                'buildout',
                'No working buildout branch found for %s in %s!' % (
                    version, ', '.join(buildout_branch.mapped('branch_name')),
                )
            )
            self.write({
                'state': 'done',
                'result': 'ko',
            })
            self._github_status()
        return buildout_build

    @api.multi
    def _init_from_buildout(self, buildout_build):
        self.ensure_one()
        if os.path.isdir(self._path()):
            shutil.rmtree(self._path(), ignore_errors=True)
        if not os.path.isdir(buildout_build._path()):
            self._log(
                'buildout',
                'Buildout directory %s does not exist' % buildout_build._path()
            )
            return MAGIC_PID_RUN_NEXT_JOB
        self._log(
            'buildout', 'Copying buildout from %s' % buildout_build._path()
        )

        def do_copy(buildout_path, own_path):
            shutil.copytree(buildout_path, own_path, symlinks=True)
            # we don't care about the logs created during the build of the
            # buildout
            shutil.rmtree(os.path.join(own_path, 'logs'), ignore_errors=True)
            os.makedirs(os.path.join(own_path, 'logs'))

        process = Process(
            target=do_copy, args=(buildout_build._path(), self._path()),
        )
        process.run()
        return process.pid

    @api.multi
    def _get_buildout_source_item(self):
        self.ensure_one()
        # the recipe switches working directory
        cwd = os.getcwd()
        buildout = Buildout(self._path('buildout.cfg'), [])
        section = buildout[self.buildout_section]
        recipe = BaseRecipe(buildout, 'buildout', section)
        recipe.parse_addons(section)
        os.chdir(cwd)

        for parts_dir, (loc_type, loc_spec, options) in recipe.sources.items():
            # we only support git urls
            if loc_type != 'git':
                continue
            # urls on github and gitlab aren't case sensitive
            normalized_name = self.repo_id.base.lower()
            normalized_location = self.env['runbot.repo'].new({
                'name': loc_spec[0],
            }).base.lower()
            if normalized_name == normalized_location:
                return parts_dir, (loc_type, loc_spec, options)

    @api.multi
    def _get_buildout_parts_path(self):
        item = self._get_buildout_source_item()
        if item:
            return item[0]

    @api.multi
    def _adapt_buildout(self):
        self.ensure_one()

        path = self._get_buildout_source_item()

        if not path:
            self._log(
                'buildout', 'No addons line found for %s' % self.repo_id.name,
            )
            self.write({
                'state': 'done',
                'result': 'ko',
            })
            self._github_status()
            return False
        else:
            path, dummy = path

        with tempfile.NamedTemporaryFile(
                prefix='buildout', suffix='.cfg', dir=self._path(),
                delete=False,
        ) as buildout_file:
            buildout_file.write(bytes(
                '[buildout]\n'
                'extends = %(buildout_cfg)s\n'
                '[%(buildout_section)s]\n'
                'vcs-revert = on-merge\n'
                'vcs-clear-retry = True\n'
                # we overwrite addons and merges because this happened already
                # now we just want to merge our branch into the main branch,
                # buildout will leave the rest of the parts directory alone
                'version = local parts/%(buildout_section)s\n'
                'addons =\n'
                '    local %(path)s\n'
                'merges =\n'
                '    git %(target_repo)s %(path)s %(target_commit)s\n'
                'options.logfile = False\n'
                'options.log_level = info\n'
                'options.log_handler = :INFO\n'
                'options.workers = 0\n'
                'options.without_demo = False\n'
                'options.data_dir = %(datadir)s\n'
                'options.dbfilter = %(dbfilter)s\n'
                'options.load_language = en_US' % dict(
                    buildout_cfg=self._path('buildout.cfg'),
                    buildout_section=self.buildout_section,
                    target_repo=self.repo_id.name,
                    target_commit=self.name,
                    path=path,
                    datadir=self._path('datadir'),
                    dbfilter=self.dest,
                ),
                'utf8',
            ))
        return buildout_file.name

    @api.multi
    def _local_cleanup(self):
        # super will rm the branch's checkout from the file system if the build
        # is older than a week. We can't have that for the first build of a
        # buildout branch
        for branch in self.env['runbot.branch'].search([
                ('buildout_version', '!=', False),
        ]):
            self.search(
                [
                    ('branch_id', '=', branch.id),
                    ('state', '=', 'done'),
                    ('result', '=', 'ok'),
                ],
                order='create_date desc', limit=1
            ).write({
                'job_end': fields.Datetime.now(),
            })
        return super(RunbotBuild, self)._local_cleanup()
