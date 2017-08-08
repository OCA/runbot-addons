# -*- encoding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Runbot Relative Links',
    'category': 'Website',
    'summary': 'Provide protocol relative links in Runbot',
    'version': '9.0.1.0.0',
    'author': "LasLabs, Odoo Community Association (OCA)",
    'depends': ['runbot'],
    'data': [
        'views/runbot_template.xml',
        'views/assets.xml',
    ],
    'installable': True,
    'application': False,
}
