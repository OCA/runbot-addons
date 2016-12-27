# -*- coding: utf-8 -*-
# Copyright 2015 Niboo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
