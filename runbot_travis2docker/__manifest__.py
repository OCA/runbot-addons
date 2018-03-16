# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Runbot travis to docker",
    "summary": "Generate docker with odoo instance based on .travis.yml",
    "version": "11.0.1.0.0",
    "category": "runbot",
    "website": "https://odoo-community.org/",
    "author": "Vauxoo,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "runbot",
    ],
    "external_dependencies": {
        "python": [
            'travis2docker',
        ],
        'bin': [
            'docker',
        ],
    },
    "data": [
        "views/runbot_repo_view.xml",
        "views/runbot_build_view.xml",
        "views/runbot_branch_view.xml",
        "data/ir_cron_data.xml",
    ],
    "demo": [
        "demo/runbot_repo_demo.xml",
    ],
    "application": False,
    "installable": True,
}
