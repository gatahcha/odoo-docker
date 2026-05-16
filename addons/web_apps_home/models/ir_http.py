# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.tools import str2bool


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def session_info(self):
        result = super().session_info()
        if not result.get("uid"):
            return result
        IrConfigSudo = self.env["ir.config_parameter"].sudo()
        enabled = str2bool(IrConfigSudo.get_param("web_apps_home.enabled", "True"), True)
        if not enabled:
            return result
        if result.get("home_action_id"):
            return result
        action = self.env.ref(
            "web_apps_home.action_client_apps_home",
            raise_if_not_found=False,
        )
        if action:
            result["home_action_id"] = action.id
        return result
