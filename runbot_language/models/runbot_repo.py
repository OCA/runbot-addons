# -*- coding: utf-8 -*-
##############################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: moylop260@vauxoo.com
############################################################################

from openerp import fields, models, tools


class RunbotRepo(models.Model):

    '''
    Inherit class runbot_repo to add field to select the language that must
      be assigned to builds
      that generate the repo.
    '''

    _inherit = "runbot.repo"

    lang = fields.Selection(
        tools.scan_languages(), 'Language',
        help='Language to change '
        'instance after of run test.', copy=True)
