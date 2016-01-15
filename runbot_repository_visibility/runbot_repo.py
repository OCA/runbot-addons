# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

import logging
from openerp import fields, models

_logger = logging.getLogger(__name__)


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"
    _order = "sequence"

    sequence = fields.Integer(
        'Sequence',
        default=10,
        )
    visible_on_website = fields.Boolean(
        'Visible On Website?',
        default=True,
        )
