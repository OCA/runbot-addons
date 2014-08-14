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
_logger = logging.getLogger("runbot-job")
ORIGINAL_PATH = os.environ.get('PATH', '').split(':')

class PylintConf(osv.osv):
    """
    class docstring
    """

    _name = "pylint.conf"

    _columns = {
        'name': fields.char("Name"),
        'path_to_test': fields.char(string = "Path to test"),
        'ignore': fields.char(string = "Ignore files"),
        'error_ids': fields.many2many(
            'pylint.error', 'pylint_conf_rel_error', 'conf_id', 'error_id',
            "Errors"),
    }

    _defaults = {
        'ignore' : "__openerp__.py"
    }

    def _run_test_pylint(self, cr, uid, errors, paths_to_test, build_openerp_path_base, ignore, log_path, lock_path):
        """
        method docstring
        """
        build_pool = self.pool.get('runbot.build')
        path_server = [build_openerp_path_base]
        env = {
            'PYTHONPATH': ':'.join(build_openerp_path_base),
            'PATH': ':'.join(path_server + ORIGINAL_PATH),
        }
        cmd = ['pylint',
            '--msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] ' +
            '{msg}"', "-d", "all", "-r", "n"] + errors + paths_to_test + ignore
        return build_pool.spawn(cmd, lock_path, log_path, cpu_limit=2100, env=env)


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
                    operand1, operand2 = name.split(
                        ' ', 1)
                    ids = self.search(cr, user, [('code', operator, operand1),
                                      ('name', operator, operand2)] + args,
                                      limit=limit)
            else:
                ids = self.search(cr, user, ['&', '!',
                                  ('code', '=like', name + "%"),
                                  ('name', operator, name)] + args,
                                  limit=limit)
                if ids and len(name.split()) >= 2:
                    operand1, operand2 = name.split(
                        ' ', 1)
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
