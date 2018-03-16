#!/bin/bash

set -v

export DEPS=${HOME}/dependencies

# Disabling matplotlib by https://github.com/travis-ci/travis-ci/issues/4948
sed -i '/from matplotlib.font_manager import FontProperties/d' $DEPS/runbot/runbot/controllers/badge.py
sed -i '/from matplotlib.textpath import TextToPath/d' $DEPS/runbot/runbot/controllers/badge.py
sed -i  '/'matplotlib'/d' $DEPS/runbot/runbot/__manifest__.py

# Change cron interval to avoid interference with tests
sed -i "s/\"interval_number\">1</\"interval_number\">60</g" $DEPS/runbot/runbot/data/runbot_cron.xml

# Disabling test_crawl (native runbot fail)
find ${HOME} -name __init__.py -exec sed -i  "/import test_crawl/d" {} \;

# Download docker image required
if [[ "${TESTS}" == "1"  ]]; then docker pull vauxoo/odoo-80-image-shippable-auto; fi
