# -*- encoding: utf-8 -*-
# Copyright (c) 2010 - 2014 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Runbot Relative Links',
    'category': 'Website',
    'summary': 'Provide protocol relative links in Runbot',
    'version': '9.0.1.0.0',
    'author': "LasLabs, Savoir-faire Linux, Odoo Community Association (OCA)",
    'depends': ['runbot'],
    'data': [
        'views/runbot_template.xml',
    ],
    'installable': True,
    'application': False,
}
