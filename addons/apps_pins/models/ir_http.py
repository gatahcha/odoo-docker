# -*- coding: utf-8 -*-
from odoo import api, models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @api.model
    def session_info(self):
        result = super().session_info()
        if not result.get('uid'):
            return result
        # Initial payload; home screen still calls apps_pins_get_home_root_menu_ids() via RPC
        # so pins after login appear without requiring a new session.
        result['apps_pins_home_menu_ids'] = self.apps_pins_get_home_root_menu_ids()
        act = self.env.ref('base.open_module_tree', raise_if_not_found=False)
        if act:
            result['apps_open_module_tree_action_id'] = act.id
        return result

    @api.model
    def apps_pins_get_home_root_menu_ids(self):
        """RPC: ordered root menu ids for /odoo — Apps, Settings, then pinned+installed apps.

        Kept on ``ir.http`` for a single entry point; safe for the logged-in user (menus filtered
        like ``get_user_roots``).
        """
        return self._apps_pins_home_launcher_menu_ids()

    def _apps_pins_home_launcher_menu_ids(self):
        Menu = self.env['ir.ui.menu']
        roots = Menu.get_user_roots()
        if not roots:
            return []
        root_ids = set(roots.ids)
        xmlids = roots._get_menuitems_xmlids()
        IrModelData = self.env['ir.model.data'].sudo()

        ordered = []
        seen = set()

        # Always show main entry points when the user can see them (same roots as navbar).
        for xid in ('base.menu_management', 'base.menu_administration'):
            mid = IrModelData._xmlid_to_res_id(xid, raise_if_not_found=False)
            if mid and mid in root_ids and mid not in seen:
                ordered.append(mid)
                seen.add(mid)

        Module = self.env['ir.module.module'].sudo()
        pin_names = list(Module._apps_pins_get_names())
        if not pin_names:
            return ordered

        installed = set(Module.search([
            ('name', 'in', pin_names),
            ('state', '=', 'installed'),
        ]).mapped('name'))
        pin_ordered = [n for n in pin_names if n in installed]
        if not pin_ordered:
            return ordered

        module_to_menu = {}
        for menu in roots.sorted('sequence'):
            xid_str = xmlids.get(menu.id, '')
            if not xid_str or '.' not in xid_str:
                continue
            mod = xid_str.split('.', 1)[0]
            if mod in pin_ordered and mod not in module_to_menu:
                module_to_menu[mod] = menu.id

        for mod in pin_ordered:
            mid = module_to_menu.get(mod)
            if mid and mid not in seen:
                ordered.append(mid)
                seen.add(mid)

        return ordered
