#!/bin/bash

set -v
# odoo-extra has a bunch of v9 modules which aren't compatible, remove them
(cd ${HOME}/dependencies/odoo-extra; rm -rf $(ls | grep -v runbot$))

# odoo version 9.0 compatibility
find ${HOME}/dependencies/odoo-extra/runbot -name res_config_view.xml -exec sed -i 's/base.menu_config/base.menu_administration/g' {} \;

# Disabling matplotlib by https://github.com/travis-ci/travis-ci/issues/4948
find ${HOME}/dependencies/odoo-extra/runbot -name runbot.py -exec sed -i  '/from matplotlib.font_manager import FontProperties/d' {} \;
find ${HOME}/dependencies/odoo-extra/runbot -name runbot.py -exec sed -i  '/from matplotlib.textpath import TextToPath/d' {} \;
find ${HOME}/dependencies/odoo-extra/runbot -name __openerp__.py -exec sed -i  '/'matplotlib'/d' {} \;

# Change cron interval to avoid interference with tests
find ${HOME}/dependencies/odoo-extra/runbot -name runbot.xml -exec sed -i "s/'interval_number'>1</'interval_number'>60</g" {} \;


# Disabling test_crawl (native runbot fail)
find ${HOME} -name __init__.py -exec sed -i  "/import test_crawl/d" {} \;

# Download docker image required
if [ "${TESTS}" == "1"  ]; then docker pull vauxoo/odoo-80-image-shippable-auto; fi
