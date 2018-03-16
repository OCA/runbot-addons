.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Runbot travis to docker
=======================

This module allows you to generate runbot builds based on docker.
Use .travis.yml file of your git repository to generate a Dockerfile after that
start to build a image, run a container to test and re-run the same container with live instance.

Installation
============

To install this module, you need to:

- Install docker https://docs.docker.com/installation
- Install travis2docker
- Install runbot module https://github.com/odoo/runbot

Configuration
=============

To configure this module, you need to:

* Go to menu Runbot/Repository and activate the field check box of "Tavis to docker"

Usage
=====

To use this module, you need to know the main functionallity of runbot base
and know the main functionallity of travis and .travis.yml file
and know the main funcitonallity of oca/maintainer-quality-tools.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/146/11.0

Known issues / Roadmap
======================

* This module run just the first build with environment variable TESTS="1"

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

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Moisés López <moylop260@vauxoo.com>
* Dave Lasley <dave@laslabs.com>

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* Vauxoo - https://www.vauxoo.com/
* LasLabs - https://laslabs.com/

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
