# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version=None):
    cr.execute(
        """update runbot_repo set buildout_branch_id=runbot_branch.id
        from runbot_branch where
        runbot_branch.repo_id=runbot_repo.id and runbot_branch.buildout_default
        """
    )
