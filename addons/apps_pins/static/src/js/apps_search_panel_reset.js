/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SearchModel } from "@web/search/search_model";

/**
 * Main Apps (base.open_module_tree) persists search state in the URL, including the
 * search panel "module_type" (Pinned / All / …). After we removed the default from the
 * action, old state still restored "pinned". Reset that category to All (false) on load.
 */
patch(SearchModel.prototype, {
    async load(config) {
        const cfg = { ...config };
        if (
            cfg.resModel === "ir.module.module" &&
            this.env?.config?.actionXmlId === "base.open_module_tree" &&
            cfg.state &&
            Array.isArray(cfg.state.sections)
        ) {
            cfg.state = { ...cfg.state, sections: cfg.state.sections.map((entry) => {
                const [sid, section] = entry;
                if (section?.type === "category" && section.fieldName === "module_type") {
                    return [sid, { ...section, activeValueId: false }];
                }
                return entry;
            }) };
        }
        return super.load(cfg);
    },
});
