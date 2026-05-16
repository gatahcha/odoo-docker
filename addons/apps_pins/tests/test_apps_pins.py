# -*- coding: utf-8 -*-
from ast import literal_eval
from unittest.mock import patch

import odoo.tests
from odoo.tests.common import TransactionCase, new_test_user


@odoo.tests.tagged('post_install', '-at_install', 'apps_pins')
class TestAppsPins(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrModule = cls.env['ir.module.module']

    def test_myadds_no_stub_names(self):
        spec = {'id': {}, 'name': {}, 'module_type': {}}
        res = self.IrModule.web_search_read([('module_type', '=', 'myadds')], spec)
        names = {r['name'] for r in res['records']}
        for stub in (
            'apps_pins_whatsapp_stub',
            'apps_pins_barcode_stub',
            'apps_pins_custom_reports_stub',
        ):
            self.assertNotIn(stub, names)

    def test_myadds_web_search_read_normalizes_module_type(self):
        mod = self.IrModule.search([('application', '=', True)], limit=1)
        if not mod:
            self.skipTest('no application module in database')
        tech = mod.name
        spec = {'id': {}, 'name': {}, 'module_type': {}, 'state': {}}
        with patch.object(
            type(self.IrModule),
            '_apps_pins_myadds_module_names',
            return_value=frozenset({tech}),
        ):
            res = self.IrModule.web_search_read([('module_type', '=', 'myadds')], spec)
        match = [r for r in res['records'] if r['name'] == tech]
        self.assertTrue(match)
        self.assertEqual(match[0]['module_type'], 'myadds')

    def test_myadds_empty_when_no_candidates(self):
        spec = {'id': {}, 'name': {}}
        with patch.object(type(self.IrModule), '_apps_pins_myadds_module_names', return_value=frozenset()):
            res = self.IrModule.web_search_read([('module_type', '=', 'myadds')], spec)
        self.assertEqual(res['length'], 0)
        self.assertEqual(res['records'], [])

    def test_myadds_combined_domain_excludes_nonmatching(self):
        mod = self.IrModule.search([('application', '=', True)], limit=1)
        if not mod:
            self.skipTest('no application module in database')
        tech = mod.name
        spec = {'id': {}, 'name': {}}
        with patch.object(
            type(self.IrModule),
            '_apps_pins_myadds_module_names',
            return_value=frozenset({tech}),
        ):
            res = self.IrModule.web_search_read(
                [('module_type', '=', 'myadds'), ('name', '=', '__no_such_module__')],
                spec,
            )
        self.assertEqual(res['length'], 0)

    def test_append_names_for_user_merge_dedupe(self):
        u = new_test_user(self.env, 'apps_pin_append_u', groups='base.group_system')
        try:
            self.IrModule._apps_pins_append_names_for_user(u, ['alpha'])
            self.IrModule._apps_pins_append_names_for_user(u, ['alpha', 'beta'])
            names = self.IrModule.with_user(u)._apps_pins_get_names()
            self.assertEqual(names, ['alpha', 'beta'])
        finally:
            self.env['ir.config_parameter'].sudo().set_param(
                self.IrModule.with_user(u)._apps_pins_param_key(), '[]'
            )

    def test_append_names_for_user_respects_max_pins(self):
        u = new_test_user(self.env, 'apps_pin_append_max', groups='base.group_system')
        max_pins = 80  # keep in sync with apps_pins.models.ir_module_module.MAX_PINS
        try:
            base = [f'myadds_pad_{i}' for i in range(max_pins - 1)]
            self.IrModule.with_user(u)._apps_pins_set_names(base)
            self.IrModule._apps_pins_append_names_for_user(u, ['last_ok', 'overflow'])
            names = self.IrModule.with_user(u)._apps_pins_get_names()
            self.assertEqual(len(names), max_pins)
            self.assertIn('last_ok', names)
            self.assertNotIn('overflow', names)
        finally:
            self.env['ir.config_parameter'].sudo().set_param(
                self.IrModule.with_user(u)._apps_pins_param_key(), '[]'
            )

    def test_pinned_official_db(self):
        mod = self.IrModule.search([('application', '=', True)], limit=1)
        if not mod:
            self.skipTest('no application module in database')
        tech = mod.name
        self.IrModule.apps_toggle_pin(tech)
        self.assertIn(tech, self.IrModule._apps_pins_get_names())
        spec = {
            'id': {}, 'name': {}, 'shortdesc': {}, 'state': {}, 'module_type': {},
            'is_pinned': {}, 'application': {},
        }
        res = self.IrModule.web_search_read([('module_type', '=', 'pinned')], spec)
        names = [r['name'] for r in res['records']]
        self.assertIn(tech, names)
        self.assertTrue(all(r.get('is_pinned') for r in res['records']))
        self.IrModule.apps_toggle_pin(tech)
        self.assertNotIn(tech, self.IrModule._apps_pins_get_names())

    def test_pinned_merge_remote_mock(self):
        fake_remote = [{
            'id': -1,
            'name': 'zz_apps_pins_remote_only',
            'shortdesc': 'Remote Only',
            'state': 'uninstalled',
            'module_type': 'industries',
            'application': True,
        }]
        self.IrModule._apps_pins_set_names(['zz_apps_pins_remote_only'])
        try:
            with patch.object(
                type(self.IrModule),
                '_get_modules_from_apps',
                return_value=fake_remote,
            ):
                spec = {'id': {}, 'name': {}, 'shortdesc': {}, 'state': {}, 'module_type': {}, 'is_pinned': {}}
                res = self.IrModule.web_search_read([('module_type', '=', 'pinned')], spec)
            names = [r['name'] for r in res['records']]
            self.assertEqual(names, ['zz_apps_pins_remote_only'])
            self.assertEqual(res['records'][0]['module_type'], 'official')
        finally:
            self.IrModule._apps_pins_set_names([])

    def test_toggle_pin_isolation(self):
        u1 = new_test_user(self.env, 'apps_pin_u1', groups='base.group_system')
        u2 = new_test_user(self.env, 'apps_pin_u2', groups='base.group_system')
        try:
            self.IrModule.with_user(u1).apps_toggle_pin('base')
            names_u1 = self.IrModule.with_user(u1)._apps_pins_get_names()
            names_u2 = self.IrModule.with_user(u2)._apps_pins_get_names()
            self.assertIn('base', names_u1)
            self.assertNotIn('base', names_u2)
        finally:
            self.env['ir.config_parameter'].sudo().set_param(
                self.IrModule.with_user(u1)._apps_pins_param_key(), '[]'
            )

    def test_industries_domain_still_routed(self):
        """Ensure super() path for industries is still used (apps_pins runs first then super)."""
        with patch.object(
            type(self.IrModule),
            '_get_modules_from_apps',
            return_value=[],
        ) as mock_get:
            spec = {'id': {}, 'name': {}}
            self.IrModule.web_search_read([('module_type', '=', 'industries')], spec)
        mock_get.assert_called()

    def test_apps_action_context_defaults_all_searchpanel(self):
        act = self.env.ref('base.open_module_tree').sudo()
        ctx = act.context
        if isinstance(ctx, str):
            ctx = literal_eval(ctx.strip()) if ctx.strip() else {}
        self.assertFalse(ctx.get('searchpanel_default_module_type'))
        self.assertTrue(ctx.get('search_default_app'))

    def test_home_launcher_includes_apps_and_settings_when_visible(self):
        mids = self.env['ir.http']._apps_pins_home_launcher_menu_ids()
        roots = self.env['ir.ui.menu'].get_user_roots()
        apps_id = self.env['ir.model.data']._xmlid_to_res_id('base.menu_management', raise_if_not_found=False)
        settings_id = self.env['ir.model.data']._xmlid_to_res_id('base.menu_administration', raise_if_not_found=False)
        if apps_id and apps_id in roots.ids:
            self.assertEqual(mids[0], apps_id)
        if settings_id and settings_id in roots.ids:
            self.assertIn(settings_id, mids)
            if apps_id and apps_id in roots.ids:
                self.assertEqual(mids[1], settings_id)
            else:
                self.assertEqual(mids[0], settings_id)

    def test_home_launcher_includes_sale_when_pinned_and_installed(self):
        sale_mod = self.IrModule.search([('name', '=', 'sale')])
        if not sale_mod or sale_mod.state != 'installed':
            self.skipTest('sale module not installed')
        sale_menu = self.env.ref('sale.sale_menu_root', raise_if_not_found=False)
        if not sale_menu or sale_menu.id not in self.env['ir.ui.menu'].get_user_roots().ids:
            self.skipTest('sale root menu not visible for this user')
        self.IrModule.apps_toggle_pin('sale')
        try:
            mids = self.IrModule.apps_pins_get_home_root_menu_ids()
            self.assertIn(sale_menu.id, mids)
        finally:
            self.IrModule.apps_toggle_pin('sale')

    def test_home_launcher_rpc_matches_http_helper(self):
        self.assertEqual(
            self.IrModule.apps_pins_get_home_root_menu_ids(),
            self.env['ir.http']._apps_pins_home_launcher_menu_ids(),
        )

    def test_search_panel_includes_pinned_selection_value(self):
        res = self.IrModule.search_panel_select_range(
            'module_type',
            category_domain=[],
            filter_domain=[],
            enable_counters=False,
            expand=True,
            hierarchize=True,
            limit=None,
            search_domain=[],
        )
        ids = {v['id'] for v in res['values']}
        self.assertIn('pinned', ids)
