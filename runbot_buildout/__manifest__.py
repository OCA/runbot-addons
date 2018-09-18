# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Buildout for runbot",
    "version": "11.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Runbot",
    "summary": "Build your branches using buildout",
    "depends": [
        'runbot',
    ],
    "data": [
        "views/templates.xml",
        "views/runbot_branch.xml",
        "views/runbot_repo.xml",
    ],
    "external_dependencies": {
        "python": [
            "anybox.recipe.odoo",
            "zc.buildout",
        ],
    },
}
