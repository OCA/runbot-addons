.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

========================
Runbot Send Email Result
========================

This addon sends the results of the Runbot builds through email, Runbot send the notification to all followers of build, the notification has the following items:

* **General Info:** Contains the Status of build, Committer name, SHA Commit, Commit description. In this section runbot will indicate status changes of the build, showing color and icon related with such build status.

 .. figure:: ../runbot_send_email/static/img/gi.png
 
* **System Message:** Contains a description of the status of the build with any suggestions if any issues are found.

 .. figure:: ../runbot_send_email/static/img/sm.png

* **Debug:** Contains important information if you want to debug, access via ssh or logs.

 .. figure:: ../runbot_send_email/static/img/dg.png

* **Documentation:** Contains the respective links to access the documentation on the runbot, or other topic associated.

 .. figure:: ../runbot_send_email/static/img/dc.png

* **Issue:** Contains link to report any issues.

 .. figure:: ../runbot_send_email/static/img/is.png

How to follow a build or repository
------------------------------------

This addon allows to follow builds or repositories, for doing so need to be logged in, then with the following buttons, you can watch/unwatch any builds/repositories which you belong to, also if you follow a repository, you will follow the next build created which belongs to that repository.

* **For follow/unfollow a repository.**

 .. figure:: ../runbot_send_email/static/img/watch_repo.jpeg

* **For follow/unfollow a build.**

 .. figure:: ../runbot_send_email/static/img/watch_build.png

Requirements:
==============

 * `runbot` module.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/vauxoo/runbot-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Jonathan Osorio <jonathan@vauxoo.com>
* Moises Lopez <moylop260@vauxoo.com>

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* Vauxoo - http://www.vauxoo.com/

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
