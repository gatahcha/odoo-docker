# -*- coding: utf-8 -*-
{
    "name": "Web Apps Home",
    "version": "19.0.1.6.0",
    "category": "Hidden",
    "summary": "Bare /odoo opens an installed-apps launcher (with navbar) when the user has no Home Action.",
    "depends": ["web"],
    "data": [
        "data/ir_actions_client.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "web_apps_home/static/src/apps_home/apps_home_palette.scss",
            "web_apps_home/static/src/apps_home/apps_home.scss",
            "web_apps_home/static/src/apps_home/apps_home.xml",
            "web_apps_home/static/src/apps_home/apps_home.js",
            "web_apps_home/static/src/navbar/navbar_apps_menu.scss",
            "web_apps_home/static/src/navbar/navbar_apps_menu.xml",
            "web_apps_home/static/src/navbar/navbar_patch.js",
        ],
    },
    "license": "LGPL-3",
    "author": "Custom",
    "installable": True,
    "application": False,
    "auto_install": False,
}
