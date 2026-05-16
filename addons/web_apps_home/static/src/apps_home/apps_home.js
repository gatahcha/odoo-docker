/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";
import { imageUrl } from "@web/core/utils/urls";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class AppsHome extends Component {
    static template = "web_apps_home.AppsHome";
    static props = { ...standardActionServiceProps };

    setup() {
        this.menuService = useService("menu");
        this.ui = useService("ui");
        this.state = useState({ apps: [] });
        onWillStart(async () => {
            this.state.apps = await this.getAppsForHome();
        });
    }

    /**
     * Override in extensions (e.g. pinned ordering) without duplicating setup wiring.
     * @returns {Promise<object[]>}
     */
    async getAppsForHome() {
        return this.menuService.getApps();
    }

    get welcomeMessage() {
        return _t("Welcome back, %s!", user.name || "");
    }

    get userName() {
        return user.name || "";
    }

    get userAvatarUrl() {
        if (!user.partnerId) {
            return "";
        }
        return imageUrl("res.partner", user.partnerId, "avatar_128", { unique: user.writeDate });
    }

    get appSwitcherTitle() {
        return _t("Apps menu");
    }

    get emptyLabel() {
        return _t("No applications are available for your user.");
    }

    get title() {
        return _t("Your apps");
    }

    async onAppSwitcherClick() {
        const all = this.menuService.getAll();
        let target = all.find((m) => m.xmlid === "base.menu_module_tree" && m.actionID);
        if (!target) {
            const apps = this.menuService.getApps();
            target = apps.find((a) => a.actionID) || apps[0];
        }
        if (!target?.actionID) {
            return;
        }
        await this.menuService.selectMenu(target);
    }

    async openApp(app) {
        await this.menuService.selectMenu(app);
    }

    /**
     * @param {KeyboardEvent} ev
     * @param {object} app
     */
    async onAppKeydown(ev, app) {
        if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            await this.openApp(app);
        }
    }
}

registry.category("actions").add("web_apps_home.main", AppsHome);
