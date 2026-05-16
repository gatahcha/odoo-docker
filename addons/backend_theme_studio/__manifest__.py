# -*- coding: utf-8 -*-
{
    "name": "Backend Theme Studio",
    "version": "19.0.1.0.5",
    "category": "Customization",
    "summary": "Glass-style backend theme with CSS variables and an in-UI customizer panel.",
    "depends": ["web", "web_apps_home"],
    "license": "LGPL-3",
    "installable": True,
    # application=True so the module appears under the default Apps filter (search_default_app).
    "application": True,
    "auto_install": False,
    "assets": {
        "web.assets_backend": [
            "backend_theme_studio/static/src/scss/theme_backend.scss",
            "backend_theme_studio/static/src/theme_presets.js",
            "backend_theme_studio/static/src/theme_customizer_service.js",
            "backend_theme_studio/static/src/theme_customizer/theme_customizer.xml",
            "backend_theme_studio/static/src/theme_customizer/theme_customizer.js",
            "backend_theme_studio/static/src/systray/theme_systray_item.xml",
            "backend_theme_studio/static/src/systray/theme_systray_item.js",
            "backend_theme_studio/static/src/main.js",
        ],
    },
}
