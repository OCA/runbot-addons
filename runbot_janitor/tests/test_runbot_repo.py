# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import os
import shutil
import tempfile
import subprocess
import sys
import psutil
import signal

import logging
_logger = logging.getLogger(__name__)

from openerp.tests import TransactionCase
from ..models.runbot_repo import exp_list_posix_user


class TestRunbotRepo(TransactionCase):
    """Aggressively clean filesystem databases and processes."""

    def setUp(self):
        """
        Create a temp build dir with a python file in it
        Run a process from inside build dir
        Create a database with similar name to temp build dir
        """
        super(TestRunbotRepo, self).setUp()
        self.runbot_repo = self.env['runbot.repo']
        self.runbot_build = self.env['runbot.build']

        # Filesystem
        self.root = os.path.join(self.runbot_repo.root(), 'build')
        if not os.path.exists(self.root):
            os.mkdir(self.root)
        self.build_dir = tempfile.mkdtemp(dir=self.root)
        self.build_basename = os.path.basename(self.build_dir)
        self.build_file_handle = tempfile.mkstemp(
            suffix=".py", dir=self.build_dir
        )

        # Database
        self.base_database = self.build_basename + "-base"
        self.all_database = self.build_basename + "-all"
        self.runbot_build.pg_createdb(dbname=self.base_database)
        self.runbot_build.pg_createdb(dbname=self.all_database)

        # Process
        self.build_filename = self.build_file_handle[1]
        with open(self.build_filename, 'w') as f:
            f.write("from time import sleep; sleep(60)")
        self.process = subprocess.Popen(
            [sys.executable, self.build_filename, '-d', self.all_database],
        )

    def tearDown(self):
        """Delete temp build dir, kill process and drop database"""
        if self.process.returncode is None:
            self.process.kill()
        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)
        # Database
        self.runbot_build.pg_dropdb(dbname=self.build_basename + "-base")
        self.runbot_build.pg_dropdb(dbname=self.build_basename + "-all")

    def test_clean_up_process(self):
        """Kill processes which run executables in those directories or are
        connected to databases matching the directory names matching
        the pattern.

        :param pattern: string
        """
        self.assertIn(self.process.pid, psutil.pids())
        self.assertIsNone(self.process.returncode)
        self.runbot_repo.clean_up_process(self.build_basename)
        self.process.wait()
        self.assertEqual(self.process.returncode, -signal.SIGKILL)

    def test_clean_up_database(self):
        """Drop all databases whose names match the directory names matching
        the pattern.

        :param pattern:string
        """
        db_list = exp_list_posix_user()
        self.assertIn(self.base_database, db_list)
        self.assertIn(self.all_database, db_list)

        # cleaning all the test database
        self.runbot_repo.clean_up_database(self.build_basename)

        # Need to refresh the db list
        db_list = exp_list_posix_user()
        self.assertNotIn(self.base_database, db_list)
        self.assertNotIn(self.all_database, db_list)

    def test_clean_up_filesystem(self):
        """Delete the directory and its contents matching the pattern.

        :param pattern: string
        """
        self.assertTrue(os.path.isdir(self.build_dir))
        self.runbot_repo.clean_up_filesystem(self.build_basename)
        self.assertFalse(os.path.isdir(self.build_dir))
