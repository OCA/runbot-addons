# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Sylvain VanHoof, Samuel Lefever
#    Odoo, Open Source Management Solution
#    Copyright (C) 2010-2015 Eezee-It (<http://www.eezee-it.com>).
#    Copyright 2015 Niboo (<http://www.niboo.be>).
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
    'name': 'Runbot Multiple Hosting',
    'category': 'Runbot',
    'summary': 'Offer the base to use several hosting in Runbot',
    'version': '1.0',
    'description': """
Runbot Multiple Hosting
=======================

Add multiple hosting ability to runbot.

Contributors
------------
* Sylvain Van Hoof (sylvain.vanhoof@eezee-it.com)
* Samuel Lefever (sam@niboo.be)
""",
    'author': "Eezee-It,Niboo,Odoo Community Association (OCA)",
    'depends': ['runbot'],
    'data': [
        "views/runbot_repo.xml"
    ],
    'installable': True,
}
