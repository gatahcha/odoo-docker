# Backend Theme Studio

Custom Odoo 19 backend module: glass-style surfaces, optional wallpaper, and an in-UI **Theme customizer** (paint-brush icon in the systray).

## Install

1. Ensure `backend_theme_studio` is under `addons/` (mounted as `/mnt/extra-addons`).
2. **Apps** → **Update Apps List** → search **Backend Theme Studio** → **Install**.

If you do not see it, remove the **Apps** filter (the default Apps screen only lists modules with **Application** = true; this module is flagged as an app so it shows there). You can also use the **Extra** filter or search by technical name `backend_theme_studio`.

## Upgrade after code changes

```bash
docker compose exec -u odoo odoo python odoo-bin -c /etc/odoo/odoo.conf -d TEST1 \
  -u backend_theme_studio --stop-after-init --http-port=0 --workers=0
docker compose restart odoo
```

Replace `TEST1` if your database name differs.

## Behavior

- **Systray** (top bar): paint-brush icon opens/closes the customizer panel.
- **Save** writes settings to **browser `localStorage`** (keyed by database and user id). No server-side model is used in this version.
- **Preview** reloads the last **saved** snapshot from `localStorage` (discards unsaved slider changes since the last Save).
- **Reset** restores the default built-in preset (does not clear `localStorage` until you click **Save**).

Default look is **blue-tinted** (navbar gradient + light blue content surfaces). Use **Reset** in the customizer to pick the **Odoo blue** preset if colors look stale after an upgrade.


## Uninstall

Uninstalling the module removes the UI; clear `localStorage` keys prefixed with `backend_theme_studio` if you need to remove leftover client-side settings.
