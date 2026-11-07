import { api } from "./api.js";
import { openPlayer } from "./player.js";
import { speech } from "./speech.js";
import { toast } from "./ui.js";

export const store = { lang: "de", settings: {}, ai: false, state: null };

export async function refreshState() {
  const st = await api.get("/api/state");
  store.state = st; store.settings = st.settings; store.ai = st.ai;
  store.lang = st.settings.current_lang || "de";
  speech.rate = Number(st.settings.speech_rate) || 0.95;
  speech.preferred = { de: st.settings.voice_de || "", fr: st.settings.voice_fr || "" };
  document.documentElement.classList.toggle("no-colors", st.settings.grammar_colors === false);
  return st;
}

export const go = (hash) => { location.hash = hash; };
const rerender = () => window.dispatchEvent(new HashChangeEvent("hashchange"));

export async function setLang(lang) {
  store.lang = lang;
  await api.put("/api/settings", { values: { current_lang: lang } });
  rerender();
}

export async function startTestout(uid, part) {
  const lesson = await api.get(`/api/lesson/${uid}/${part}?mode=testout`);
  const sessionId = Math.random().toString(36).slice(2, 12);
  openPlayer({
    title: `Test out: ${lesson.title} · ${lesson.part}`, steps: lesson.steps, lang: lesson.lang, kind: "testout", sessionId,
    onComplete: () => api.post("/api/testout/finish", { unit_id: uid, part, session_id: sessionId }),
    onRetry: () => startLesson(uid, part),
    onFinish: async () => { await refreshState(); rerender(); },
  });
}

export async function startLesson(uid, part) {
  const lesson = await api.get(`/api/lesson/${uid}/${part}`);
  openPlayer({
    title: `${lesson.title} · ${lesson.part}`, steps: lesson.steps, lang: lesson.lang, kind: "lesson",
    onComplete: () => api.post("/api/progress", { unit_id: uid, part }),
    onFinish: async () => { await refreshState(); rerender(); },
  });
}

export async function startSession({ focus = null, kind = "mix", size = null, title } = {}) {
  const lang = store.lang;
  const q = new URLSearchParams({ lang }); if (size) q.set("size", size); if (focus) q.set("focus", focus);
  const s = await api.get(`/api/session?${q}`);
  if (s.empty || !s.exercises.length) { toast(s.reason || "Nothing to practise yet. Start a lesson first!"); return; }
  openPlayer({
    title: title || (focus ? `Focus: ${focus.replace("_", " ")}` : "Daily mix"), lang, kind,
    steps: s.exercises.map((ex) => ({ step: "exercise", ex })),
    onFinish: async () => { await refreshState(); rerender(); },
  });
}

export async function startCheckpoint() {
  const lang = store.lang;
  const c = await api.get(`/api/checkpoint?lang=${lang}`);
  if (c.empty) { toast(c.reason); return; }
  openPlayer({
    title: "Checkpoint test", lang, kind: "checkpoint", sessionId: c.session_id,
    steps: c.exercises.map((ex) => ({ step: "exercise", ex })),
    onComplete: () => api.post("/api/checkpoint/finish", { lang, session_id: c.session_id }),
    onFinish: async () => { await refreshState(); rerender(); },
  });
}

/** Plan blocks and recommendations carry an action; this runs it. */
export function runAction(a, lang = store.lang) {
  const switchTo = lang !== store.lang ? setLang(lang) : Promise.resolve();
  return switchTo.then(() => {
    switch (a.type) {
      case "mix": return startSession({ kind: "mix" });
      case "lesson": return startLesson(a.unit_id, a.part);
      case "unit": return go(`#/unit/${store.lang}-${String(a.stage).padStart(2, "0")}`);
      case "drill": return startSession({ focus: a.focus, kind: `drill-${a.focus}`, size: 12 });
      case "gaps": return startSession({ focus: "gaps", kind: "gaps", title: "Fix my gaps" });
      case "checkpoint": return startCheckpoint();
      case "write": return go("#/write");
      case "offline": return toast("Away from the screen: put on a podcast or show in " + (lang === "de" ? "German" : "French") + ".");
    }
  });
}
