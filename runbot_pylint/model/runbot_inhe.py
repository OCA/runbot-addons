# -*- encoding: utf-8 -*-

import argparse
from openerp.osv import fields, osv
import logging
import subprocess
import os
import openerp.tools as tools
logger = logging.getLogger('runbot-job')

class runbot_repo(osv.osv):

    _inherit = 'runbot.repo'

    _columns = {
        'pylint_test': fields.boolean('Test Pylint'),
    }

class runbot_build(osv.osv):
    _inherit = "runbot.build"
    
    def job_30_run(self, cr, uid, build, lock_path, log_path, args=None):
        logger = logging.getLogger('runbot-job')
        res = super(runbot_build, self).job_30_run(cr, uid, build, lock_path, log_path)
        print build.path(), "KKKKKKKKKKKKKKKKKKKKK"
        print build.result, 'buildddddddddddddddddd'
        #~ if build.result == 'ok':
        logger.info("running pylint tests...")
        #~ if True:
        #~ try:
        print args, 'ARGSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS'
        build_openerp_path=build.path()+'/odoo.py'
        #~ env = self.env_from_args(args, 'all')
        #~ add_env_lib( env )
        #~ pylint_log = os.path.join(self.args.log_prefix, pylint_test_log_path)
        command = ['--msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"', "-d", "all", "-e", "E0601", "-e", "E1124", "-e", "E0602", "-e", "E1306", "-e", "E0101"]
        #~ openerp_path = os.path.join( self.args.server_path, "openerp" )
        if os.path.exists( build_openerp_path ):
            command.append( build_openerp_path )
            self.run_command(None, 'pylint', command, build_openerp_path)
        else:
            logger.info("not exists path [%s]"%(build_openerp_path) )
        return res
    
    
    def run_command(self, log_path, app, command, server_path):
        """
        Small wrapper around the `anyone` command. It is used like:
            command ({..}, path_to_logs, 'initialize --tests')
        return tuple (bool:finished, int:return_code)
        """
        hide_stderr=False
        if log_path is None:
            log_file = None
        else:
            log_file = open(log_path, 'w')

        if isinstance(command, basestring):
            command = command.split()
        logger.info("running command `%s %s`", app, ' '.join(command))
        stderr = open(os.devnull, 'w') if hide_stderr else log_file
        app_path = os.path.join( os.path.realpath( os.path.join( os.path.dirname(__file__) ) ), app )
        app_server = os.path.join( server_path, app )
        if os.path.exists( app_server ):
            app_path = app_server
        elif os.path.exists( app_path ):
            app_path = app_path
        else:
            app_path = app
        export_str = ""
        command = [ app_path ] + command
        export_str += '\n' + ' '.join( command )
        p = subprocess.Popen(command,
                             stdout=log_file, stderr=stderr,
                             close_fds=True, env={})
        r = [True, 0]
        return tuple(r)
