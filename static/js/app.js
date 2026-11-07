import { api } from "./api.js";
import { store, refreshState, setLang } from "./store.js";
import { flag, h, toast } from "./ui.js";
import * as V from "./views.js";

const routes = {
  today: (v) => V.today(v), journey: (v) => V.journey(v), unit: (v, a) => V.unit(v, a), practice: (v) => V.practice(v),
  insights: (v) => V.insights(v), plan: (v) => V.plan(v), write: (v, a) => V.write(v, a), colors: (v) => V.colors(v), settings: (v) => V.settings(v),
};

function drawLangSwitch() {
  const el = document.getElementById("langSwitch");
  el.innerHTML = "";
  for (const [code, name] of [["de", "Deutsch"], ["fr", "Français"]]) {
    el.append(h("button", { role: "tab", "aria-selected": store.lang === code, class: store.lang === code ? "on" : "", onclick: () => setLang(code) }, flag(code), name));
  }
  const foot = document.getElementById("navFoot");
  const t = store.state.today[store.lang];
  foot.innerHTML = "";
  foot.append(h("div", { class: "row small" }, h("span", { class: "chip sun" }, "🔥 ", store.state.streak), h("span", { class: "chip" }, `${t.xp} XP today`)));
}

async function route() {
  const [, name = "today", arg] = location.hash.replace(/^#\/?/, "#/").split("/");
  const view = document.getElementById("view");
  document.querySelectorAll(".tabs a").forEach((a) => a.classList.toggle("on", a.dataset.tab === (name === "unit" ? "journey" : name)));
  try {
    await refreshState();
    drawLangSwitch();
    await (routes[name] || routes.today)(view, arg);
  } catch (e) {
    console.error(e);
    view.innerHTML = "";
    view.append(h("div", { class: "empty" }, h("h2", {}, "Something went wrong"), h("p", { class: "muted" }, e.message), h("a", { class: "btn", href: "#/today" }, "Back to today")));
  }
  view.focus({ preventScroll: true });
  window.scrollTo({ top: 0 });
}

// Study-time tracking: count time only while you're actually interacting with a lesson / practice.
let lastInput = Date.now();
["pointerdown", "keydown"].forEach((ev) => addEventListener(ev, () => { lastInput = Date.now(); }, { passive: true }));
setInterval(() => {
  const studying = !document.getElementById("player").hidden || location.hash.startsWith("#/write");
  if (studying && document.visibilityState === "visible" && Date.now() - lastInput < 60000) {
    api.post("/api/activity", { lang: store.lang, seconds: 15 }).catch(() => {});
  }
}, 15000);

addEventListener("hashchange", route);
route();
addEventListener("unhandledrejection", (e) => toast(e.reason?.message || "Error"));
