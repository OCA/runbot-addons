.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===================
runbot_subject_skip
===================

This module skip a build based on the commit message.
Inspired by Travis-CI: https://docs.travis-ci.com/user/customizing-the-build#Skipping-a-build

Usage
=====

To use this module, you need create a commit message with the following keywords:
  - "[skip ci]" or "[ci skip]" uppercase or lowercase in anywhere

The builds will be skipped.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/146/11.0


Known issues / Roadmap
======================

* Just is used the first line of the commit message but in travis they are using all lines.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/runbot-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Moisés López <moylop260@vauxoo.com> (https://www.vauxoo.com)

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* Vauxoo (https://www.vauxoo.com)

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
