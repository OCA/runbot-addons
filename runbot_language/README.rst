.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Runbot language
===========

This module was written to extend the functionality of runbot to support add custom language
and allow you to choose it from repository configuration.

Installation
============

To install this module, you need to:

* See main root README of this repository.

Configuration
=============

To configure this module, you need to:

* Go to `runbot.repo` model.
* Choose a language in new field.
* Wait a build creation with this configuration.
* Now, you will see in `runbot.build` a new field `language`
* Now, you can connect to this build and you will see GUI in language configurated.

Usage
=====

To use this module, you need to:

* Go to your new build and connect it.

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* Don't work fine with remote databases.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/runbot-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/runbot-addons/issues/new?body=module:%20runbot_language%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Moises Lopez <moylop260@vauxoo.com>

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

