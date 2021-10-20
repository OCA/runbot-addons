.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===============================
Preseed test database in runbot
===============================

This module allows you to have runbot use a database template that already has some modules installed. This allows for much faster builds in case you're only interested in a subset of the tests.

Configuration
=============

To configure this module, you need to:

#. go to your repository (all builds in the repo) or a branch (just builds for this branch)
#. alternatively
   - fill in a database name to be used as template. This database must exist in the cluster and be accessible for the user running runbot
   - use the wizard to select a build to use to generate a template. This will also preselect all modules installed in the build's database minus the build's modules to test as the list of modules to preseed
#. when you use builds to generate template, review the refresh cronjob to move it to a time where regeneration won't interfere with your development. During refreshing, repos and branches with preseeded database will fall back to the empty database, so you will have slow builds in this period, not failing ones

Usage
=====

You will have to regenerate the database template from time if you don't use the build mechanism, and you should also take care to have one branch tested with a fresh database. This is meant to speedup builds for which most tests are irrelevant.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/runbot-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Do not contact contributors directly about help with questions or problems concerning this addon, but use the `community mailing list <mailto:community@mail.odoo.com>`_ or the `appropriate specialized mailinglist <https://odoo-community.org/groups>`_ for help, and the bug tracker linked in `Bug Tracker`_ above for technical issues.

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
