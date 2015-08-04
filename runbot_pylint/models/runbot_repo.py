# -*- encoding: utf-8 -*-
##############################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: moylop260@vauxoo.com
############################################################################

"""
This module is used to create new fields in the inherited classes
to work with pylint from runbot
"""

import os

from openerp import api, fields, models


class RunbotRepo(models.Model):

    """
    Added pylint_conf_path field to use a configuration
      of pylint by repository,
      to use for each build of repository.
    """

    _inherit = 'runbot.repo'

    pylint_conf_path = fields.Char(
        help='Relative path to pylint conf file')
    check_pylint = fields.Boolean(
        help='Check pylint to modules of this repo')

    @api.multi
    def get_module_list(self, treeish):
        """
        Get module list from a repo with a treeish (sha, tag or branch name)
        """
        repo_paths_list = []
        for repo in self:
            command_git = ['ls-tree', treeish, '--name-only']
            # get addons list from main repo
            repo_paths_str = repo.git(command_git +
                                      ['addons/', 'openerp/addons/'])
            if not repo_paths_str:
                # get addons list from module repo
                repo_paths_str = repo.git(command_git)
            repo_paths_list = repo_paths_str and\
                repo_paths_str.rstrip().split('\n') or []
            repo_paths_list = [os.path.basename(module)
                               for module in repo_paths_list]
        return repo_paths_list
