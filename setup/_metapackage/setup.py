import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-runbot-addons",
    description="Meta package for oca-runbot-addons Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-runbot_build_instructions',
        'odoo8-addon-runbot_coverage',
        'odoo8-addon-runbot_gitlab',
        'odoo8-addon-runbot_language',
        'odoo8-addon-runbot_pylint',
        'odoo8-addon-runbot_secure',
        'odoo8-addon-runbot_skip_tests',
        'odoo8-addon-runbot_website_display',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
