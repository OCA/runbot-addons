# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2010 Savoir-faire Linux
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

import logging
import simplejson
import werkzeug
from werkzeug.wrappers import Response

from openerp import http, SUPERUSER_ID
from openerp.http import request

logger = logging.getLogger(__name__)


class GitlabCIController(http.Controller):
    CONTROLLER_PREFIX = '/gitlab-ci/<repo_id>'

    @http.route(CONTROLLER_PREFIX, type="http", auth="public")
    def repo_view(self, repo_id, ref=None):
        """Redirect to runbot page related to current repo"""
        try:
            registry, cr, uid = request.registry, request.cr, SUPERUSER_ID

            branch_id = registry['runbot.branch'].search(
                cr, uid, [('branch_name', '=', ref)]
            )[0]
            build_id = registry['runbot.build'].search(
                cr, uid, [
                    ('branch_id', '=', branch_id),
                    ('result', '!=', 'skipped'),
                ], limit=1, order='job_start desc',
            )[0]
        except IndexError:
            return werkzeug.utils.redirect('/runbot/repo/%s' % repo_id)
        else:
            return werkzeug.utils.redirect('/runbot/build/%d' % build_id)

    @http.route(CONTROLLER_PREFIX + "/build", type="json", auth="public")
    def build(self, repo_id, token=None):
        """Call to start build for regular push"""
        logger.info("build with token %s" % token)
        return {}

    @http.route(CONTROLLER_PREFIX + "/builds/<sha>",
                type="http", auth="public")
    def build_view(self, repo_id, sha):
        """Call on merge request open/close"""
        try:
            registry, cr, uid = request.registry, request.cr, SUPERUSER_ID
            build_id = registry['runbot.build'].search(
                cr, uid, [
                    ('name', 'like', sha + '%'),
                    ('result', '!=', 'skipped'),
                ],
                limit=1, order='job_start desc'
            )[0]
        except (IndexError, KeyError):
            return werkzeug.utils.redirect('/runbot/repo/%s' % repo_id)
        else:
            return werkzeug.utils.redirect('/runbot/build/%d' % build_id)

    @http.route(CONTROLLER_PREFIX + "/builds/<sha>/status.json",
                type="http", auth="public")
    def builds(self, repo_id, sha, token=None):
        """Call on merge request open/close"""
        res = None
        try:
            logger.debug("build with token %s" % token)
            logger.debug("I want the status of commit %s" % sha)
            registry, cr, uid = request.registry, request.cr, SUPERUSER_ID
            status = 'unknown'
            try:
                build_id = registry['runbot.build'].search(
                    cr, uid, [
                        ('name', 'like', sha + '%'),
                        ('result', '!=', 'skipped'),
                    ], limit=1, order='job_start desc'
                )[0]
                build = registry['runbot.build'].browse(cr, uid, build_id)
                result = build.result
                state = build.state
                logger.debug("Build status of commit %s is %s" % (sha, state))
                logger.debug("Build result of commit %s is %s" % (sha, result))
                if result == 'ko':
                    status = 'failed'
                elif state == 'pending':
                    status = 'pending'
                elif state == 'testing':
                    status = 'pending'
                elif state == 'running':
                    status = 'running'
                elif result in ['ok', 'warn']:
                    status = 'success'
                else:
                    status = 'unknown'
            except IndexError:
                logger.debug("No good builds found for commit %s" % sha)
                status = 'failed'
            finally:
                res = {
                    'id': repo_id,
                    'sha': sha,
                    'status': status,
                }
        finally:
            res = simplejson.dumps(res)
            return Response(res, mimetype='application/json')

    @http.route(CONTROLLER_PREFIX + "/status.png", type="http", auth="public")
    def status_badge(self, repo_id, ref):
        logger.info("I want the status badge for branch %s" % ref)
        return werkzeug.utils.redirect(
            '/runbot/badge/%s/%s.svg' % (repo_id, ref)
        )

    @http.route("/<namespace>/<repo>/services/gitlab_ci/edit",
                type="json", auth="public")
    def edit(self, namespace, repo):
        logger.exception("Edit for %s/%s" % (namespace, repo))
