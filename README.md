[![Build Status](https://travis-ci.org/OCA/runbot-addons.svg?branch=9.0)](https://travis-ci.org/OCA/runbot-addons)
[![Coverage Status](https://coveralls.io/repos/OCA/runbot-addons/badge.svg?branch=9.0&service=github)](https://coveralls.io/github/OCA/runbot-addons?branch=9.0)

Odoo modules for runbot
========================

Dependencies
------------
* Odoo repositories
     * [odoo-extra](https://github.com/odoo/odoo-extra)
* Dependencies
     * Python
         * matplotlib (through runbot)

[//]: # (addons)
Available addons
----------------
addon | version | summary
--- | --- | ---
[runbot_build_instructions](runbot_build_instructions/) | 9.0.1.0.0 | Runbot with custom build and run instructions
[runbot_skip_tests](runbot_skip_tests/) | 9.0.1.0.0 | Skip tests on runbot builds
[runbot_travis2docker](runbot_travis2docker/) | 9.0.1.1.0 | Generate docker with odoo instance based on .travis.yml

Unported addons
---------------
addon | version | summary
--- | --- | ---
[runbot_gitlab](runbot_gitlab/) | 8.0.1.1.0 (unported) | Runbot with Gitlab integration
[runbot_pylint](runbot_pylint/) | 8.0.1.0.0 (unported) | Runbot
[runbot_secure](runbot_secure/) | 8.0.1.0.0 (unported) | Provide https links

[//]: # (end addons)
