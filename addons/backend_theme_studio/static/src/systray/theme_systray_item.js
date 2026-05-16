/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ThemeSystrayItem extends Component {
    static template = "backend_theme_studio.ThemeSystrayItem";
    static props = {};

    setup() {
        this.theme = useService("theme_customizer");
    }

    onClick() {
        this.theme.togglePanel();
    }
}

registry.category("systray").add(
    "backend_theme_studio.theme_systray",
    { Component: ThemeSystrayItem },
    { sequence: 45 }
);
