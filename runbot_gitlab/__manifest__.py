# Copyright 2010 - 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# Copyright 2017 Vauxoo <info@vauxoo.com> (<https://www.vauxoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Runbot Gitlab Integration',
    'summary': 'Gitlab Integration',
    'author': 'Savoir-faire Linux, Vauxoo, Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/runbot-addons",
    'license': 'AGPL-3',
    'category': 'Runbot',
    'version': '11.0.1.0.0',
    'depends': ['runbot'],
    'data': [
        'views/runbot_repo.xml',
    ],
    'installable': True,
}
