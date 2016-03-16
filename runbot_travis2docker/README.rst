.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Runbot travis to docker
=======================

This app allows you to generate runbot builds based on docker.
Use .travis.yml file of your git repository to generate a Dockerfile after that
start to build a image, run a container to test and re-run the same container with instance alive.

Installation
============

To install this module, you need to:

1. Install `docker <http://www.docker.com>`_ (Version >= 1.8)
2. Install `travis2docker <https://github.com/vauxoo/travis2docker>`_
3. Use .travis.yml in all your repositories with maintainer-quality-tools with support for runbot.

Example of a installation from scratch:

1. Create OS "runbot" user.
  - `useradd -d /home/runbot -m -s /bin/bash -p runbotpwd runbot && usermod -aG docker runbot`
  - `su - runbot`
2. Clone all repositories
  
  ```bash
  # Run as runbot user:
  mkdir -p ~/instance
  git clone https://github.com/Vauxoo/runbot-addons.git -b 9.0 ~/instance/dependencies/runbot-addons
  git clone https://github.com/Vauxoo/odoo-extra.git -b 9.0 ~/instance/dependencies/odoo-extra
  git clone https://github.com/odoo/odoo.git -b 9.0 ~/instance/odoo
  ```

3. Install dependencies apt and pip packages

  ```bash
  # Run as root user:
  apt-get install -y python-pip python-dev python-lxml \
      libsasl2-dev libldap2-dev libssl-dev \
      libjpeg-dev \
      python-matplotlib \
      nodejs npm node-less
  ln -sf /usr/sbin/node /usr/bin/node
  sed -i '/lxml/d' /home/runbot/instance/odoo/requirements.txt
  pip install -r /home/runbot/instance/odoo/requirements.txt
  pip install travis2docker simplejson
  npm install -g less-plugin-clean-css

  locale-gen fr_FR \
    && locale-gen en_US.UTF-8 \
    && dpkg-reconfigure locales \
    && update-locale LANG=en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 \
    && ln -s /usr/share/i18n/SUPPORTED /var/lib/locales/supported.d/all \
    && locale-gen \
    && echo 'LANG="en_US.UTF-8"' > /etc/default/locale
  ```

4. Install and configure postgresql

  ```bash
  # Run as root user:
  apt-get install -y postgresql-9.3 postgresql-contrib-9.3 postgresql-common postgresql-server-dev-9.3
  su - postgres -c "psql -c  \"CREATE ROLE runbot LOGIN PASSWORD 'runbotpwd' SUPERUSER INHERIT CREATEDB CREATEROLE;\""
  
  # Run as runbot user:
  createdb runbot
  ```

5. Configure odoo and start with test

  ```bash
  # Run as runbot user:
  echo -e "[options]\naddons_path=${HOME}/instance/dependencies/runbot-addons,\n    ${HOME}/instance/dependencies/odoo-extra,\n    ${HOME}/instance/odoo/addons,\n    ${HOME}/instance/odoo/openerp/addons\ndb_name = runbot\ndbfilter = runbot" | tee -a ~/.openerp_serverrc
  ~/instance/odoo/odoo.py -i runbot_travis2docker --test-enable
  ```
 
Contributors
------------

* Moises Lopez <moylop260@vauxoo.com>

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

