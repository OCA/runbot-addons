# -*- encoding: utf-8 -*-
# © 2010 - 2014 Savoir-faire Linux
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Runbot Skip Tests',
    'category': 'Website',
    'summary': 'Skip tests on runbot builds',
    'version': '8.0.1.0.0',
    'author': "Savoir-faire Linux,Therp BV, Odoo Community Association (OCA)",
    'depends': ['runbot'],
    'data': [
        "views/runbot_repo.xml",
    ],
    'installable': True,
}
