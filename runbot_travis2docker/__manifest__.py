# Copyright <2015> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Runbot travis to docker",
    "summary": "Generate docker with odoo instance based on .travis.yml",
    "version": "11.0.1.0.0",
    "category": "runbot",
    "website": "https://github.com/OCA/runbot-addons",
    "author": "Vauxoo,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "runbot",
    ],
    "external_dependencies": {
        "python": [
            "travis2docker",
        ],
        "bin": [
            "docker",
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
