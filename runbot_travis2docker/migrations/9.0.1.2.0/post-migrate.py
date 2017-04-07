# coding: utf-8
# © 2017 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """Skip new feature for old runbot builds."""
    cr.execute("UPDATE runbot_build SET docker_executed_commands = true")
    cr.commit()
