/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { useService } from "@web/core/utils/hooks";

import { AppsHome } from "@web_apps_home/apps_home/apps_home";

/**
 * Replaces web_apps_home launcher: Apps + Settings (when visible), then pinned+installed apps.
 * Menu order is loaded via RPC so pins after login show without a full session reload.
 */
export class AppsHomePinned extends AppsHome {
    setup() {
        this.orm = useService("orm");
        super.setup();
    }

    /** @override */
    async getAppsForHome() {
        const allApps = this.menuService.getApps();
        let sequence = session.apps_pins_home_menu_ids || [];
        try {
            sequence = await this.orm.call("ir.module.module", "apps_pins_get_home_root_menu_ids", []);
        } catch {
            // offline / access edge: keep session copy
        }
        const byId = Object.fromEntries(allApps.map((a) => [a.id, a]));
        return sequence.map((id) => byId[id]).filter(Boolean);
    }

    /** @override */
    get emptyLabel() {
        return _t(
            "Pin installed applications in Apps (thumb icon) to list them here after Apps and Settings."
        );
    }
}

registry.category("actions").add("web_apps_home.main", AppsHomePinned, { force: true });
