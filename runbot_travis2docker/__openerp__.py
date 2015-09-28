# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Runbot travis to docker",
    "summary": "Generate docker with odoo instance based on .travis.yml",
    "version": "8.0.1.0.0",
    "category": "runbot",
    "website": "https://www.vauxoo.com",
    "author": "Vauxoo",
    "license": "AGPL-3",
    "depends": [
        "runbot",
    ],
    "external_dependencies": {
        "python": [],
        "bin": ['travisfile2dockerfile'],
    },
    "data": [
        "views/runbot_repo_view.xml",
    ],
    "demo": [
    ],
    "application": False,
    "installable": True,
}
