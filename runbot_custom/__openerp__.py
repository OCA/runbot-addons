# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
##############################################################################

{
    'name': 'Runbot Custom Builder',
    'category': 'Website',
    'summary': 'Runbot with custom build instructions',
    'version': '1.0',
    'description': """
Runbot Custom Builder
=====================

Runbot with custom build instructions.
This is useful for custom installation and deployment scripts such as buildout.

Add option in repo form view for custom builds. When checked:

* Modules to test becomes required attribute.
* Custom build directory can be specified. This is where the repo will be
  cloned in the build directory.
* Custom server path is required to be specified. This is tells runbot which
  executable script to run.
* Custom server flags can be specified to add to execution. E.g. --workers=0
* Pre-build commands can be run such as additional fetch scripts or buildout.

Contributors
------------
* Sandy Carter (sandy.carter@savoirfairelinux.com)
""",
    'author': 'Savoir-faire Linux',
    'depends': ['runbot'],
    'data': [
        'runbot_repo_view.xml',
    ],
    'installable': True,
}
