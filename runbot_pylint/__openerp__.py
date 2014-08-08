{
    'name': 'Runbot Pylint',
    'category': 'Website',
    'summary': 'Runbot',
    'version': '1.0',
    'description': "Runbot",
    'author': 'OpenERP SA',
    'depends': ['runbot'],
    'external_dependencies': {
        'bin': ['pylint'],
    },
    'data': [
        "view/runbot_pylint_view.xml"
    ],
    'installable': True,
}
