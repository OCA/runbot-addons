# -*- encoding: utf-8 -*-
# Copyrigh 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import fields, models

_logger = logging.getLogger(__name__)

ARGUMENTS_HELP = """\
- Use %(custom_build_dir)s for relative custom build directory.
- Use %(custom_server_path)s for relative custom server path.
- Use %(other_repo_path)s for the path of the other repo.
- Use %(build_dest)s for the build_dest code, used for example to build the \
database name."""


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"
    is_custom_build = fields.Boolean('Custom Build')
    skip_test_jobs = fields.Boolean('Skip standard test jobs')
    custom_build_dir = fields.Char(
        'Custom Build Directory',
        help="Relative directory where repo will be checked out"
    )
    custom_server_path = fields.Char(
        'Custom Server Path',
        help="Relative path of starter script",
    )
    custom_server_params = fields.Char(
        'Custom Server Flags',
        help=ARGUMENTS_HELP,
    )
    custom_pre_build_cmd = fields.Char(
        'Custom Pre-build Command',
        help=ARGUMENTS_HELP,
    )
    other_repo_id = fields.Many2one(
        'runbot.repo',
        'Other repository',
        help='Specify a secondary repository whose path can be passed to the '
        'build commands.',
    )
