/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useBus, useService } from "@web/core/utils/hooks";

export class ThemeCustomizer extends Component {
    static template = "backend_theme_studio.ThemeCustomizer";
    static props = {};

    setup() {
        this.theme = useService("theme_customizer");
        this.ui = useService("ui");
        this.notification = useService("notification");
        this.user = useService("user");
        this.state = this.theme.state;
        this.presets = this.theme.getPresets();
        this.appsHome = useState({ canEdit: false, enabled: true, loaded: false });
        onWillStart(async () => {
            const canEdit = await this.user.hasGroup("base.group_system");
            this.appsHome.canEdit = canEdit;
            if (canEdit) {
                const res = await rpc("/backend_theme_studio/web_apps_home_setting", {});
                if (res.ok) {
                    this.appsHome.enabled = res.enabled;
                }
                this.appsHome.loaded = true;
            }
        });
        useBus(this.theme.bus, "UPDATED", () => this.render());
        this.sectionState = useState({ open: "sidebar" });
        this.sections = [
            {
                id: "sidebar",
                label: "Side bar",
                fields: [{ key: "sidebarAlpha", label: "Transparency" }],
            },
            {
                id: "navbar",
                label: "App tab / navbar",
                fields: [{ key: "navAlpha", label: "Transparency" }],
            },
            {
                id: "body",
                label: "Body / content",
                fields: [
                    { key: "bodyAlpha", label: "Body surface" },
                    { key: "actionAlpha", label: "Action area" },
                ],
            },
        ];
    }

    get openSection() {
        return this.sectionState.open;
    }

    toggleSection(id) {
        this.sectionState.open = this.sectionState.open === id ? null : id;
    }

    close() {
        this.theme.setPanelOpen(false);
    }

    setMode(mode) {
        this.theme.setMode(mode);
    }

    applyPreset(id) {
        this.theme.applyPreset(id);
    }

    onBgUrl(ev) {
        this.theme.patch({ bgUrl: ev.target.value });
    }

    patch(partial) {
        this.theme.patch(partial);
    }

    preview() {
        this.theme.previewFromSaved();
    }

    reset() {
        this.theme.resetToFactory();
    }

    save() {
        this.theme.save();
    }

    get closeBtnClass() {
        return this.state.mode === "dark" ? "btn-close btn-close-white" : "btn-close";
    }

    presetClass(p) {
        return p.id === this.state.presetId ? "bts-preset-swatch active" : "bts-preset-swatch";
    }

    onFieldInput(key, ev) {
        const val = parseFloat(ev.target.value);
        this.theme.patch({ [key]: val });
    }

    presetStyle(p) {
        if (p.id === "light-odoo-blue") {
            return "background:linear-gradient(135deg,rgba(59,130,246,0.55),rgba(147,197,253,0.85))";
        }
        const a = p.mode === "dark" ? "40,45,58" : "255,255,255";
        const b = p.mode === "dark" ? "24,26,32" : "230,235,245";
        return `background:linear-gradient(135deg,rgba(${a},0.9),rgba(${b},0.7))`;
    }

    async onWebAppsHomeToggle(ev) {
        const enabled = ev.target.checked;
        const res = await rpc("/backend_theme_studio/web_apps_home_setting", { enabled });
        if (res.ok) {
            this.appsHome.enabled = res.enabled;
            this.notification.add(
                "Reload the page so bare /odoo picks up the new apps-home setting.",
                { type: "info" }
            );
        } else {
            const cur = await rpc("/backend_theme_studio/web_apps_home_setting", {});
            if (cur.ok) {
                this.appsHome.enabled = cur.enabled;
            }
            this.notification.add("You need Settings access to change this option.", { type: "warning" });
        }
    }
}

registry.category("main_components").add("backend_theme_studio.ThemeCustomizer", {
    Component: ThemeCustomizer,
});
