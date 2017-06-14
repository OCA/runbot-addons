# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Coverage for runbot",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Runbot",
    "summary": "Collect coverage information during test_all",
    "depends": [
        'runbot',
    ],
    "data": [
        "views/runbot_repo.xml",
        'views/templates.xml',
    ],
}
