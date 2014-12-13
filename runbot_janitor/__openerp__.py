# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
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
    'name': 'Runbot Janitor',
    'category': 'Website',
    'summary': 'Aggressively clean filesystem databases and processes',
    'version': '1.0',
    'description': """
Runbot Janitor
==============

Aggressively clean filesystem databases and processes
Start a cron which will look in runbot's build directories
(runbot/static/build) and identify all build directories which have no running
builds (runbot.build).

Using the names of these directories, cleanup by:
  * killing processes which run executables in those directories or are
    connected to databases matching the directory names
  * drop all databases whose names match the directory names
  * delete the directory and its contents

Contributors
------------
* Sandy Carter (sandy.carter@savoirfairelinux.com)
* Jordi Riera (jordi.riera@savoirfairelinux.com)
""",
    'author': 'Savoir-faire Linux',
    'depends': ['runbot'],
    'data': [
    ],
    'installable': True,
}
