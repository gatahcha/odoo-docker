/** @odoo-module **/

import { EventBus, reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { browser } from "@web/core/browser/browser";
import { PRESETS, defaultPreset, getPresetById } from "./theme_presets";

const STORAGE_VERSION = 1;
const STORAGE_PREFIX = "backend_theme_studio";

function storageKey() {
    const uid = session.uid ?? "anon";
    const db = session.db ?? "nodb";
    return `${STORAGE_PREFIX}.v${STORAGE_VERSION}:${db}:${uid}`;
}

/**
 * @param {import("./theme_presets").ThemePreset} base
 */
function stateFromPreset(base) {
    return {
        mode: base.mode,
        presetId: base.id,
        bgUrl: base.bgUrl || "",
        bgDim: base.bgDim,
        navAlpha: base.navAlpha,
        sidebarAlpha: base.sidebarAlpha,
        actionAlpha: base.actionAlpha,
        bodyAlpha: base.bodyAlpha,
        blurPx: base.blurPx,
    };
}

function readStored() {
    try {
        const raw = browser.localStorage.getItem(storageKey());
        if (!raw) {
            return null;
        }
        const data = JSON.parse(raw);
        if (!data || data.version !== STORAGE_VERSION) {
            return null;
        }
        return data.payload;
    } catch {
        return null;
    }
}

function writeStored(payload) {
    browser.localStorage.setItem(
        storageKey(),
        JSON.stringify({ version: STORAGE_VERSION, payload })
    );
}

function applyToDocument(state) {
    const root = document.documentElement;
    const body = document.body;
    if (!body) {
        return;
    }
    body.classList.add("bts-enabled");
    root.dataset.btsMode = state.mode;
    root.style.setProperty("--bts-nav-alpha", String(state.navAlpha));
    root.style.setProperty("--bts-sidebar-alpha", String(state.sidebarAlpha));
    root.style.setProperty("--bts-action-alpha", String(state.actionAlpha));
    root.style.setProperty("--bts-body-alpha", String(state.bodyAlpha));
    root.style.setProperty("--bts-blur", `${state.blurPx}px`);
    root.style.setProperty("--bts-bg-dim", String(state.bgDim));
    const url = (state.bgUrl || "").trim();
    root.style.setProperty(
        "--bts-bg-image",
        url ? `url("${url.replace(/"/g, '\\"')}")` : "none"
    );
}

function cloneThemeState(s) {
    return {
        mode: s.mode,
        presetId: s.presetId,
        bgUrl: s.bgUrl,
        bgDim: s.bgDim,
        navAlpha: s.navAlpha,
        sidebarAlpha: s.sidebarAlpha,
        actionAlpha: s.actionAlpha,
        bodyAlpha: s.bodyAlpha,
        blurPx: s.blurPx,
    };
}

export const themeCustomizerService = {
    dependencies: [],
    start() {
        const bus = new EventBus();
        const base = defaultPreset();
        const stored = readStored();
        const initial = stored
            ? {
                  mode: stored.mode ?? base.mode,
                  presetId: stored.presetId ?? base.id,
                  bgUrl: stored.bgUrl ?? "",
                  bgDim: stored.bgDim ?? base.bgDim,
                  navAlpha: stored.navAlpha ?? base.navAlpha,
                  sidebarAlpha: stored.sidebarAlpha ?? base.sidebarAlpha,
                  actionAlpha: stored.actionAlpha ?? base.actionAlpha,
                  bodyAlpha: stored.bodyAlpha ?? base.bodyAlpha,
                  blurPx: stored.blurPx ?? base.blurPx,
              }
            : stateFromPreset(base);

        const state = reactive({
            ...initial,
            panelOpen: false,
        });

        let savedSnapshot = cloneThemeState(state);

        function notifyUi() {
            bus.trigger("UPDATED");
        }

        function syncDom() {
            applyToDocument(state);
            notifyUi();
        }

        syncDom();

        return {
            bus,
            state,
            togglePanel() {
                state.panelOpen = !state.panelOpen;
                bus.trigger("PANEL", { open: state.panelOpen });
                notifyUi();
            },
            setPanelOpen(open) {
                state.panelOpen = open;
                bus.trigger("PANEL", { open: state.panelOpen });
                notifyUi();
            },
            applyPreset(presetId) {
                const p = getPresetById(presetId);
                if (!p) {
                    return;
                }
                Object.assign(state, {
                    presetId: p.id,
                    mode: p.mode,
                    bgUrl: p.bgUrl || "",
                    bgDim: p.bgDim,
                    navAlpha: p.navAlpha,
                    sidebarAlpha: p.sidebarAlpha,
                    actionAlpha: p.actionAlpha,
                    bodyAlpha: p.bodyAlpha,
                    blurPx: p.blurPx,
                });
                syncDom();
            },
            setMode(mode) {
                state.mode = mode;
                syncDom();
            },
            patch(partial) {
                Object.assign(state, partial);
                syncDom();
            },
            previewFromSaved() {
                Object.assign(state, cloneThemeState(savedSnapshot));
                syncDom();
            },
            resetToFactory() {
                const d = defaultPreset();
                Object.assign(state, stateFromPreset(d));
                syncDom();
            },
            save() {
                const payload = {
                    mode: state.mode,
                    presetId: state.presetId,
                    bgUrl: state.bgUrl,
                    bgDim: state.bgDim,
                    navAlpha: state.navAlpha,
                    sidebarAlpha: state.sidebarAlpha,
                    actionAlpha: state.actionAlpha,
                    bodyAlpha: state.bodyAlpha,
                    blurPx: state.blurPx,
                };
                writeStored(payload);
                savedSnapshot = cloneThemeState(state);
                bus.trigger("SAVED");
                notifyUi();
            },
            syncDom,
            getPresets() {
                return PRESETS;
            },
        };
    },
};

registry.category("services").add("theme_customizer", themeCustomizerService);
