# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools import str2bool


class BackendThemeStudioController(http.Controller):
    @http.route(
        "/backend_theme_studio/web_apps_home_setting",
        type="jsonrpc",
        auth="user",
    )
    def web_apps_home_setting(self, enabled=None):
        """Read or update web_apps_home.enabled (Settings users only)."""
        if not request.env.user.has_group("base.group_system"):
            return {"ok": False, "error": "access_denied"}
        param = request.env["ir.config_parameter"].sudo()
        if enabled is None:
            return {
                "ok": True,
                "enabled": str2bool(param.get_param("web_apps_home.enabled", "True"), True),
            }
        param.set_param("web_apps_home.enabled", "True" if enabled else "False")
        return {"ok": True, "enabled": bool(enabled)}
