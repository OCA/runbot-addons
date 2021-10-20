# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Preseed test database in runbot",
    "version": "11.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Runbot",
    "summary": "Allows to run tests with a partially initialized database",
    "depends": [
        'runbot',
    ],
    "data": [
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "wizards/runbot_preseed_database_refresh.xml",
        "views/runbot_branch.xml",
        "views/runbot_repo.xml",
    ],
}
