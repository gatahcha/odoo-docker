# -*- coding: utf-8 -*-
import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Domain

_logger = logging.getLogger(__name__)

MAX_PINS = 80
MYADDS_STUB_IDS = (-10, -11, -12)


def _domain_has_module_type_value(domain, value):
    if not domain:
        return False
    for condition in Domain(domain).iter_conditions():
        if condition.field_expr == 'module_type':
            if condition.operator == '=' and condition.value == value:
                return True
            if condition.operator == 'in':
                vals = condition.value
                if isinstance(vals, (list, tuple, set)):
                    if value in vals and len(vals) == 1:
                        return True
                elif vals == value:
                    return True
    return False


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    module_type = fields.Selection(selection_add=[
        ('pinned', 'Pinned'),
        ('myadds', 'My Adds'),
    ])

    is_pinned = fields.Boolean(
        string='Pinned',
        compute='_compute_is_pinned',
        search='_search_is_pinned',
    )

    def _compute_is_pinned(self):
        pinset = set(self._apps_pins_get_names())
        for mod in self:
            mod.is_pinned = mod.name in pinset

    def _search_is_pinned(self, operator, value):
        names = self._apps_pins_get_names()
        if operator == '=' and value:
            return [('name', 'in', names)] if names else [('id', '=', False)]
        if operator == '=' and not value:
            return [('name', 'not in', names)] if names else []
        if operator == '!=' and value:
            return [('name', 'not in', names)] if names else []
        if operator == '!=' and not value:
            return [('name', 'in', names)] if names else [('id', '=', False)]
        return []

    # -------------------------------------------------------------------------
    # Pin storage (ir.config_parameter: internal users cannot write res.users)
    # -------------------------------------------------------------------------

    def _apps_pins_param_key(self):
        return 'apps_pins.names.%s' % (self.env.uid,)

    def _apps_pins_get_names(self):
        raw = self.env['ir.config_parameter'].sudo().get_param(self._apps_pins_param_key(), '[]')
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            data = []
        if not isinstance(data, list):
            return []
        return [str(x) for x in data if isinstance(x, str) and x][:MAX_PINS]

    def _apps_pins_set_names(self, names):
        clean = []
        seen = set()
        for n in names:
            if not isinstance(n, str) or not n or n in seen:
                continue
            seen.add(n)
            clean.append(n)
            if len(clean) >= MAX_PINS:
                break
        self.env['ir.config_parameter'].sudo().set_param(
            self._apps_pins_param_key(),
            json.dumps(clean),
        )
        self.invalidate_model(['is_pinned'])

    @api.model
    @api.model
    def apps_toggle_pin(self, module_name):
        """Toggle pin by technical module name (for RPC from list widget)."""
        if not module_name or not isinstance(module_name, str):
            raise UserError(_('Invalid module name.'))
        names = list(self._apps_pins_get_names())
        if module_name in names:
            names.remove(module_name)
            pinned = False
        else:
            names.append(module_name)
            pinned = True
        self._apps_pins_set_names(names)
        return {'pinned_names': names, 'is_pinned': pinned}

    def action_apps_toggle_pin(self):
        """Kanban ⋮ menu: context carries module_name for virtual rows (id -1)."""
        name = self.env.context.get('module_name')
        rec = self[:1]
        if not name and rec.id and rec.id > 0:
            name = rec.name
        if not name:
            raise UserError(_('Could not determine which application to pin.'))
        self.env['ir.module.module'].apps_toggle_pin(name)
        return {'type': 'ir.actions.client', 'tag': 'soft_reload'}

    def _apps_pins_myadds_stub_dicts(self, fields_list):
        stubs = [
            {
                'id': MYADDS_STUB_IDS[0],
                'name': 'apps_pins_whatsapp_stub',
                'shortdesc': _('WhatsApp integration (stub)'),
                'summary': _('Placeholder entry for a future WhatsApp connector.'),
                'author': 'My Adds',
                'website': '',
                'state': 'uninstallable',
                'module_type': 'myadds',
                'application': True,
                'is_pinned': False,
            },
            {
                'id': MYADDS_STUB_IDS[1],
                'name': 'apps_pins_barcode_stub',
                'shortdesc': _('Barcode utilities (stub)'),
                'summary': _('Placeholder entry for barcode-related tools.'),
                'author': 'My Adds',
                'website': '',
                'state': 'uninstallable',
                'module_type': 'myadds',
                'application': True,
                'is_pinned': False,
            },
            {
                'id': MYADDS_STUB_IDS[2],
                'name': 'apps_pins_custom_reports_stub',
                'shortdesc': _('Custom reports pack (stub)'),
                'summary': _('Placeholder for user-specific reporting add-ons.'),
                'author': 'My Adds',
                'website': '',
                'state': 'uninstallable',
                'module_type': 'myadds',
                'application': True,
                'is_pinned': False,
            },
        ]
        keys = set(fields_list or []) | {'id', 'name'}
        out = []
        for row in stubs:
            out.append({k: row[k] for k in keys if k in row})
        return out

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        if _domain_has_module_type_value(domain, 'myadds'):
            records = self._apps_pins_myadds_stub_dicts(list(specification.keys()))
            return {
                'length': len(records),
                'records': records[offset: offset + (limit or len(records))],
            }

        if _domain_has_module_type_value(domain, 'pinned'):
            return self._web_search_read_pinned(
                domain, specification, offset=offset, limit=limit, order=order, count_limit=count_limit,
            )

        return super().web_search_read(domain, specification, offset=offset, limit=limit, order=order, count_limit=count_limit)

    def _web_search_read_pinned(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        pin_order = self._apps_pins_get_names()
        pin_set = set(pin_order)
        if not pin_set:
            return {'length': 0, 'records': []}

        fields_name = list(specification.keys())

        db_modules = self.search([('application', '=', True), ('name', 'in', list(pin_set))], order=order)
        by_name = {}
        for mod in db_modules:
            by_name[mod.name] = mod

        missing = [n for n in pin_order if n in pin_set and n not in by_name]
        remote_list = []
        if missing:
            try:
                remote_list = self._get_modules_from_apps(
                    fields_name, 'industries', False, [('name', 'in', missing)], limit=len(missing) * 2,
                )
            except UserError as e:
                _logger.info('Pinned merge: remote fetch failed: %s', e)
            except Exception as e:  # noqa: BLE001
                _logger.warning('Pinned merge: remote fetch error: %s', e)

        for row in remote_list:
            n = row.get('name')
            if n and n not in by_name:
                by_name[n] = row

        ordered_keys = [n for n in pin_order if n in by_name]
        for n, val in by_name.items():
            if n not in ordered_keys:
                ordered_keys.append(n)

        records_out = []
        for n in ordered_keys:
            val = by_name[n]
            if isinstance(val, models.Model):
                data = val.web_read(specification)
                if data:
                    row = data[0]
                    row['is_pinned'] = True
                    records_out.append(row)
            else:
                row = dict(val)
                row['is_pinned'] = True
                if row.get('module_type') == 'industries':
                    row['module_type'] = 'official'
                records_out.append(row)

        total = len(records_out)
        slice_ = records_out[offset: offset + (limit or total)]
        return {
            'length': total,
            'records': slice_,
        }
