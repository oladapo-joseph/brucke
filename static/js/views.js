import { api } from "./api.js";
import { bridgeBoxes, grammarTable, writingFeedback } from "./player.js";
import { speech } from "./speech.js";
import { store, go, runAction, startLesson, startSession, startCheckpoint, startTestout, refreshState } from "./store.js";
import { ICON, SKILL_ICON, accentBar, flag, gclass, h, md, pct, ring, savedTheme, setTheme, shape, tagged, tipOn, toast, wordLabel, GENDER_NAME } from "./ui.js";

const LNAME = { de: "German", fr: "French" };
const GREET = { de: ["Guten Morgen", "Guten Tag", "Guten Abend"], fr: ["Bonjour", "Bonjour", "Bonsoir"] };
const SKILLS = ["listening", "speaking", "reading", "writing"];

function greeting(lang) { const hr = new Date().getHours(); return GREET[lang][hr < 11 ? 0 : hr < 18 ? 1 : 2]; }
function loading(view) { view.innerHTML = ""; view.append(h("div", { class: "empty" }, h("div", { class: "spinner" }))); }


function zoneLabel(c) {
  if (c.recent_accuracy == null) return "Not enough answers yet";
  return { coasting: "Coasting: it's about to get tougher", struggling: "Struggling: easing off", "sweet spot": "In the sweet spot" }[c.zone];
}

export function challengeCard(c) {
  const card = h("div", { class: "card stack rec" }, h("div", { class: "section-head" }, h("h3", {}, `Challenge level ${c.level} · ${c.name}`),
    h("span", { class: "chip" }, c.auto ? "auto" : "fixed in Settings")), h("p", { class: "muted small" }, c.desc));
  // a single-series meter: recent accuracy against the 70–93% band the app aims for
  const acc = c.recent_accuracy;
  const meter = h("div", { class: "zone-meter" }, h("div", { class: "band", style: { left: "70%", width: "23%" } }),
    acc != null ? h("div", { class: "mark", style: { left: `${Math.round(acc * 100)}%` } }) : null);
  tipOn(meter, acc != null ? `Last ${c.window} answers: <b>${pct(acc)}</b><br>Sweet spot: 70–93% (target 85%)` : "Answer a few more questions");
  card.append(h("div", { class: "row small" }, h("b", {}, acc != null ? pct(acc) : "–"), h("span", { class: "muted" }, zoneLabel(c))), meter,
    h("div", { class: "row small muted", style: { justifyContent: "space-between" } }, h("span", {}, "0%"), h("span", {}, "sweet spot"), h("span", {}, "100%")));
  if (c.history?.length) card.append(h("details", { class: "fold" }, h("summary", { class: "small" }, "Level history"),
    ...c.history.slice().reverse().map((x) => h("div", { class: "small muted" }, `${new Date(x.ts * 1000).toLocaleDateString()} · ${x.from} → ${x.to}: ${x.reason}`))));
  card.append(h("p", { class: "small muted" }, "Learning is fastest at about 85% correct. Near 100% you're coasting, so the app makes you produce more (type and speak from memory), with trickier options and decoys. Below 70% it eases off."));
  return card;
}

function paceLine(p) {
  if (!p) return null;
  if (p.finish_week) {
    const early = p.weeks_early;
    return early >= 1 ? `At your real pace you'll finish B1 around week ${Math.round(p.finish_week)}, ${Math.round(early)} weeks early.`
      : early <= -1 ? `At your current pace B1 lands around week ${Math.round(p.finish_week)}. The catch-up blocks will close the gap.`
      : "Right on pace for B1 in week 26.";
  }
  return p.status === "ahead" ? `You're ${p.ahead} stages ahead of schedule.` : "Your pace forecast appears after your first week.";
}

// ====================================================================== TODAY
export async function today(view) {
  loading(view);
  const lang = store.lang;
  const [plan, ins] = await Promise.all([api.get("/api/schedule"), api.get(`/api/insights?lang=${lang}`)]);
  const st = store.state.today[lang];
  const lp = plan.langs[lang];
  const other = plan.order.find((l) => l !== lang);
  view.innerHTML = "";

  const notStarted = lp.minutes === 0;
  view.append(h("div", { class: "stack", style: { gap: "6px" } },
    h("div", { class: "row" }, h("span", { class: "chip level" }, plan.phase[2]), h("span", { class: "chip" }, `Week ${plan.week} of ${plan.weeks_total}`), h("span", { class: "chip" }, plan.weekday)),
    h("div", { class: "hello" }, `${greeting(lang)}! `, h("em", {}, notStarted ? `${LNAME[lang]} starts in week ${lp.starts_week}` : `${lp.minutes} min of ${LNAME[lang]} today`)),
    h("p", { class: "muted" }, plan.phase[3])));

  // hero: continue + stats
  const cur = lp.current_stage;
  const next = lp.blocks.find((b) => b.action.type === "lesson")?.action;
  const deco = h("div", { class: "deco", html: `<svg viewBox="0 0 200 160"><rect class="s1" x="20" y="60" width="54" height="54" rx="6" fill="var(--m)"/><circle class="s2" cx="120" cy="60" r="32" fill="var(--f)"/><path class="s3" d="M150 150 L185 90 L200 150z" fill="var(--n)"/></svg>` });
  const contCard = h("div", { class: "card continue stack" }, deco,
    h("span", { class: "tiny muted" }, `Stage ${cur} · ${notStarted ? "preview" : "your current unit"}`),
    h("h2", { style: { fontSize: "1.8rem", maxWidth: "70%" } }, ins && (await unitTitle(lang, cur))),
    h("p", { class: "muted", style: { maxWidth: "70%" } }, lp.behind > 0 ? `You're ${lp.behind} stage${lp.behind > 1 ? "s" : ""} behind schedule. Today's plan adds a catch-up block.`
      : lp.fast_track ? "You're moving fast. Today's plan adds a fast-track push." : "On track. Keep the rhythm going.", " ", paceLine(lp.pace) || ""),
    h("div", { class: "row", style: { position: "relative" } }, h("span", { class: "chip sun" }, `Challenge Lv ${lp.challenge.level} · ${lp.challenge.name}`),
      lp.stretch ? h("span", { class: "chip sun" }, "🚀 Stretch goal unlocked") : null),
    h("div", { class: "row", style: { position: "relative" } },
      next ? h("button", { class: "btn sun big", onclick: () => startLesson(next.unit_id, next.part) }, "Continue lesson", h("span", { html: ICON.arrow })) :
        h("button", { class: "btn sun big", onclick: () => go(`#/unit/${lang}-${String(cur).padStart(2, "0")}`) }, "Open stage ", cur),
      h("button", { class: "btn ghost", onclick: () => startSession({ kind: "mix" }) }, `Daily mix · ${st.due} due`)));
  const stats = h("div", { class: "card grid g4", style: { gridTemplateColumns: "repeat(2,1fr)", alignContent: "center" } },
    h("div", { class: "stat" }, h("b", {}, h("span", { class: "flame" }, "🔥"), " ", store.state.streak), h("span", { class: "muted small" }, "day streak")),
    h("div", { class: "stat" }, h("b", {}, st.xp), h("span", { class: "muted small" }, "XP today")),
    h("div", { class: "stat" }, h("b", {}, `${st.minutes}`, h("span", { class: "muted", style: { fontSize: "1rem" } }, `/${lp.minutes}`)), h("span", { class: "muted small" }, "minutes today")),
    h("div", { class: "stat" }, h("b", {}, ins.items_learned), h("span", { class: "muted small" }, `items learned · ${ins.items_solid} solid`)));
  view.append(h("div", { class: "hero" }, contCard, stats));

  // plan
  const planCard = (lng, data) => h("div", { class: "card stack" },
    h("div", { class: "section-head" }, h("h2", { class: "row" }, flag(lng, true), `${LNAME[lng]} plan`), h("span", { class: "muted small" }, data.minutes ? `${data.minutes} min` : `starts week ${data.starts_week}`)),
    data.blocks.length ? h("div", { class: "plan-list" }, data.blocks.map((b) => h("button", { class: "plan-item" + (b.done ? " done" : ""), onclick: () => runAction(b.action, lng) },
      h("span", { class: "tick", html: b.done ? ICON.check.replace("<svg", '<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="3"') : "" }),
      h("span", { class: "title" }, b.title), h("span", { class: "mins" }, b.minutes ? `${b.minutes}′` : "")))) :
      h("p", { class: "muted" }, "Not started yet. German gets a head start so the basics don't get mixed up. You can preview French in the Journey tab any time."));
  view.append(h("div", { class: "section" }, h("div", { class: "grid g2" }, planCard(lang, lp), planCard(other, plan.langs[other]))));

  // skills
  view.append(h("div", { class: "section" }, h("div", { class: "section-head" }, h("h2", {}, "Your four skills"), h("a", { href: "#/insights", class: "small" }, "See insights →")),
    h("div", { class: "skills" }, ins.skills.map((s) => h("button", { class: "skill", style: { border: 0, cursor: "pointer" }, onclick: () => startSession({ focus: s.skill, kind: `drill-${s.skill}`, size: 12 }), title: `Drill ${s.skill}` },
      h("div", { style: { position: "relative", display: "grid", placeItems: "center" } }, ring(s.mastery), h("span", { style: { position: "absolute" }, html: SKILL_ICON[s.skill] })),
      h("b", { style: { textTransform: "capitalize" } }, s.skill), h("span", { class: "muted small" }, `${pct(s.mastery)} mastery · ${pct(s.accuracy)} acc.`))))));

  if (ins.recommendations?.length) {
    view.append(h("div", { class: "section" }, h("h2", {}, "Coach says"), h("div", { class: "grid g2" }, ins.recommendations.map(recCard))));
  }
}

async function unitTitle(lang, stage) {
  const d = await api.get(`/api/units/${lang}-${String(stage).padStart(2, "0")}`);
  return d.has_content ? d.title : d.outline.title;
}

function recCard(r) {
  return h("div", { class: "card rec" }, h("h3", {}, r.title), h("p", { class: "muted", html: md(r.body) }),
    h("div", {}, h("button", { class: "btn ghost", onclick: () => runAction(r.action) }, "Start", h("span", { html: ICON.arrow }))));
}

// ====================================================================== JOURNEY
export async function journey(view) {
  loading(view);
  const lang = store.lang;
  const data = await api.get(`/api/units?lang=${lang}`);
  view.innerHTML = "";
  view.append(h("div", { class: "stack", style: { gap: "6px" } }, h("h1", { class: "row" }, flag(lang, true), `Your ${LNAME[lang]} journey`),
    h("p", { class: "muted" }, `26 stages from your first sounds to B1 independence. You're on stage ${data.current_stage}; the schedule expects stage ${data.expected_stage || "–"} this week.`)));
  const shapes = ["f", "m", "n", "pl"];
  if (data.pace) view.append(h("p", { class: "muted" }, paceLine(data.pace)));
  for (const lv of store.state.levels) {
    if (!data.units.some((u) => u.stage >= lv.stages[0] && u.stage <= lv.stages[1])) continue;
    const band = h("div", { class: "level-band" + (lv.stretch ? " stretch" : "") }, h("div", { class: "level-head" }, h("span", { class: "chip level" }, lv.code), h("h2", {}, lv.name)),
      lv.stretch ? h("p", { class: "muted small" }, "🚀 Unlocked because you're ahead of schedule. Extra scope towards B2, written by Claude when you open a stage.") : null);
    const path = h("div", { class: "path" });
    data.units.filter((u) => u.stage >= lv.stages[0] && u.stage <= lv.stages[1]).forEach((u) => {
      const state = u.complete ? "done" : u.stage === data.current_stage ? "current" : u.has_content ? "todo" : "locked";
      const sh = shapes[u.stage % 4];
      const discSvg = { f: '<circle cx="35" cy="35" r="31"/>', m: '<rect x="6" y="6" width="58" height="58" rx="14"/>', n: '<path d="M35 4 L67 62 Q68 66 64 66 H6 Q2 66 3 62z"/>', pl: '<path d="M35 3 L67 35 L35 67 L3 35z"/>' }[sh];
      path.append(h("a", { class: `node ${state}`, href: `#/unit/${u.id}` },
        h("div", { class: "disc" }, h("span", { html: `<svg class="bg" viewBox="0 0 70 70">${discSvg}</svg>` }), h("span", { class: "num" }, u.complete ? "✓" : u.stage)),
        h("div", { class: "meta" }, h("b", {}, u.title), h("span", { class: "muted small" }, u.has_content ? (u.native || u.can_do?.[0] || "") : `Outline: ${u.grammar_focus}`),
          u.has_content ? h("div", { class: "bar" }, h("i", { style: { width: `${(u.done / u.parts) * 100}%` } })) : h("span", { class: "chip", style: { justifySelf: "start" } }, store.ai ? "✨ generate with Claude" : "needs content"))));
    });
    band.append(path);
    view.append(band);
  }
}

// ====================================================================== UNIT
export async function unit(view, uid) {
  loading(view);
  const d = await api.get(`/api/units/${uid}`);
  const lang = uid.slice(0, 2);
  view.innerHTML = "";
  view.append(h("a", { href: "#/journey", class: "small muted" }, "← Journey"));
  if (!d.has_content) {
    const o = d.outline;
    view.append(h("div", { class: "card stack", style: { marginTop: "14px" } },
      h("div", { class: "row" }, h("span", { class: "chip level" }, o.level), h("span", { class: "chip" }, `Stage ${o.stage}`)),
      h("h1", {}, o.title), h("p", {}, h("b", {}, "Grammar focus: "), o.grammar_focus), h("p", {}, h("b", {}, "Goal: "), o.can_do[0]), h("p", { class: "muted" }, "Themes: " + o.themes),
      d.ai ? genButton(lang, o.stage) : h("div", { class: "card flat stack" }, h("b", {}, "This stage is an outline."),
        h("p", { class: "muted" }, "Set ANTHROPIC_API_KEY and restart to let Claude write it (about a minute). Or add it by hand in app/content/" + lang + ".py using the same format as stages 1–8."))));
    return;
  }
  const nextPart = d.parts.find((p) => !p.done);
  view.append(h("div", { class: "unit-head", style: { marginTop: "14px" } },
    h("div", { class: "row" }, h("span", { class: "chip level" }, d.level), h("span", { class: "chip" }, `Stage ${d.stage}`), flag(lang), d.source === "claude" ? h("span", { class: "chip sun" }, "✨ written by Claude") : null),
    h("h1", {}, d.title, " ", h("span", { class: "muted", style: { fontWeight: 500 } }, "· " + d.native)),
    h("ul", { class: "stack", style: { paddingLeft: "20px", margin: 0, gap: "4px" } }, d.can_do.map((c) => h("li", {}, c))),
    d.recognisable ? h("div", { class: "bridge same", style: { justifySelf: "start" } }, h("b", {}, "🌉 Head start: "),
      `${d.recognisable} of the ${d.vocab_total} words here link to English you already know. Look for the bridge on each card.`) : null));

  view.append(h("div", { class: "section" }, h("div", { class: "section-head" }, h("h2", {}, "Lessons"), h("span", { class: "muted small" }, `${d.parts.filter((p) => p.done).length}/${d.parts.length} done · ~6 min each`)),
    h("div", { class: "parts" }, d.parts.map((p) => h("div", { class: "part" + (p.done ? " done" : "") + (p === nextPart ? " next" : "") },
      h("span", { class: "n" }, p.done ? "✓" : p.n + 1), h("div", {}, h("b", {}, p.title), h("div", { class: "muted small" }, p.kind === "final" ? "reading passage + free writing" : `${p.count} items`)),
      h("div", { class: "row", style: { gap: "8px" } },
        !p.done && p.kind !== "final" ? h("button", { class: "btn line testout-btn", title: "Already know this? Pass a quick check (85%) and skip ahead", onclick: () => startTestout(d.id, p.n) }, "I know this") : null,
        h("button", { class: p === nextPart ? "btn sun" : "btn ghost", onclick: () => startLesson(d.id, p.n) }, p.done ? "Redo" : "Start")))))));

  if (d.grammar.length) view.append(h("div", { class: "section" }, h("h2", {}, "Grammar ideas"),
    ...d.grammar.map((g, k) => h("details", { class: "card fold gnote", open: k === 0 }, h("summary", {}, g.title), h("div", { class: "body", html: md(g.body) }), g.table ? grammarTable(g.table) : null))));

  if (d.letters?.length) view.append(h("div", { class: "section" }, h("div", { class: "section-head" }, h("h2", {}, "Alphabet"),
      h("span", { class: "muted small" }, "Tap a letter to hear its name. ⚠ = a trap for English speakers")),
    h("div", { class: "alphabet" }, d.letters.map((l) => h("button", { class: "abc" + (l.tricky ? " tricky" : ""), title: `${l.name}: sounds like “${l.like}”${l.tip ? "\n" + l.tip : ""}`,
      onclick: () => speech.say(l.audio, lang) }, h("b", {}, l.letter), h("span", {}, l.name), l.tricky ? h("i", {}, "⚠") : null)))));

  if (d.sounds.length) view.append(h("div", { class: "section" }, h("h2", {}, "Sounds"), h("div", { class: "grid g3" }, d.sounds.map((s) =>
    h("button", { class: "word", onclick: () => speech.say(s.text, lang) }, h("b", { style: { fontFamily: "var(--display)", fontSize: "1.6rem", minWidth: "60px" } }, s.pattern),
      h("div", {}, h("div", { class: "t" }, s.text, " ", h("span", { class: "en" }, s.en)), h("div", { class: "en small" }, s.tip)))))));

  view.append(h("div", { class: "section" }, h("div", { class: "section-head" }, h("h2", {}, "Words"), h("span", { class: "muted small" }, "Tap to hear. Colour and shape = gender")),
    h("div", { class: "grid g3" }, d.vocab.map((v) => { const { el, cls } = wordLabel(v);
      return h("button", { class: `word ${cls}`, onclick: () => speech.say(v.text, lang) }, v.pos === "noun" && v.g ? shape(v.g, 18) : v.pos === "verb" || v.pos === "adj" ? shape(null, 18, v.pos) : h("span", { style: { width: "18px" } }),
        h("div", {}, el, h("div", { class: "en" }, v.en, v.pl ? ` · pl. ${v.pl}` : ""), bridgeBoxes(v, { compact: true }))); }))));

  view.append(h("div", { class: "section" }, h("h2", {}, "Sentences"), h("div", { class: "stack" }, d.sentences.map((s) =>
    h("div", { class: "card flat row", style: { justifyContent: "space-between", padding: "12px 16px" } }, h("div", {}, tagged(s.tags), h("div", { class: "muted small" }, s.en)),
      h("button", { class: "icon-btn", html: ICON.speaker, "aria-label": "Play", onclick: () => speech.say(s.text, lang) }))))));

  if (d.writing_prompt) view.append(h("div", { class: "section" }, h("div", { class: "card rec" }, h("h3", {}, "Writing task"), h("p", {}, d.writing_prompt),
    h("div", {}, h("button", { class: "btn ghost", onclick: () => go(`#/write/${d.id}`) }, "Open in writing studio")))));
}

function genButton(lang, stage) {
  const b = h("button", { class: "btn sun big" }, "✨ Generate this unit with Claude");
  const status = h("p", { class: "muted small" }, "Takes about 1–2 minutes. The unit is saved to data/generated/ so you can edit it.");
  b.onclick = async () => {
    b.disabled = true; b.innerHTML = '<span class="spinner" style="width:20px;height:20px;border-width:3px"></span> Writing your unit…';
    try { await api.post(`/api/units/${lang}/${stage}/generate`); toast("Unit ready!"); window.dispatchEvent(new HashChangeEvent("hashchange")); }
    catch (e) { toast(e.message); b.disabled = false; b.textContent = "✨ Try again"; }
  };
  return h("div", { class: "stack" }, b, status);
}

// ====================================================================== PRACTICE
export async function practice(view) {
  const lang = store.lang;
  const st = store.state.today[lang];
  view.innerHTML = "";
  view.append(h("h1", { class: "row" }, flag(lang, true), "Practice"), h("p", { class: "muted" }, "Everything here adapts to you: due reviews, your weakest skill and your recurring mistakes."));
  const card = (title, body, btn, onclick, accent) => h("div", { class: "card stack" + (accent ? " rec" : "") }, h("h3", {}, title), h("p", { class: "muted" }, body), h("div", {}, h("button", { class: accent ? "btn sun" : "btn ghost", onclick }, btn)));
  view.append(h("div", { class: "section grid g3" },
    card("Daily mix", `${st.due} reviews due. Spaced repetition across all four skills, with extra slots for your weak spots.`, "Start mix", () => startSession({ kind: "mix" }), true),
    card("Fix my gaps", "Only the items you've missed in the last three weeks.", "Fix gaps", () => startSession({ focus: "gaps", kind: "gaps", title: "Fix my gaps" })),
    card("Checkpoint test", "A production-only test (no multiple choice). Scored per skill and tracked over time.", "Take test", () => startCheckpoint()),
    ...SKILLS.map((s) => card(`${s[0].toUpperCase() + s.slice(1)} drill`, {
      listening: "Dictation and listening comprehension at natural and slow speed.",
      speaking: "Shadow, then speak from memory. Your pronunciation is scored word by word.",
      reading: "Read colour-coded sentences and passages.",
      writing: "Translate, build sentences, choose genders.",
    }[s], "Drill", () => startSession({ focus: s, kind: `drill-${s}`, size: 12 }))),
    card("Writing studio", "Free writing with feedback (Claude if configured, otherwise a model answer).", "Write", () => go("#/write"))));
  const cats = store.state.categories;
  view.append(h("div", { class: "section" }, h("h2", {}, "Targeted drills"), h("p", { class: "muted" }, "Pick a mistake type to drill it directly."),
    h("div", { class: "row" }, Object.entries(cats).filter(([k]) => !(lang === "fr" && ["capitalization", "case"].includes(k)))
      .map(([k, c]) => h("button", { class: "btn line", onclick: () => startSession({ focus: k, kind: `drill-${k}`, size: 10, title: c.label }) }, c.label)))));
}

// ====================================================================== INSIGHTS
export async function insights(view) {
  loading(view);
  const lang = store.lang;
  const d = await api.get(`/api/insights?lang=${lang}`);
  view.innerHTML = "";
  view.append(h("h1", { class: "row" }, flag(lang, true), `${LNAME[lang]} insights`),
    h("p", { class: "muted" }, `${d.total_attempts} answers analysed · ${d.items_learned} items learned · ${d.items_solid} solid in every skill · 🔥 ${d.streak}-day streak`));

  view.append(h("div", { class: "section" }, challengeCard(d.challenge)));
  if (d.recommendations.length) view.append(h("div", { class: "section" }, h("h2", {}, "What to do next"), h("div", { class: "grid g2" }, d.recommendations.map(recCard))));

  // skills: accuracy (14 days) as bars, with previous period as text
  const skillCard = h("div", { class: "card stack" }, h("h3", {}, "Accuracy by skill"), h("p", { class: "muted small" }, "Last 14 days, compared with the 14 days before."));
  d.skills.forEach((s) => {
    const row = h("div", { class: "bar-row" }, h("span", { class: "row", html: SKILL_ICON[s.skill] + `<span style="text-transform:capitalize">${s.skill}</span>` }),
      h("div", { class: "track" }, h("i", { style: { width: s.accuracy == null ? "0" : pct(s.accuracy) } })), h("span", { class: "val" }, pct(s.accuracy)));
    tipOn(row, `<b>${s.skill}</b><br>accuracy ${pct(s.accuracy)} (before: ${pct(s.prev)})<br>mastery ${pct(s.mastery)} · ${s.cards} cards`);
    skillCard.append(row);
  });

  const catCard = h("div", { class: "card stack" }, h("h3", {}, "Mistake patterns"), h("p", { class: "muted small" }, "Every wrong answer is diagnosed. Last 14 days; ▲ means more than the 14 days before."));
  if (!d.categories.length) catCard.append(h("p", { class: "muted" }, "No mistakes logged yet."));
  const maxC = Math.max(1, ...d.categories.map((c) => c.count));
  d.categories.slice(0, 8).forEach((c) => {
    const row = h("div", { class: "bar-row", style: { cursor: "pointer" }, onclick: () => startSession({ focus: c.id, kind: `drill-${c.id}`, size: 10, title: c.label }) },
      h("span", {}, c.label, " ", h("span", { class: `trend ${c.trend}` }, c.trend === "up" ? "▲" : c.trend === "down" ? "▼" : "")),
      h("div", { class: "track" }, h("i", { style: { width: `${(c.count / maxC) * 100}%` } })), h("span", { class: "val" }, c.count));
    tipOn(row, `<b>${c.label}</b>: ${c.count} (previous 14 days: ${c.prev})<br>${md(c.tip)}<br><i>Click to drill</i>`);
    catCard.append(row);
  });
  view.append(h("div", { class: "section grid g2" }, skillCard, catCard));

  // activity: two separate charts (no dual axis)
  view.append(h("div", { class: "section grid g2" },
    h("div", { class: "card stack" }, h("h3", {}, "Minutes studied"), h("p", { class: "muted small" }, "Last 14 days"), barChart(d.timeline, "minutes", (v) => `${v} min`)),
    h("div", { class: "card stack" }, h("h3", {}, "Daily accuracy"), h("p", { class: "muted small" }, "Days with answers only"), lineChart(d.timeline))));

  // persistent gaps
  const gapCard = h("div", { class: "card stack" }, h("div", { class: "section-head" }, h("h3", {}, "Persistent gaps"),
    d.gaps.length ? h("button", { class: "btn sun", onclick: () => startSession({ focus: "gaps", kind: "gaps", title: "Fix my gaps" }) }, "Fix these") : null));
  if (!d.gaps.length) gapCard.append(h("p", { class: "muted" }, "Nothing keeps slipping right now. 🎉"));
  d.gaps.forEach((g) => gapCard.append(h("div", { class: "gap-row" },
    h("button", { class: "icon-btn", html: ICON.speaker, "aria-label": "Play", onclick: () => g.kind !== "passage" && speech.say(g.text, lang) }),
    h("div", {}, h("b", { class: gclass(g.g), style: { color: g.g ? "var(--g)" : "" } }, g.text), h("div", { class: "muted small" }, g.en, g.last_given ? ` · you wrote “${g.last_given}”` : "")),
    h("div", { style: { textAlign: "right" } }, h("b", {}, `${g.misses}×`), h("div", { class: "muted small" }, g.category_label)))));

  const confCard = h("div", { class: "card stack" }, h("h3", {}, "Gender slips"), h("p", { class: "muted small" }, "Nouns whose article you've mixed up."));
  if (!d.confusions.length) confCard.append(h("p", { class: "muted" }, "None yet."));
  d.confusions.forEach((c) => confCard.append(h("div", { class: `word ${gclass(c.g)}`, style: { cursor: "default" } }, shape(c.g, 18),
    h("div", {}, h("span", { class: "t" }, h("span", { class: "art", style: { color: "var(--g)" } }, (c.article || "") + " "), c.word), h("div", { class: "en" }, `${GENDER_NAME[c.g]} · missed ${c.times}×`)))));
  view.append(h("div", { class: "section grid g2" }, gapCard, confCard));

  if (d.checkpoints.length) view.append(h("div", { class: "section card stack" }, h("h3", {}, "Checkpoint history"),
    ...d.checkpoints.map((c) => h("div", { class: "row" }, h("span", { class: "chip" }, new Date(c.ts * 1000).toLocaleDateString()), h("span", { class: "chip level" }, `stage ${c.stage}`),
      ...Object.entries(c.scores).map(([s, v]) => h("span", { class: "chip" }, `${s} ${pct(v)}`))))));
}

function barChart(series, key, fmt) {
  const W = 420, H = 120, pad = 22, n = series.length, bw = (W - pad) / n;
  const max = Math.max(10, ...series.map((s) => s[key] || 0));
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg"); svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("class", "spark");
  svg.innerHTML = `<g class="grid"><line x1="${pad}" x2="${W}" y1="${H - 18}" y2="${H - 18}"/><line x1="${pad}" x2="${W}" y1="10" y2="10" stroke-dasharray="3 4"/></g><g class="axis"><text x="0" y="14">${max}</text><text x="0" y="${H - 18}">0</text></g>`;
  series.forEach((s, k) => {
    const v = s[key] || 0, bh = ((H - 28) * v) / max, x = pad + k * bw + 2, y = H - 18 - bh;
    const hit = document.createElementNS(ns, "rect"); hit.setAttribute("x", x - 2); hit.setAttribute("y", 0); hit.setAttribute("width", bw); hit.setAttribute("height", H); hit.setAttribute("fill", "transparent"); hit.setAttribute("class", "hit");
    const r = document.createElementNS(ns, "rect"); r.setAttribute("class", "b"); r.setAttribute("x", x); r.setAttribute("width", Math.max(2, bw - 4));
    r.setAttribute("y", v ? y : H - 19); r.setAttribute("height", v ? bh : 1); r.setAttribute("rx", 4);
    svg.append(hit, r);
    if (k % 2 === 1 || k === n - 1) { const t = document.createElementNS(ns, "text"); t.setAttribute("x", x); t.setAttribute("y", H - 4); t.textContent = s.day.slice(8); t.setAttribute("class", "axis"); t.setAttribute("fill", "var(--muted)"); t.setAttribute("font-size", "10"); svg.append(t); }
    tipOn(hit, `${new Date(s.day).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" })}<br><b>${fmt(v)}</b> · ${s.answers} answers`);
  });
  return svg;
}

function lineChart(series) {
  const W = 420, H = 120, pad = 30, n = series.length, step = (W - pad - 6) / (n - 1);
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg"); svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("class", "spark");
  const y = (v) => 10 + (H - 30) * (1 - v);
  svg.innerHTML = `<g class="grid"><line x1="${pad}" x2="${W}" y1="${y(1)}" y2="${y(1)}" stroke-dasharray="3 4"/><line x1="${pad}" x2="${W}" y1="${y(.5)}" y2="${y(.5)}" stroke-dasharray="3 4"/><line x1="${pad}" x2="${W}" y1="${y(0)}" y2="${y(0)}"/></g>
    <g class="axis"><text x="0" y="${y(1) + 4}">100%</text><text x="0" y="${y(.5) + 4}">50%</text><text x="0" y="${y(0) + 4}">0%</text></g>`;
  const pts = series.map((s, k) => ({ x: pad + k * step, v: s.accuracy, s }));
  let d = "", pen = false;
  pts.forEach((p) => { if (p.v == null) { pen = false; return; } d += `${pen ? "L" : "M"}${p.x},${y(p.v)} `; pen = true; });
  const path = document.createElementNS(ns, "path"); path.setAttribute("class", "l"); path.setAttribute("d", d); svg.append(path);
  pts.forEach((p) => {
    if (p.v == null) return;
    const c = document.createElementNS(ns, "circle"); c.setAttribute("class", "d"); c.setAttribute("cx", p.x); c.setAttribute("cy", y(p.v)); c.setAttribute("r", 4.5);
    const hit = document.createElementNS(ns, "circle"); hit.setAttribute("cx", p.x); hit.setAttribute("cy", y(p.v)); hit.setAttribute("r", 14); hit.setAttribute("fill", "transparent");
    svg.append(c, hit);
    tipOn(hit, `${new Date(p.s.day).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" })}<br><b>${pct(p.v)}</b> of ${p.s.answers} answers`);
  });
  if (!pts.some((p) => p.v != null)) { const t = document.createElementNS(ns, "text"); t.setAttribute("x", W / 2 - 40); t.setAttribute("y", H / 2); t.setAttribute("fill", "var(--muted)"); t.textContent = "No answers yet"; svg.append(t); }
  return svg;
}

// ====================================================================== PLAN
export async function plan(view) {
  loading(view);
  const p = await api.get("/api/schedule");
  view.innerHTML = "";
  view.append(h("h1", {}, "Your 26-week plan"), h("p", { class: "muted" },
    `Started ${new Date(p.start_date).toLocaleDateString(undefined, { day: "numeric", month: "long", year: "numeric" })}. ${LNAME[p.order[0]]} first, ${LNAME[p.order[1]]} joins in week ${p.langs[p.order[1]].starts_week}, so the basics of each settle before the next arrives. ${p.daily_minutes} min/day in total.`));

  // timeline
  const tl = h("div", { class: "timeline card" });
  tl.append(h("div", { class: "tl-row tl-head" }, h("span", {}), ...p.timeline.map((w) => h("div", { class: "tl-cell" }, w.week))));
  for (const lang of p.order) {
    tl.append(h("div", { class: "tl-row" }, h("span", { class: "lab" }, flag(lang), LNAME[lang]), ...p.timeline.map((w) => {
      const c = w[lang];
      const cell = h("div", { class: `tl-cell ${c.level || ""} ${w.week === p.week_capped ? "now" : ""} ${w.checkpoint && c.stage ? "cp" : ""}` }, c.stage || "");
      tipOn(cell, `Week ${w.week} · ${new Date(w.start).toLocaleDateString(undefined, { day: "numeric", month: "short" })}<br>${c.stage ? `<b>Stage ${c.stage} (${c.level})</b><br>${c.title}` : "not started"}${w.checkpoint && c.stage ? "<br>◆ checkpoint week" : ""}`);
      return cell;
    })));
  }
  view.append(h("div", { class: "section" }, h("div", { class: "section-head" }, h("h2", {}, "Timeline"),
    h("div", { class: "row small muted" }, h("span", { class: "tl-cell A1", style: { width: "22px", height: "16px" } }), "A1", h("span", { class: "tl-cell A2", style: { width: "22px", height: "16px" } }), "A2",
      h("span", { class: "tl-cell B1", style: { width: "22px", height: "16px" } }), "B1", h("span", { style: { color: "var(--sun)" } }, "◆"), "checkpoint")), tl));

  // weekly rhythm
  view.append(h("div", { class: "section grid g2" },
    h("div", { class: "card stack" }, h("h3", {}, "Weekly rhythm"),
      h("p", {}, h("b", {}, "Mon–Sat: "), "warm-up mix (spaced review) → new lesson part → skill drill. Writing on Tue / Thu / Sat."),
      h("p", {}, h("b", {}, "Sunday: "), "fix your gaps, then free writing or a checkpoint test, then relaxed listening (podcast or show)."),
      h("p", {}, h("b", {}, "Checkpoints: "), "weeks 4, 8, 13, 17, 22 and 26. These are production-only tests that measure real progress per skill."),
      h("p", { class: "muted small" }, "Fall behind? The plan automatically adds a catch-up block until you're back on track.")),
    projectionCard(p)));
  view.append(h("div", { class: "section grid g2" }, ...p.order.map((lang) => {
    const lp = p.langs[lang];
    return h("div", { class: "card stack" }, h("h3", { class: "row" }, flag(lang), `${LNAME[lang]}: your real pace`),
      h("p", {}, lp.pace ? `${lp.pace.stages_done} stages done (schedule: ${lp.pace.expected_done}).`
        : `Starts ${new Date(new Date(p.start_date).getTime() + (lp.starts_week - 1) * 7 * 864e5).toLocaleDateString(undefined, { day: "numeric", month: "long" })} (week ${lp.starts_week}). Your pace forecast appears after a week of lessons.`),
      h("p", { class: "muted" }, paceLine(lp.pace) || ""),
      h("p", { class: "small" }, h("b", {}, `Challenge Lv ${lp.challenge.level} · ${lp.challenge.name}. `), lp.challenge.desc),
      h("p", { class: "small muted" }, lp.stretch ? "🚀 Stretch goal unlocked: stages 27–32 (towards B2) now appear in your Journey."
        : "Get 2 stages ahead of schedule to unlock the stretch goal (stages 27–32, towards B2)."));
  })));
}

function projectionCard(p) {
  const [lo, hi] = p.projection.b1_guided_hours;
  const card = h("div", { class: "card stack rec" }, h("h3", {}, "Honest maths"));
  for (const lang of p.order) {
    const hrs = p.projection.hours[lang];
    const share = Math.min(1, hrs / lo);
    card.append(h("div", { class: "bar-row" }, h("span", { class: "row" }, flag(lang), LNAME[lang]), h("div", { class: "track" }, h("i", { style: { width: `${share * 100}%` } })), h("span", { class: "val" }, `${hrs} h`)));
  }
  card.append(h("p", { class: "muted small" }, `B1 usually takes about ${lo}–${hi} hours of guided study per language. With ${p.daily_minutes} min/day across both, the app gets you to a strong A2 with B1 in reach. To close the gap, add daily “free” immersion: podcasts on the commute, a show at night, voice notes to yourself. Every 30 min/day of listening adds about 90 hours over 6 months.`));
  return card;
}

// ====================================================================== WRITE
export async function write(view, uid) {
  const lang = store.lang;
  view.innerHTML = "";
  let u = null;
  const units = await api.get(`/api/units?lang=${lang}`);
  const cur = uid || `${lang}-${String(units.current_stage).padStart(2, "0")}`;
  u = await api.get(`/api/units/${cur}`);
  const prompt = u.has_content ? u.writing_prompt : `Write freely about your day in ${LNAME[lang]}.`;
  view.append(h("h1", { class: "row" }, flag(lang, true), "Writing studio"),
    h("p", { class: "muted" }, store.ai ? "Claude corrects your text and tags every mistake. Those tags feed your Insights, just like drills." : "Offline mode: self-check plus a model answer. Add an Anthropic API key for full corrections."));
  const promptSel = h("select", {}, units.units.filter((x) => x.has_content).map((x) => h("option", { value: x.id, selected: x.id === cur }, `Stage ${x.stage}: ${x.title}`)), h("option", { value: "free", selected: false }, "Free topic"));
  promptSel.onchange = () => promptSel.value === "free" ? (promptBox.textContent = `Write about anything in ${LNAME[lang]}: your day, your plans, a memory.`, current = null) : go(`#/write/${promptSel.value}`);
  let current = u.has_content ? u.id : null;
  const promptBox = h("div", { class: "en-prompt" }, prompt);
  const ta = h("textarea", { placeholder: lang === "de" ? "Schreib hier…" : "Écris ici…" });
  const out = h("div", {});
  const btn = h("button", { class: "btn sun big" }, "Get feedback");
  btn.onclick = async () => {
    if (ta.value.trim().length < 3) return toast("Write a little more first.");
    btn.disabled = true; btn.innerHTML = '<span class="spinner" style="width:20px;height:20px;border-width:3px"></span> Checking…';
    try { const fb = await api.post("/api/writing", { lang, text: ta.value, prompt: promptBox.textContent, unit_id: current }); out.innerHTML = ""; out.append(writingFeedback(fb, u.writing_model, lang)); }
    catch (e) { toast(e.message); }
    btn.disabled = false; btn.textContent = "Get feedback";
  };
  view.append(h("div", { class: "section stack" }, h("label", { class: "field" }, "Prompt", promptSel), promptBox, ta, accentBar(lang, () => ta), h("div", {}, btn), out));
  const hist = await api.get(`/api/writing?lang=${lang}`);
  if (hist.length) view.append(h("div", { class: "section" }, h("h2", {}, "Past writing"), ...hist.map((w) => h("details", { class: "card fold" },
    h("summary", {}, new Date(w.ts * 1000).toLocaleDateString(), " · ", w.prompt.slice(0, 60), w.feedback.score != null ? ` · ${w.feedback.score}/100` : ""),
    h("p", { style: { margin: "10px 0" } }, w.text), writingFeedback(w.feedback, "", lang)))));
}

// ====================================================================== COLOUR KEY
export function colors(view) {
  view.innerHTML = "";
  view.append(h("h1", {}, "The colour key"), h("p", { class: "muted" }, "Colour and shape always mean the same thing, everywhere in the app. Your brain links the colour to the word without you having to memorise rules: that's dual coding. Shapes keep it working for colour-blind eyes and in black-and-white."));
  const L = (g, pos, title, de, fr, note) => h("div", { class: `legend ${gclass(g, pos)}` }, shape(g, 40, pos), h("h3", {}, title), h("div", {}, flag("de"), " ", de), h("div", {}, flag("fr"), " ", fr), h("p", { class: "small muted" }, note));
  view.append(h("div", { class: "section legend-grid" },
    L("m", null, "■ Masculine", "der Hund, der Tisch", "le chien, le livre", "Blue square. Solid and stable."),
    L("f", null, "● Feminine", "die Lampe, die Tür", "la maison, la porte", "Rose circle."),
    L("n", null, "▲ Neuter", "das Buch, das Mädchen", "(none in French)", "Green triangle. German only."),
    L("pl", null, "◆ Plural", "die Bücher, die Eltern", "les livres, les parents", "Violet diamond. German plural is always ‘die’."),
    L(null, "verb", "➜ Verbs", "ich wohne, du bist", "je parle, il est", "Orange arrow: verbs are the action. Watch them move in German word order."),
    L(null, "adj", "〰 Adjectives & adverbs", "groß, heute", "petit, souvent", "Teal wave: they describe."),
  ));
  view.append(h("div", { class: "section card stack" }, h("h3", {}, "In a sentence"),
    tagged([{ t: "Heute", pos: "adj" }, { t: "möchte", pos: "verb" }, { t: "ich", pos: "pron" }, { t: "einen", pos: "art", g: "m" }, { t: "Kaffee", pos: "noun", g: "m" }, { t: "und", pos: "conj" }, { t: "die", pos: "art", g: "f" }, { t: "Suppe", pos: "noun", g: "f" }, { t: ".", pos: "punct" }]),
    tagged([{ t: "Aujourd'hui", pos: "adj" }, { t: "je", pos: "pron" }, { t: "voudrais", pos: "verb" }, { t: "un", pos: "art", g: "m" }, { t: "café", pos: "noun", g: "m" }, { t: "et", pos: "conj" }, { t: "la", pos: "art", g: "f" }, { t: "soupe", pos: "noun", g: "f" }, { t: ".", pos: "punct" }]),
    h("p", { class: "muted small" }, "Notice: German puts the verb second, so ‘Heute möchte ich’. French keeps subject + verb together: ‘Aujourd'hui je voudrais’. And gender doesn't carry over: der Kaffee is masculine, and so is le café, but das Buch is neuter while le livre is masculine.")));
  view.append(h("div", { class: "section card stack" }, h("h3", {}, "Feedback colours"),
    h("div", { class: "row" }, h("span", { class: "chip", style: { background: "var(--ok-bg)", color: "var(--ok-ink)" } }, "✓ correct"), h("span", { class: "chip", style: { background: "var(--almost-bg)", color: "var(--almost-ink)" } }, "✓ almost (accent or capital slip)"), h("span", { class: "chip", style: { background: "var(--bad-bg)", color: "var(--bad-ink)" } }, "✕ not quite")),
    h("p", { class: "muted small" }, "Feedback uses pale backgrounds and icons so it never competes with the grammar colours.")));
}

// ====================================================================== SETTINGS
export async function settings(view) {
  await refreshState();
  const s = store.settings;
  view.innerHTML = "";
  const f = {
    start: h("input", { type: "date", value: s.start_date }),
    mins: h("input", { type: "number", min: 15, max: 480, step: 5, value: s.daily_minutes }),
    first: h("select", {}, h("option", { value: "de", selected: s.first_lang === "de" }, "German first"), h("option", { value: "fr", selected: s.first_lang === "fr" }, "French first")),
    second: h("input", { type: "number", min: 1, max: 20, value: s.second_lang_start_week }),
    rate: h("input", { type: "range", min: 0.6, max: 1.2, step: 0.05, value: s.speech_rate }),
    challenge: h("select", {}, h("option", { value: "auto", selected: String(s.challenge_mode) === "auto" }, "Automatic (recommended): adapts to how you're doing"),
      ...[1, 2, 3, 4, 5].map((n) => h("option", { value: String(n), selected: String(s.challenge_mode) === String(n) }, `Fixed at level ${n}: ${["Gentle", "Steady", "Stretch", "Hard", "Expert"][n - 1]}`))),
    stretch: h("input", { type: "checkbox", checked: !!s.stretch_goal }),
    colorsOn: h("input", { type: "checkbox", checked: s.grammar_colors !== false }),
    vde: h("select", {}), vfr: h("select", {}),
  };
  const fillVoices = () => {
    for (const [lang, sel] of [["de", f.vde], ["fr", f.vfr]]) {
      sel.innerHTML = ""; sel.append(h("option", { value: "" }, "Automatic (best available)"));
      speech.voicesFor(lang).forEach((v) => sel.append(h("option", { value: v.name, selected: v.name === s[`voice_${lang}`] }, `${v.name} (${v.lang})`)));
    }
  };
  fillVoices(); speechSynthesis.addEventListener?.("voiceschanged", fillVoices);
  const save = async () => {
    await api.put("/api/settings", { values: { start_date: f.start.value, daily_minutes: +f.mins.value, first_lang: f.first.value, second_lang_start_week: +f.second.value,
      speech_rate: +f.rate.value, grammar_colors: f.colorsOn.checked, voice_de: f.vde.value, voice_fr: f.vfr.value,
      challenge_mode: f.challenge.value, stretch_goal: f.stretch.checked } });
    await refreshState(); toast("Saved ✓");
  };
  view.append(h("h1", {}, "Settings"), h("div", { class: "section grid g2" },
    h("div", { class: "card stack" }, h("h3", {}, "Schedule"),
      h("label", { class: "field" }, "Start date", f.start, h("span", { class: "hint" }, "Week 1 begins here.")),
      h("label", { class: "field" }, "Minutes per day (both languages)", f.mins),
      h("label", { class: "field" }, "Order", f.first),
      h("label", { class: "field" }, "Second language starts in week", f.second),
      h("label", { class: "field" }, "Challenge level", f.challenge, h("span", { class: "hint" }, "Automatic keeps you near 85% correct: tougher when you're coasting, gentler when you're struggling.")),
      h("label", { class: "row" }, f.stretch, "Stretch goal: show stages 27–32 (towards B2) now")),
    h("div", { class: "card stack" }, h("h3", {}, "Voice & display"),
      h("label", { class: "field" }, "Speech speed", f.rate),
      h("label", { class: "field" }, "German voice", f.vde), h("label", { class: "field" }, "French voice", f.vfr),
      h("div", { class: "row" }, h("button", { class: "btn ghost", onclick: () => speech.say("Guten Tag! Wie geht's?", "de") }, "▶ Test German"), h("button", { class: "btn ghost", onclick: () => speech.say("Bonjour ! Ça va ?", "fr") }, "▶ Test French")),
      h("label", { class: "field" }, "Theme", h("select", { "data-theme-select": true, onchange: (e) => setTheme(e.target.value) },
        ...[["system", "Match my system"], ["light", "Light"], ["dark", "Dark"]].map(([v, t]) => h("option", { value: v, selected: savedTheme() === v }, t))),
        h("span", { class: "hint" }, "Applies straight away. The sun/moon button next to the logo switches it too.")),
      h("label", { class: "row" }, f.colorsOn, "Grammar colours on words"),
      h("p", { class: "small muted" }, speech.canListen() ? "✅ Speech recognition available" : "⚠️ Speech recognition isn't available in this browser. Use Chrome or Edge.")),
    h("div", { class: "card stack" }, h("h3", {}, "Claude (optional)"),
      h("p", {}, store.ai ? "✅ Connected. Free writing gets full corrections, and A2/B1 stages can be generated." : "Not configured. Set ANTHROPIC_API_KEY before starting the app to turn on AI writing feedback and unit generation."),
      h("p", { class: "small muted" }, "Model: " + s.ai_model))),
    h("div", { class: "section" }, h("button", { class: "btn sun big", onclick: save }, "Save settings")));
}
