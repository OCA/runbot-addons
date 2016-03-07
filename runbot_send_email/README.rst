.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Runbot Send Email Result
========================

This module sends the results of the RunBot builds through email, when there is a change of status, runbot send the notification to all followers of build, the notification has the following items:

* **General Info:** Contains the Status of build, Committer name, SHA Commit, Commit description. In this section runbot will indicate status changes of the build, showing color and icon related with such build status.

 .. image:: runbot_send_email/static/img/gi.png

* **System Message:** Contains a description of the status of the build with any suggestions if any issues are found.

 .. image:: runbot_send_email/static/img/sm.png

* **Debug:** Contains important information if you want to debug, access via ssh or logs.

 .. image:: runbot_send_email/static/img/dg.png

* **Documentation:** Contains the respective links to access the documentation on the runbot, or other topic associated.

 .. image:: runbot_send_email/static/img/dc.png

* **Issue:** Contains link to report any issues.

 .. image:: runbot_send_email/static/img/is.png

Requirements:
-------------

- `runbot_travis2docker` module.

Contributors
------------

* Luis Escobar <lescobar@vauxoo.com>

Maintainer
----------

 .. image:: https://www.vauxoo.com/logo.png
    :alt: Vauxoo
    :target: https://vauxoo.com

 This module is maintained by Vauxoo.

 a latinamerican company that provides training, coaching,
 development and implementation of enterprise management
 sytems and bases its entire operation strategy in the use
 of Open Source Software and its main product is odoo.

 To contribute to this module, please visit http://www.vauxoo.com.
