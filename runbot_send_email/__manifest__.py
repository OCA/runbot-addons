# Copyright <2016> <Vauxoo info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Runbot Send Email Result",
    "summary": "This module sends the results of the RunBot builds through \
email.",
    "version": "11.0.1.0.0",
    "category": "runbot",
    "website": "https://www.vauxoo.com",
    "author": "Vauxoo,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "runbot"
    ],
    "data": [
        "views/runbot_send_email_view.xml",
        "views/assets.xml",
        "data/runbot_send_email_data.xml",
    ],
    "demo": [
        "demo/ir_mail_server_demo.xml",
    ],
    "application": False,
    "installable": True,
}
