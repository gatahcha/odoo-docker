/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { SearchModel } from "@web/search/search_model";

function isMainAppsModuleAction(env) {
    if (env?.config?.actionXmlId === "base.open_module_tree") {
        return true;
    }
    const aid = env?.config?.actionId;
    const expected = session.apps_open_module_tree_action_id;
    return Boolean(aid && expected && aid === expected);
}

/**
 * Main Apps (base.open_module_tree) persists search state in the URL, including the
 * search panel "module_type" (Pinned / All / …). After we removed the default from the
 * action, old state still restored "pinned". Reset that category to All (false) on load.
 */
patch(SearchModel.prototype, {
    async load(config) {
        const cfg = { ...config };
        const isApps = cfg.resModel === "ir.module.module" && isMainAppsModuleAction(this.env);
        if (isApps && cfg.state && Array.isArray(cfg.state.sections)) {
            cfg.state = { ...cfg.state, sections: cfg.state.sections.map((entry) => {
                const [sid, section] = entry;
                if (section?.type === "category" && section.fieldName === "module_type") {
                    return [sid, { ...section, activeValueId: false }];
                }
                return entry;
            }) };
        }
        await super.load(cfg);
        if (!isApps) {
            return;
        }
        const cat = [...this.sections.values()].find(
            (s) => s.type === "category" && s.fieldName === "module_type"
        );
        if (cat?.activeValueId === "pinned") {
            cat.activeValueId = false;
            await this._notify();
        }
    },
});
