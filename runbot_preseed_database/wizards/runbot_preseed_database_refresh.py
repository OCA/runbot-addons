# (c) 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import psycopg2
from psycopg2.extensions import AsIs
from odoo import api, fields, models
from odoo.addons.runbot.common import local_pgadmin_cursor
_logger = logging.getLogger(__name__)


class RunbotPreseedDatabaseRefresh(models.TransientModel):
    _name = 'runbot.preseed.database.refresh'
    _description = 'Database refresh wizard'

    repo_id = fields.Many2one('runbot.repo')
    branch_id = fields.Many2one('runbot.branch')
    build_id = fields.Many2one(
        'runbot.build', required=True, ondelete='cascade',
        domain=[('result', '=', 'ok'), ('status', '=', 'running')],
    )
    preseed_database = fields.Char(
        help='Fill in the name of a database to use as template for the all '
        'build', required=True,
    )
    preseed_database_module_ids = fields.Many2many(
        'runbot.preseed.database.module',
        relation='runbot_preseed_database_refresh_module',
        column1='wizard_id', column2='module_id',
        string='Modules to install',
    )

    @api.onchange('build_id')
    def onchange_build_id(self):
        self.preseed_database = '%s-all' % self.build_id.dest

    @api.model
    def default_get(self, fields_list):
        result = super(RunbotPreseedDatabaseRefresh, self).default_get(
            fields_list=fields_list,
        )
        repo_or_branch = self.env['runbot.repo']
        if self.env.context.get('active_model') == 'runbot.repo':
            result['repo_id'] = self.env.context.get('active_id')
            repo_or_branch = self.env['runbot.repo'].browse(result['repo_id'])
        if self.env.context.get('active_model') == 'runbot.branch':
            result['branch_id'] = self.env.context.get('active_id')
            repo_or_branch = self.env['runbot.branch'].browse(
                result['branch_id'],
            )
        if not repo_or_branch or not repo_or_branch.preseed_database:
            return result
        result.update(
            preseed_database=repo_or_branch.preseed_database,
            preseed_database_module_ids=self._get_module_x2many_commands(
                repo_or_branch.preseed_database,
            )
        )
        return result

    @api.multi
    def _get_module_x2many_commands(self, database):
        modules = []
        try:
            with psycopg2.connect('dbname=%s' % database) as connection:
                with connection.cursor() as cr:
                    cr.execute(
                        "select name from ir_module_module where state in %s",
                        (tuple(['installed', 'to upgrade']),),
                    )
                    modules = [module for module, in cr.fetchall()]
        except (psycopg2.ProgrammingError, psycopg2.OperationalError):
            # either database or modules table doesn't exist
            pass
        return [
            (
                4,
                self.env['runbot.preseed.database.module'].search([
                    ('name', '=', module),
                ]).id or self.env['runbot.preseed.database.module'].create({
                    'name': module
                }).id
            )
            for module in modules
            if module not in (self.build_id.modules or '').split(',')
        ]

    @api.multi
    def action_get_modules(self):
        self.ensure_one()
        modules = self._get_module_x2many_commands(
            '%s-all' % self.build_id.dest
        )
        if not modules:
            modules = self._get_module_x2many_commands(self.preseed_database)
        self.write({'preseed_database_module_ids': modules})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def action_write_result(self):
        self.ensure_one()
        repo_or_branch = self.repo_id or self.branch_id
        database = self.preseed_database
        # create empty database if necessary
        try:
            with psycopg2.connect('dbname=%s' % database):
                pass
        except psycopg2.OperationalError:
            with local_pgadmin_cursor() as cr:
                cr.execute(
                    'create database "%s" template template1',
                    (AsIs(database),),
                )

        repo_or_branch.write({
            'preseed_database': self.preseed_database,
            'preseed_database_module_ids': [
                (4, module.id)
                for module in self.preseed_database_module_ids
            ],
            'preseed_database_build_id': self.build_id.id,
        })
        self.build_id._reset()
        return {'type': 'ir.actions.act_window.close'}

    @api.model
    def _refresh_preseed_database(self):
        """Create a new preseed database for all configured branches/repos"""
        self.env['runbot.build'].search([
            '|',
            ('preseed_repo_ids', '!=', False),
            ('preseed_branch_ids', '!=', False),
        ])._reset_for_preseed()
