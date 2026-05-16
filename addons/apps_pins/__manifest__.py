# -*- coding: utf-8 -*-
{
    'name': 'Apps Pins and My Adds',
    'version': '19.0.1.4.0',
    'category': 'Hidden',
    'summary': '/odoo home: Apps + Settings, then pinned installed apps (RPC-fresh). Pins, My Adds, Apps=All. Upgrade with -u apps_pins after pull.',
    'depends': ['base', 'base_import_module', 'web', 'web_apps_home'],
    'data': [
        'views/ir_module_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'apps_pins/static/src/scss/apps_pins.scss',
            'apps_pins/static/src/fields/apps_pin_field.js',
            'apps_pins/static/src/fields/apps_pin_field.xml',
            'apps_pins/static/src/js/apps_search_panel_reset.js',
            'apps_pins/static/src/web_apps_home/apps_home_pinned.js',
        ],
    },
    'license': 'LGPL-3',
    'author': 'Custom',
    'installable': True,
    'application': False,
    'auto_install': False,
}
