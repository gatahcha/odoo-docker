# -*- coding: utf-8 -*-
{
    'name': 'Apps Pins and My Adds',
    'version': '19.0.1.0.2',
    'category': 'Hidden',
    'summary': 'Pinned apps sidebar, My Adds stub, Kanban pin icon, Apps opens on Pinned; upgrade with -u apps_pins after pull.',
    'depends': ['base', 'base_import_module', 'web'],
    'data': [
        'views/ir_module_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'apps_pins/static/src/scss/apps_pins.scss',
            'apps_pins/static/src/fields/apps_pin_field.js',
            'apps_pins/static/src/fields/apps_pin_field.xml',
        ],
    },
    'license': 'LGPL-3',
    'author': 'Custom',
    'installable': True,
    'application': False,
    'auto_install': False,
}
