# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import multiprocessing
import subprocess
import tarfile
import tempfile
from odoo import models
from odoo.addons.runbot.common import lock


class RunbotBuild(models.Model):
    _inherit = 'runbot.build'

    def _job_29_export_translations(self, build, lock_path, log_path):
        if not build.branch_id.push_pot or build.build_type == 'rebuild':
            return -2
        command, modules = build._cmd()
        process = multiprocessing.Process(
            target=self._export_translations.__func__,
            args=(
                None,
                command, modules, build.repo_id.path, build.repo_id.name,
                build.branch_id.branch_name, '%s-all' % build.dest, lock_path,
                log_path, self.env['ir.config_parameter'].get_param(
                    'runbot_push_pot.commit_message',
                    '[UPD] updated translations from runbot',
                ),
            ),
            name='translation export for %s' % build,
        )
        process.start()
        return process.pid

    def _export_translations(
            self, command, modules, repo_path, repo_url, branch_name, db_name,
            lock_path, log_path, commit_message,
    ):
        """Do the actual translation export. Note you can't override this
        because we don't use it as a class member"""
        lock(lock_path)
        with open(log_path, 'w') as log_file, tempfile.NamedTemporaryFile(
            suffix='.tgz', delete=False,
        ) as translation_file:
            command.extend([
                '-d', db_name,
                '--i18n-export', translation_file.name,
                '--modules', modules,
                '--stop-after-init',
            ])
            subprocess.check_call(
                command, stdout=log_file, stderr=log_file,
            )
            translations = tarfile.open(translation_file.name)
            with tempfile.TemporaryDirectory() as checkout:
                subprocess.run(
                    ['git', 'clone', repo_path, checkout],
                    stdout=log_file, stderr=log_file,
                )

                def git(*cmd, **kwargs):
                    cmd = ('git', '-C', checkout) + cmd
                    return subprocess.run(
                        cmd, stdout=log_file, stderr=log_file, **kwargs
                    )

                git('checkout', branch_name)
                translations.extractall(checkout)
                git('add', '.')
                diff_lines = [
                    line for line in
                    subprocess.run(
                        ['git', '-C', checkout, 'diff', 'HEAD', '-U0'],
                        capture_output=True
                    ).stdout.decode('utf8').split('\n')
                    if
                    # we want only lines from the diff where we actually have
                    # changes, and we want to ignore the date fields because
                    # they change for every export
                    (line.startswith('+') or line.startswith('-')) and not
                    (line.startswith('+++') or line.startswith('---')) and
                    'POT-Creation-Date' not in line and
                    'PO-Revision-Date' not in line
                ]
                if diff_lines:
                    git('commit', '-m', commit_message)
                    git('push', repo_url, branch_name)
