# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import inspect
import os
import shutil
from psycopg2.extensions import AsIs
from odoo import api, fields, models
from odoo.addons.runbot.common import local_pgadmin_cursor


class RunbotBuild(models.Model):
    _inherit = 'runbot.build'

    preseed_database = fields.Char(
        compute=lambda self: [
            this.update({
                'preseed_database':
                this.branch_id.preseed_database or
                this.branch_id.repo_id.preseed_database
            })
            for this in self
        ],
    )
    preseed_database_build_id = fields.Many2one(
        'runbot.build',
        compute=lambda self: [
            this.update({
                'preseed_database_build_id':
                this.branch_id.preseed_database_build_id or
                this.branch_id.repo_id.preseed_database_build_id
            })
            for this in self
        ],
    )
    preseed_repo_ids = fields.One2many(
        'runbot.repo', 'preseed_database_build_id',
    )
    preseed_branch_ids = fields.One2many(
        'runbot.branch', 'preseed_database_build_id',
    )

    def _job_00_init(self, build, lock_path, log_path):
        """Don't do a checkout for preseed builds"""
        if build.preseed_repo_ids or build.preseed_branch_ids:
            build._log('init', 'Skipping checkout for database refresh')
            build._github_status()
            return -2
        return super(RunbotBuild, self)._job_00_init(
            build, lock_path, log_path
        )

    def _job_10_test_base(self, build, lock_path, log_path):
        """No need for base tests for preseed builds"""
        if build.preseed_repo_ids or build.preseed_branch_ids:
            build._log('test_base', 'Skipping base test for database refresh')
            return -2
        return super(RunbotBuild, self)._job_10_test_base(
            build, lock_path, log_path
        )

    def _job_30_run(self, build, lock_path, log_path):
        """Don't run preseed builds, this locks the database"""
        if build.preseed_repo_ids or build.preseed_branch_ids:
            build._log('test_base', 'Skipping running preseed build')
            return -2
        return super(RunbotBuild, self)._job_30_run(
            build, lock_path, log_path
        )

    def _local_pg_createdb(self, dbname):
        """Use preseed database if applicable"""
        if dbname.endswith('-base'):
            # no need to do anything here
            return super(RunbotBuild, self)._local_pg_createdb(dbname)
        stack = inspect.stack()
        # there should be a build in the callee, don't recurse through stack
        build = stack[1][0].f_locals.get('build')
        if (
                isinstance(build, models.BaseModel) and
                build.preseed_database and
                build.preseed_database_build_id != build and
                (
                    not build.preseed_database_build_id or
                    build.preseed_database_build_id.state == 'done'
                )
        ):
            build._log(
                'init',
                'Using %s as database template' % build.preseed_database
            )
            with local_pgadmin_cursor() as cr:
                cr.execute(
                    'create database "%s" TEMPLATE "%s"',
                    (AsIs(dbname), AsIs(build.preseed_database)),
                )
            if build.preseed_database_build_id:
                # copy the build's filestore
                template_filestore = build.preseed_database_build_id._path(
                    os.path.join(
                        'datadir', 'filestore', build.preseed_database
                    )
                )
                build._log(
                    'init', 'Copying filestore from %s' % template_filestore
                )
                filestore = build._path(os.path.join('datadir', 'filestore'))
                os.makedirs(filestore, exist_ok=True)
                if os.path.exists(template_filestore):
                    shutil.copytree(template_filestore, os.path.join(
                        filestore, dbname
                    ))
        else:
            super(RunbotBuild, self)._local_pg_createdb(dbname)

    @api.multi
    def _local_cleanup(self):
        """Never clean up a preseed build"""
        preseed_builds = self.env['runbot.build'].search([
            '|',
            ('preseed_repo_ids', '!=', False),
            ('preseed_branch_ids', '!=', False),
        ])
        build2state = {build: build.state for build in preseed_builds}
        # super deletes builds in state done
        preseed_builds.write({'state': 'running'})
        super(RunbotBuild, self - preseed_builds)._local_cleanup()
        for build, state in build2state.items():
            build.write({'state': state})

    @api.multi
    def reset(self):
        self._reset_for_preseed()
        return super(RunbotBuild, self).reset()

    @api.multi
    def _reset_for_preseed(self):
        for this in self:
            repo_or_branch = this.preseed_branch_ids or this.preseed_repo_ids
            if not repo_or_branch:
                continue
            this.write({
                'modules': ','.join(
                    repo_or_branch.mapped('preseed_database_module_ids.name')
                ),
            })
            self.env['ir.logging'].search([
                ('build_id', '=', this.id),
            ]).unlink()
            this._reset()
