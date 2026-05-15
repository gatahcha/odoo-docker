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

    def test_myadds_stub(self):
        spec = {'id': {}, 'name': {}, 'shortdesc': {}, 'state': {}, 'module_type': {}, 'is_pinned': {}}
        res = self.IrModule.web_search_read(
            [('module_type', '=', 'myadds')],
            spec,
        )
        self.assertEqual(res['length'], 3)
        names = {r['name'] for r in res['records']}
        self.assertIn('apps_pins_whatsapp_stub', names)
        self.assertTrue(all(r['module_type'] == 'myadds' for r in res['records']))

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

    def test_apps_action_context_defaults_pinned_searchpanel(self):
        act = self.env.ref('base.open_module_tree').sudo()
        ctx = act.context
        if isinstance(ctx, str):
            ctx = literal_eval(ctx.strip()) if ctx.strip() else {}
        self.assertEqual(ctx.get('searchpanel_default_module_type'), 'pinned')
        self.assertTrue(ctx.get('search_default_app'))

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
