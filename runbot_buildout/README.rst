.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===================
Buildout for runbot
===================

This module was written to make it convenient to use `buildout based builds <http://pythonhosted.org/anybox.recipe.odoo>`_ on runbot.

Configuration
=============

To configure this module, you need to:

#. turn on `Use buildouts` on a repository
#. fill in a regex that allows to differentiate a normal branch name: For runbot, branches should be named ``$version-$sometext`` anyways, so this module's suggestion is to call buildout branches ``buildout-$version-$sometext``
#. check the value of the field `Buildout section`, this must be the name you use in your buildouts
#. if you use multiple buildouts for the same version to implement some kind of DTAP scenario (you should), you can mark some buildout branch as the one to be used for tests by navigating to the branch and checking `Default for this version`
#. when converting a repository to use buildouts, be sure to remove all dependency branches first. Otherwise, runbot will copy all of them unnecessarily. Then, rebuild some buildout branch, and when it is green, rebuild another branch that is supposed to use the buildout

Background
==========

This module will cause buildout branches to be treated radically differently: For buildout branches, the buildout will be run, and any failures reported in the build results. For normal branches, it will search for a buildout branch with a matching version, copy this buildout to a temporary directory, manipulate buildout.cfg to use the branch to be tested and the ports assigned for this instance, then rerun the buildout, then run tests within the buildout environment.

For this to work, your buildout.cfg needs to contain one addons line::

    git $the_exact_repo_url_as_configured_in_runbot parts/$repo_name $version

or if you use pinned branches::

    git $the_exact_repo_url_as_configured_in_runbot parts/$repo_name $commit_hash branch=$version

Which then will be replaced by::

    git $the_exact_repo_url_as_configured_in_runbot parts/$repo_name $commit_hash branch=$current_branchname

Known issues / Roadmap
======================

* none currently

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
