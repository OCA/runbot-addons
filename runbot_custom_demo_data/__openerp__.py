# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Samuel Lefever
#    Copyright 2015 Niboo SPRL
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
    "name": "Runbot Custom Demo Data",
    "version": "0.1",
    "author": "Niboo,Odoo Community Association (OCA)",
    "category": "Runbot",
    "description": """
Runbot Custom Demo Data
=======================

Add a job to only load demo data from the repository and not from odoo modules

Contributors
------------
* Samuel Lefever (sam@niboo.be)
""",
    "depends": ["runbot"],
    "data": [
        'runbot_repo.xml',
    ],
    "active": False,
    "installable": True
}
