# -*- coding: utf-8 -*-
##############################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: moylop260@vauxoo.com
############################################################################

'''
    This file is used to add the field lang in runbot.build and the function
      that install and assign the language to the users in the instance
      generated.
'''

import logging

from openerp import api, fields, models, tools
from openerp.addons.runbot.runbot import run

_logger = logging.getLogger(__name__)


class RunbotBuild(models.Model):

    '''
    Inherit class runbot_build to add field to select the language &
      the function with a job
      to install and assign the language to users if this is captured
      too is added with an super the
      function create to assign the language from repo in the builds.
    '''

    _inherit = "runbot.build"

    lang = fields.Selection(
        tools.scan_languages(), 'Language',
        help='Language to change '
        'instance after of run test.', copy=True)

    @api.multi
    def cmd(self):
        """Return a list describing the command to start the build"""
        cmd, modules = super(RunbotBuild, self).cmd()
        for build in self:
            if build.lang and build.job == 'job_30_run':
                cmd.append("--load-language=%s" % (build.lang))
        return cmd, modules

    @api.one
    def update_lang(self):
        """Set lang to all users into '-all' database"""
        if self.lang:
            db_name = "%s-all" % self.dest
            # All odoo versions has openerp/release.py file
            sys.path.insert(0, build.server("openerp"))
            try:
                release =  __import__("release")
            finally:
                sys.path.pop(0)
            version = float("{main_version}.{secondary_version}".format(
                main_version=release.version_info[0],
                secondary_version=release.version_info[1]))

            if version < 7:
                run(['psql', db_name, '-c', "UPDATE res_users SET lang='%s';" %
                     (self.lang)])
            else:
                run(['psql', db_name, '-c', "UPDATE res_partner SET lang='%s' "
                     "WHERE id IN (SELECT partner_id FROM res_users);" %
                     (self.lang)])
        return True

    def job_30_run(self, cr, uid, build, lock_path, log_path):
        res = super(RunbotBuild, self).job_30_run(cr, uid, build,
                                                  lock_path, log_path)
        self.update_lang(cr, uid, build.id)
        return res

    @api.model
    def create(self, values):
        """
        This method set language from repo in the build.
        """
        if values.get('branch_id', False) and 'lang' not in values:
            lang = self.env['runbot.branch'].browse(
                values['branch_id']).repo_id.lang
            values.update({
                'lang': lang,
            })
        return super(RunbotBuild, self).create(values)
