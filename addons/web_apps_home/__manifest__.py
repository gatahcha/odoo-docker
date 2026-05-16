# -*- coding: utf-8 -*-
{
    "name": "Web Apps Home",
    "version": "19.0.1.1.0",
    "category": "Hidden",
    "summary": "Bare /odoo opens a fullscreen installed-apps launcher when the user has no Home Action.",
    "depends": ["web"],
    "data": [
        "data/ir_actions_client.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "web_apps_home/static/src/apps_home/apps_home.scss",
            "web_apps_home/static/src/apps_home/apps_home.xml",
            "web_apps_home/static/src/apps_home/apps_home.js",
        ],
    },
    "license": "LGPL-3",
    "author": "Custom",
    "installable": True,
    "application": False,
    "auto_install": False,
}
