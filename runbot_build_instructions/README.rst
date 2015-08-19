.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Runbot Custom Build and Run Instructions
========================================

Runbot with custom build instructions.
This is useful for custom installation and deployment scripts such as buildout.

Configuration
=============

This module adds an option in Repository form view for custom builds. When
checked:

* Modules to test becomes required attribute.
* Custom build directory can be specified. This is where the repo will be
  cloned in the build directory.
* Custom server path is required to be specified. This is tells runbot which
  executable script to run.
* Custom server flags can be specified to add to execution. E.g. --workers=0
* Pre-build commands can be run such as additional fetch scripts or buildout.
* An alternate repository can be specified, and then passed on to the custom
  build commands. A practical example of that is passing on a repository
  containing a clone of odoo to the custom build script. That script can for
  example make a local clone of odoo, saving both time and disk space.
* An option allows to skip the standard test jobs. This is useful if the whole
  build phase is done in a custom script in the prebuild step.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/146/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/{project_repo}/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/runbot-addons/issues/new?body=module:%20runbot_build_instructions%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------
* Sandy Carter (sandy.carter@savoirfairelinux.com)
* Leonardo Pistone (leonardo.pistone@camptocamp.com)

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
