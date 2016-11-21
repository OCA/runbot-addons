#!/bin/bash

set -v

export DEPS=${HOME}/dependencies
# odoo-extra has a bunch of v9 modules which aren't compatible, remove them
(cd $DEPS/odoo-extra; rm -rf $(ls | grep -v runbot$))

# odoo version 9.0 compatibility
sed -i 's/base.menu_config/base.menu_administration/g' ${DEPS}/odoo-extra/runbot/res_config_view.xml

# Disabling matplotlib by https://github.com/travis-ci/travis-ci/issues/4948
sed -i '/from matplotlib.font_manager import FontProperties/d' $DEPS/odoo-extra/runbot/runbot.py
sed -i '/from matplotlib.textpath import TextToPath/d' $DEPS/odoo-extra/runbot/runbot.py
sed -i  '/'matplotlib'/d' $DEPS/odoo-extra/runbot/__openerp__.py

# Change cron interval to avoid interference with tests
sed -i "s/'interval_number'>1</'interval_number'>60</g" $DEPS/odoo-extra/runbot/runbot.xml

# Disabling test_crawl (native runbot fail)
find ${HOME} -name __init__.py -exec sed -i  "/import test_crawl/d" {} \;
