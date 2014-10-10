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
This module added new pylint test, this improvement quality of development,
    following standard guidelines of python language.
"""

from openerp.osv import fields, osv, expression
import os
import ast
ORIGINAL_PATH = os.environ.get('PATH', '').split(':')


def _get_paths_py_to_test(path):
    """
    This method is used to search py files in the path.

    :param path: Path of search py files.
    """
    list_paths_py = []
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            fname_path = os.path.join(dirname, filename)
            fext = os.path.splitext(fname_path)[1]
            if fext == '.py':
                list_paths_py.append(fname_path)
            else:
                continue
    return list_paths_py


class PylintConf(osv.osv):

    """
    This new class is used to select errors, path to test, and files to ignore.
    """

    _name = "pylint.conf"

    _columns = {
        'name': fields.char("Name"),
        'path_to_test': fields.char(string="Path to test"),
        'ignore': fields.char(string="Ignore files"),
        'error_ids': fields.many2many(
            'pylint.error', 'pylint_conf_rel_error', 'conf_id', 'error_id',
            "Errors"),
        'check_print': fields.boolean(string='Check Prints',
             help='Selected, to find prints in all py files in the'
             + 'specified path.'),
        'check_pdb': fields.boolean(string='Check Pdb',
             help='Selected, to find pdb in all py files in the'
             + 'specified path.'),
        'conf_file': fields.char(string="File of configuration",
             help='Indicate the name of the configuration file cfg extension')
    }

    _defaults = {
        'ignore': "__openerp__.py"
    }

    def _run_test_pylint(self, cr, uid, errors, paths_to_test,
                         build_openerp_path_base, ignore, log_path, lock_path,
                         params_extra):
        """
        This method is used to run pylint test, takes the parameters:

        :param errors: list of strings with the errors to test.
        :param paths_to_test: list of strings with the paths to test.
        :param build_openerp_path_base: string with the server path.
        :param build_openerp_path_base: list of strings with the files or
                                            directories to ignore in the test.
        :param log_path: path of log file, this parameter is string, where are
                            has saved the log of test.
        :param lock_path: path of lock file, this parameter is string.
        """
        build_pool = self.pool.get('runbot.build')
        path_server = [build_openerp_path_base]
        env = {
            'PYTHONPATH': ':'.join(build_openerp_path_base),
            'PATH': ':'.join(path_server + ORIGINAL_PATH),
        }
        cmd = ['pylint',
               '--msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] ' +
               '{msg}"', "-r", "n"] + errors + paths_to_test + \
            ignore + params_extra
        print "***" * 10, ' '.join(cmd)
        return build_pool.spawn(cmd, lock_path, log_path, cpu_limit=2100,
                                env=env)

    def _search_print_pdb(self, cr, uid, build, paths_to_test, context=None):
        """
        This method is used to search all prints and import pdbs,
        for each paths to test.

        :param build: object build of runbot.
        :param paths_to_test: list of strings with the paths to test.
        """
        if context is None:
            context = {}
        for path_test in paths_to_test:
            for paths_py in _get_paths_py_to_test(path_test):
                with open(paths_py) as fin:
                    parsed = ast.parse(fin.read())
                for node in ast.walk(parsed):
                    if build.pylint_config.check_print and isinstance(node,
                                                                    ast.Print):
                        message = '"print" at line {} col {} of file: %s'\
                            .format(node.lineno, node.col_offset) % paths_py
                        self.pool['ir.logging'].create(cr, uid, {
                            'build_id': build.id,
                            'level': 'WARNING',
                            'type': 'runbot',
                            'name': 'odoo.runbot',
                            'message': message,
                            'path': paths_py,
                            'func': 'Detect print',
                            'line': node.lineno,
                        }, context=context)
                    elif build.pylint_config.check_pdb and isinstance(node,
                                                                 ast.Import):
                        for import_name in node.names:
                            if import_name.name == 'pdb':
                                message = '"import pdb" at line {} col {}' + \
                                    'of file: %s'.format(node.lineno,
                                                    node.col_offset) % paths_py
                                self.pool['ir.logging'].create(cr, uid, {
                                    'build_id': build.id,
                                    'level': 'WARNING',
                                    'type': 'runbot',
                                    'name': 'odoo.runbot',
                                    'message': message,
                                    'path': paths_py,
                                    'func': 'Detect pdb',
                                    'line': node.lineno,
                                }, context=context)


class PylintError(osv.osv):

    """
    This class is used to save catalog of errors pylint.
    """

    _name = "pylint.error"

    _columns = {
        'code': fields.char(string="Code"),
        'name': fields.char(string="Description"),
    }

    def name_search(self, cr, user, name, args=None, operator='ilike',
                    context=None, limit=100):
        """
        This method is used to search errors by code or name.
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
        This method is used to show in the views the error with the following
            format: code error + description.
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
