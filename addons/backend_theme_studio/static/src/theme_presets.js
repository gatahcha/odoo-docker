/** @odoo-module **/

/**
 * @typedef {Object} ThemePreset
 * @property {string} id
 * @property {string} name
 * @property {"light"|"dark"} mode
 * @property {string} [bgUrl] optional wallpaper URL
 * @property {number} bgDim 0-1 overlay darkness on top of wallpaper
 * @property {number} navAlpha
 * @property {number} sidebarAlpha
 * @property {number} actionAlpha
 * @property {number} bodyAlpha
 * @property {number} blurPx
 */

/** @type {ThemePreset[]} */
export const PRESETS = [
    {
        id: "light-odoo-blue",
        name: "Odoo blue",
        mode: "light",
        bgUrl: "",
        bgDim: 0.18,
        navAlpha: 0.94,
        sidebarAlpha: 0.9,
        actionAlpha: 0.93,
        bodyAlpha: 0.95,
        blurPx: 10,
    },
    {
        id: "light-glass",
        name: "Light glass",
        mode: "light",
        bgUrl: "",
        bgDim: 0.25,
        navAlpha: 0.82,
        sidebarAlpha: 0.78,
        actionAlpha: 0.88,
        bodyAlpha: 0.9,
        blurPx: 14,
    },
    {
        id: "dark-glass",
        name: "Dark glass",
        mode: "dark",
        bgUrl: "",
        bgDim: 0.55,
        navAlpha: 0.72,
        sidebarAlpha: 0.68,
        actionAlpha: 0.78,
        bodyAlpha: 0.82,
        blurPx: 16,
    },
    {
        id: "high-contrast",
        name: "Solid (readable)",
        mode: "light",
        bgUrl: "",
        bgDim: 0,
        navAlpha: 1,
        sidebarAlpha: 1,
        actionAlpha: 1,
        bodyAlpha: 1,
        blurPx: 0,
    },
    {
        id: "ocean-wallpaper",
        name: "Ocean preset",
        mode: "light",
        bgUrl: "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=1920&q=80",
        bgDim: 0.35,
        navAlpha: 0.75,
        sidebarAlpha: 0.72,
        actionAlpha: 0.85,
        bodyAlpha: 0.88,
        blurPx: 12,
    },
];

/**
 * @param {string} id
 * @returns {ThemePreset|undefined}
 */
export function getPresetById(id) {
    return PRESETS.find((p) => p.id === id);
}

/**
 * @returns {ThemePreset}
 */
export function defaultPreset() {
    return PRESETS[0];
}

/**
 * @param {ThemePreset} preset
 * @param {string} [bgUrlOverride]
 * @returns {Record<string, string>}
 */
export function presetToCssVars(preset, bgUrlOverride) {
    const url = (bgUrlOverride ?? preset.bgUrl ?? "").trim();
    const bgImage = url ? `url("${url.replace(/"/g, '\\"')}")` : "none";
    return {
        "--bts-bg-image": bgImage,
        "--bts-bg-dim": String(preset.bgDim ?? 0),
        "--bts-nav-alpha": String(preset.navAlpha ?? 0.85),
        "--bts-sidebar-alpha": String(preset.sidebarAlpha ?? 0.8),
        "--bts-action-alpha": String(preset.actionAlpha ?? 0.88),
        "--bts-body-alpha": String(preset.bodyAlpha ?? 0.9),
        "--bts-blur": `${preset.blurPx ?? 12}px`,
    };
}
