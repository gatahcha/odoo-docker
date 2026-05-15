/** @odoo-module **/

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class AppsPinField extends Component {
    static template = "apps_pins.AppsPinField";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
    }

    get moduleName() {
        return this.props.record.data.name;
    }

    get pinned() {
        return Boolean(this.props.record.data.is_pinned);
    }

    get cssClass() {
        return this.pinned ? "o_apps_pin_btn--pinned" : "o_apps_pin_btn--unpinned";
    }

    get title() {
        return this.pinned ? _t("Unpin application") : _t("Pin application");
    }

    async onClick(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        if (!this.moduleName) {
            return;
        }
        await this.orm.call("ir.module.module", "apps_toggle_pin", [this.moduleName]);
        await this.action.doAction({ type: "ir.actions.client", tag: "soft_reload" });
    }
}

export const appsPinField = {
    component: AppsPinField,
    displayName: _t("Apps pin"),
    supportedTypes: ["boolean"],
};

registry.category("fields").add("apps_pin", appsPinField);
