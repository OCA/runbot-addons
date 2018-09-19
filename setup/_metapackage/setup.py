import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-runbot-addons",
    description="Meta package for oca-runbot-addons Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-runbot_buildout',
        'odoo11-addon-runbot_gitlab',
        'odoo11-addon-runbot_send_email',
        'odoo11-addon-runbot_subject_skip',
        'odoo11-addon-runbot_travis2docker',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
