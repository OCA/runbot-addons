.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=========================
Runbot Gitlab Integration
=========================

This addon supports gitlab's CI API available in versions >= 8.1.

Configuration
=============

On your repository, check the box `Use gitlab` and fill in your gitlab user's API token. You can also decide to clean up old branches (`Active branches only`), to only run tests for merge requests (`MR only`) and to make protected branches sticky (`Sticky for protected branches`).

Usage
=====

To use this module, you need to activate `Builds` in the gitlab project's settings. You'll also need to add a file called `.gitlab-ci.yml` to your repository's root. It's contents don't matter, this is only needed by gitlab to activate the CI logic. It has to be valid YAML though::

    job1:
        script: "noop"

suffices, where job1 is how the build is called internally in gitlab. Change this to whatever you see fit.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
:alt: Try me on Runbotrunbo
    :target: https://runbot.odoo-community.org/runbot/146/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/runbot_gitlab/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/runbot-addons/issues/new?body=module:%20runbot_gitlab%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Paul Catinean <paulcatinean@gmail.com>
* Holger Brunn <hbrunn@therp.nl>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
