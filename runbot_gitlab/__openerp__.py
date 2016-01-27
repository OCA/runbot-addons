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
    'name': 'Runbot Gitlab Integration',
    'category': 'Website',
    'summary': 'Runbot with Gitlab integration',
    'version': '8.0.1.1.0',
    'author': "Savoir-faire Linux,Therp BV,Odoo Community Association (OCA)",
    'depends': ['runbot'],
    'data': [
        "views/runbot_branch.xml",
        "views/runbot_build.xml",
        'views/runbot_repo.xml',
    ],
    'external_dependencies': {
        'python': [
            'requests',
        ]
    },
    'installable': True,
}
