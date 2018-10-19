# Copyright <2017> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Runbot Gitlab Integration",
    "summary": "Gitlab Integration",
    "author": "Vauxoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/runbot-addons",
    "license": "AGPL-3",
    "category": "runbot",
    "version": "11.0.1.0.0",
    "depends": ["runbot"],
    "data": [
        "views/runbot_repo.xml",
        "templates/build.xml",
        "templates/runbot_gitlab_logos.xml",
    ],
    "installable": True,
}
