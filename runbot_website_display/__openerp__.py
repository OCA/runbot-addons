# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Runbot display options",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Usability",
    "summary": "Allows to reorder and hide runbot repositories",
    "depends": [
        'runbot',
    ],
    "data": [
        "views/runbot_branch.xml",
        "views/runbot_repo.xml",
    ],
    "installable": True,
}
