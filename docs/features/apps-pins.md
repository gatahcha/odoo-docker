# Feature: Apps Pins (`apps_pins`)

The **Apps Pins and My Adds** module (`apps_pins`) customizes the Odoo **Apps** experience: pinning applications per user, defaulting the Apps action to the pinned filter, optional kanban and list controls, and a **My Adds** stub list for future connectors.

**Technical name:** `apps_pins`  
**Declared version:** 19.0.x (see `addons/apps_pins/__manifest__.py`)  
**Dependencies:** `base`, `base_import_module`, `web`

## What it does

1. **Pinned applications** — Users can pin apps by technical module name. Pinned apps appear when the Apps UI filters by module type **Pinned**, in the order pins were saved.
2. **Default Apps view** — The main Apps window action is adjusted so the search panel defaults to **Pinned** (empty until the user pins apps or changes the sidebar).
3. **List and Kanban UI** — A custom field widget adds a pin control in list view; Kanban gets a pin button and a menu action to toggle pin (restricted to administrators for those server actions; see below).
4. **My Adds (stub)** — Three placeholder “applications” are returned for the **My Adds** filter to reserve UX space for future integrations (WhatsApp, barcode utilities, custom reports). They are not installable modules.

## How pinning is stored

Pins are **not** stored on `res.users` (to avoid requiring write access on users for internal accounts). Instead, each user’s pin list is stored in **`ir.config_parameter`**:

- Key pattern: `apps_pins.names.<user_id>`
- Value: JSON array of technical module name strings.
- Maximum **80** names; duplicates and invalid entries are stripped when saving.

The computed boolean field **`is_pinned`** on `ir.module.module` reflects whether the row’s `name` appears in that list (with a custom search implementation for filtering).

## Server API

- **`apps_toggle_pin(module_name)`** (model `ir.module.module`, `@api.model`) — Toggles the given technical name in the current user’s pin list and returns `{ pinned_names, is_pinned }`. Used from the list widget via RPC.
- **`action_apps_toggle_pin`** — Button/menu action used from Kanban; resolves the module name from context (`module_name`) or the current record; performs toggle and returns a client action `soft_reload` to refresh the UI.

## Apps list and search behavior

The module overrides **`web_search_read`** on `ir.module.module`:

- **Filter `module_type = myadds`** — Returns a fixed set of stub dictionaries (virtual negative IDs), not database records.
- **Filter `module_type = pinned`** — Builds the result from:
  - Installed application modules in the database whose names are pinned, and
  - Optionally merged metadata from **`_get_modules_from_apps`** for pinned names that are not local DB rows (for example remote/industry apps), with graceful logging if remote fetch fails.

Official remote rows may have `module_type` normalized for display (for example `industries` shown as `official`).

## UI surfaces

| Location | Behavior |
|----------|------------|
| Apps list | Column on `is_pinned` with OWL widget **`apps_pin`** (thumb icon); click toggles pin and soft-reloads. |
| Apps Kanban | Pin button on the card; dropdown menu entry **Toggle pin** (both use `action_apps_toggle_pin` with `module_name` in context). |
| Search panel / default action | Inherited Apps action sets default context so Apps opens with **Pinned** as the default module type filter. |

Kanban pin button and dropdown item are limited to **`base.group_system`** in the view XML.

## Assets

Backend assets registered in the manifest:

- `apps_pins/static/src/scss/apps_pins.scss`
- `apps_pins/static/src/fields/apps_pin_field.js`
- `apps_pins/static/src/fields/apps_pin_field.xml`

After changes, upgrade the module and refresh assets as you normally would for Odoo web changes.

## Install and upgrade

1. Ensure `addons_path` includes `/mnt/extra-addons` (default in this repo’s `odoo.conf`).
2. **Apps** → update apps list → install **Apps Pins and My Adds** (or install from command line).

After pulling code updates for this module:

```bash
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d YOUR_DB -u apps_pins --stop-after-init
```

The manifest summary also reminds operators to upgrade with **`-u apps_pins`** after pulls when behavior changes.

## Tests

Automated tests live under `addons/apps_pins/tests/` (for example pinned `web_search_read` behavior and My Adds stubs). Run them with your usual Odoo test invocation for the database and tags you use.

## Assets for screenshots

Place screenshots or diagrams under [docs/assets/](../assets/) and link them from this file if you add visuals later.
