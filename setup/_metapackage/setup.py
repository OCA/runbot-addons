import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-runbot-addons",
    description="Meta package for oca-runbot-addons Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-runbot_build_instructions',
        'odoo9-addon-runbot_relative',
        'odoo9-addon-runbot_skip_tests',
        'odoo9-addon-runbot_travis2docker',
        'odoo9-addon-runbot_website_display',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
