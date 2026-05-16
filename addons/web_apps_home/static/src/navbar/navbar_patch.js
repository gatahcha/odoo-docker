/** @odoo-module **/

import { useExternalListener } from "@odoo/owl";

import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useBus } from "@web/core/utils/hooks";
import { NavBar } from "@web/webclient/navbar/navbar";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        useExternalListener(window, "keydown", (ev) => {
            if (ev.key === "Escape" && this.state.isAppMenuSidebarOpened) {
                this._closeAppMenuSidebar();
            }
        });
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", () => this.render());
    },

    get appsHomeCubesTitle() {
        return _t("Home");
    },

    /**
     * Bare `/odoo` launcher: do not surface the last opened app in the navbar (brand / sections).
     */
    _isWebAppsHomeLauncher() {
        const action = this.actionService.currentController?.action;
        return Boolean(action?.type === "ir.actions.client" && action.tag === "web_apps_home.main");
    },

    get isWebAppsLauncher() {
        return this._isWebAppsHomeLauncher();
    },

    set isWebAppsLauncher(_) {},

    get currentApp() {
        if (this._isWebAppsHomeLauncher()) {
            return undefined;
        }
        return this.menuService.getCurrentApp();
    },

    /**
     * When opening with no current app (e.g. /odoo launcher), show the all-apps list with icons.
     */
    _openAppMenuSidebar() {
        const opening = !this.state.isAppMenuSidebarOpened;
        this.state.isAppMenuSidebarOpened = opening;
        if (
            opening &&
            (!this.menuService.getCurrentApp() || this._isWebAppsHomeLauncher())
        ) {
            this.state.isAllAppsMenuOpened = true;
        }
    },

    onAppsHomeCubesClick(ev) {
        ev.preventDefault();
        this._closeAppMenuSidebar();
        browser.location.assign("/odoo");
    },
});
