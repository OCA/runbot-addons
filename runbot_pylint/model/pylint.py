#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: vauxoo consultores (info@vauxoo.com)
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
module docstring
"""

from openerp.osv import fields, osv, expression
import os
import subprocess
import logging
#~ logger = logging.get_logger('runbot-job')

class PylintConf(osv.osv):
    """
    class docstring
    """

    _name = "pylint.conf"

    _columns = {
        'name': fields.char("Name"),
        'ignore': fields.char("Ignore files"),
        'error_ids': fields.many2many(
            'pylint.error', 'pylint_conf_rel_error', 'conf_id', 'error_id',
            "Errors"),
    }

    def _run_test_pylint(self, cr, uid, errors, paths_to_test, build_openerp_path_base, ignore):
        """
        method docstring
        """
        command = [
            '--msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] ' +
            '{msg}"', "-d", "all", "-r", "n"] + errors + paths_to_test + ignore
        self.run_command(None, 'pylint', command)
        return True

    def run_command(self, log_path, app, command):
        """
        Small wrapper around the `anyone` command. It is used like:
            command ({..}, path_to_logs, 'initialize --tests')
        return tuple (bool:finished, int:return_code)
        """
        hide_stderr = False
        if log_path is None:
            log_file = None
        else:
            log_file = open(log_path, 'w')
        if isinstance(command, basestring):
            command = command.split()
        #~ logger.info("running command `%s %s`", app, ' '.join(command))
        stderr = open(os.devnull, 'w') if hide_stderr else log_file
        app_path = os.path.join(
            os.path.realpath(os.path.join(os.path.dirname(__file__))), app)
        if os.path.exists(app_path):
            app_path = app_path
        else:
            app_path = app
        command = [app_path] + command
        subprocess.Popen(command, stdout=log_file, stderr=stderr,
                         close_fds=True, env={})
        returned = [True, 0]
        return tuple(returned)


class PylintError(osv.osv):
    """
    class docstring
    """

    _name = "pylint.error"

    _columns = {
        'code': fields.char(string="Code"),
        'name': fields.char(string="Description"),
    }

    def name_search(self, cr, user, name, args=None, operator='ilike',
                    context=None, limit=100):
        """
        method docstring
        """
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            if operator not in expression.NEGATIVE_TERM_OPERATORS:
                ids = self.search(
                    cr, user, ['|', ('code', '=like', name + "%"),
                                 ('name', operator, name)] + args, limit=limit)
                if not ids and len(name.split()) >= 2:
                    # Separating code and name of account for searching
                    operand1, operand2 = name.split(
                        ' ', 1)  # name can contain spaces e.g. OpenERP S.A.
                    ids = self.search(cr, user, [('code', operator, operand1),
                                      ('name', operator, operand2)] + args,
                                      limit=limit)
            else:
                ids = self.search(cr, user, ['&', '!',
                                  ('code', '=like', name + "%"),
                                  ('name', operator, name)] + args,
                                  limit=limit)
                # as negation want to restric, do if already have results
                if ids and len(name.split()) >= 2:
                    operand1, operand2 = name.split(
                        ' ', 1)  # name can contain spaces e.g. OpenERP S.A.
                    ids = self.search(cr, user, [('code', operator, operand1),
                                      ('name', operator, operand2),
                                      ('id', 'in', ids)]
                                      + args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        """
        method docstring
        """
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' ' + name
            res.append((record['id'], name))
        return res
