// The study player: runs lessons, mixes, drills and checkpoints full-screen.
// Flow per exercise: render → answer → instant diagnosis (what kind of mistake) → continue.
import { api } from "./api.js";
import { speech } from "./speech.js";
import { ICON, SKILL_ICON, accentBar, burst, flag, gclass, h, md, shape, tagged, toast, wordLabel, GENDER_NAME, pct } from "./ui.js";

const HEAD = {
  de: { correct: "Richtig!", almost: "Fast!", wrong: "Nicht ganz." },
  fr: { correct: "Bravo !", almost: "Presque !", wrong: "Pas tout à fait." },
};
const SUB = { correct: "Correct", almost: "Almost: accepted with a note", wrong: "Not quite. It'll come back soon" };

export function openPlayer({ title, steps, lang, kind, sessionId = "", onFinish, onComplete, onRetry }) {
  const root = document.getElementById("player");
  root.hidden = false; root.innerHTML = "";
  document.body.style.overflow = "hidden";
  const queue = steps.slice();
  const requeued = new Set();
  const results = [];
  let i = 0, xp = 0, t0 = Date.now(), closed = false;

  const progress = h("i");
  const xpPill = h("div", { class: "xp-pill" }, "0 XP");
  const closeBtn = h("button", { class: "icon-btn", "aria-label": "Close", html: ICON.close, onclick: () => close(true) });
  root.append(h("div", { class: "p-top" }, closeBtn, h("div", { class: "progress", role: "progressbar", "aria-label": title }, progress), xpPill));
  const stage = h("div", { class: "p-stage" });
  const foot = h("div", { class: "p-foot" });
  root.append(stage, foot);

  let primary = null;  // the current main button (Enter)
  let keyHandler = null;
  const onKey = (e) => {
    if (closed) return;
    const inText = ["TEXTAREA"].includes(document.activeElement?.tagName);
    if (e.key === "Escape") { close(true); return; }
    if (e.key === "Enter" && (!inText || e.ctrlKey || e.metaKey)) {
      if (primary && !primary.disabled) { e.preventDefault(); primary.click(); }
      return;
    }
    keyHandler?.(e);
  };
  document.addEventListener("keydown", onKey);

  function close(early) {
    if (closed) return;
    if (early && results.length && !confirm("Leave this session? Your answers so far are saved.")) return;
    closed = true; speech.stop();
    document.removeEventListener("keydown", onKey);
    root.hidden = true; root.innerHTML = ""; document.body.style.overflow = "";
    onFinish?.(early);
  }

  function setProgress() { progress.style.width = `${Math.round((i / queue.length) * 100)}%`; }

  function setFoot({ state = "", content = null, button = "Continue", disabled = false, onclick, secondary = null, hidden = false }) {
    foot.className = "p-foot " + state;
    primary = h("button", { class: "btn big " + (state === "correct" ? "" : state === "wrong" ? "" : ""), disabled, onclick });
    primary.innerHTML = `${button} ${ICON.arrow}`;
    foot.innerHTML = "";
    foot.append(h("div", { class: "inner" }, content || h("div", { class: "spacer" }), secondary, primary));
    primary.hidden = hidden;  // tap-to-answer questions submit on tap, so no Check button
  }

  function next() {
    speech.stop();
    i++; setProgress();
    if (i >= queue.length) return finish();
    render();
  }

  function render() {
    setProgress();
    keyHandler = null;
    stage.innerHTML = "";
    const step = queue[i];
    const node = h("div", { class: "enter stack", style: { gap: "22px" }, "data-item": step.ex?.item_id || step.item_id || "", "data-type": step.ex?.type || step.step });
    stage.append(node);
    stage.scrollTop = 0; root.scrollTop = 0;
    if (step.step === "grammar") return renderGrammar(step, node);
    if (step.step === "teach") return renderTeach(step, node);
    if (step.step === "write") return renderWrite(step, node);
    return renderExercise(step.ex, node);
  }

  // ------------------------------------------------------------ grammar & teach
  function renderGrammar(g, node) {
    node.append(
      h("div", { class: "p-kicker" }, h("span", { class: "chip sun" }, "Grammar idea")),
      h("h2", { class: "p-prompt" }, g.title),
      h("div", { class: "card gnote" }, h("div", { class: "body", html: md(g.body || "") }), g.table ? table(g.table) : null),
    );
    setFoot({ onclick: next });
  }

  function renderTeach(it, node) {
    const cls = gclass(it.g, it.pos);
    const card = h("div", { class: `card teach ${cls}` });
    const playBtn = h("button", { class: "play", "aria-label": "Play", html: ICON.play, onclick: () => speech.say(it.audio, lang, { btn: playBtn }) });
    const slowBtn = h("button", { class: "play slow", "aria-label": "Play slowly", html: ICON.slow, onclick: () => speech.say(it.audio, lang, { slow: true, btn: slowBtn }) });
    if (it.kind === "letter") {
      const wordBtn = h("button", { class: "btn ghost", style: { padding: "6px 12px" }, onclick: () => speech.say(it.word, lang), "aria-label": "Play example" }, "▶");
      card.append(h("div", { class: "letter-tile" + (it.tricky ? " tricky" : "") }, h("span", {}, it.letter.toUpperCase()), h("span", { class: "lower" }, it.letter.toLowerCase())),
        h("div", { class: "meaning" }, "Name: ", h("b", {}, it.name), h("span", { class: "muted" }, `  ·  sounds like “${it.like}”`)),
        h("div", { class: "audio-row" }, playBtn, slowBtn, speakMini(it.word)),
        h("div", { class: "ex" }, h("div", { class: "row", style: { justifyContent: "center" } }, tagged(it.tags), wordBtn),
          h("div", { class: "muted small" }, it.word_en, " · spelled: ", it.spelled)),
        it.tip ? h("div", { class: "tipbox" }, "⚠ " + it.tip) : null);
      node.append(h("div", { class: "p-kicker" }, h("span", { class: "chip sun" }, "New letter"), it.tricky ? "A trap for English speakers: listen closely" : "Listen to its name and say it"), card);
      setTimeout(() => !closed && speech.say(it.audio, lang, { btn: playBtn }), 300);
      keyHandler = (e) => { if (e.key === " ") { e.preventDefault(); playBtn.click(); } };
      setFoot({ onclick: next });
      return;
    }
    if (it.kind === "sound") {
      card.append(h("div", { class: "pattern" }, it.pattern), h("div", { class: "big" }, it.text), h("div", { class: "meaning" }, it.en),
        h("div", { class: "audio-row" }, playBtn, slowBtn), h("div", { class: "tipbox" }, "How to say it: " + it.tip));
    } else {
      const big = h("div", { class: "big" });
      if (it.pos === "noun" && it.g) big.append(shape(it.g, 34));
      if (it.pos === "verb") big.append(shape(null, 34, "verb"));
      big.append(it.kind === "sentence" ? tagged(it.tags) : wordLabel(it).el);
      card.append(big, h("div", { class: "meaning" }, it.en));
      const links = bridgeBoxes(it);
      if (links) card.append(links);
      if (it.pos === "noun" && it.g) card.append(h("div", { class: "gender-label" }, `${GENDER_NAME[it.g]}${it.pl ? " · plural: " + it.pl : ""}`));
      if (it.forms?.length) card.append(h("div", { class: "muted" }, "Forms: ", h("b", {}, it.forms.join(" · "))));
      card.append(h("div", { class: "audio-row" }, playBtn, slowBtn, speakMini(it.audio)));
      if (it.ex) card.append(h("div", { class: "ex" }, tagged(it.ex.tags), h("div", { class: "muted small" }, it.ex.en),
        h("button", { class: "btn ghost", style: { marginTop: "8px", padding: "6px 12px" }, onclick: () => speech.say(it.ex.t, lang) }, "▶ example")));
    }
    node.append(h("div", { class: "p-kicker" }, h("span", { class: "chip sun" }, "New"), it.kind === "sound" ? "Listen and copy the sound" : "Listen, look at the colour, say it"), card);
    setTimeout(() => !closed && speech.say(it.audio, lang, { btn: playBtn }), 300);
    keyHandler = (e) => { if (e.key === " " && document.activeElement?.tagName !== "INPUT") { e.preventDefault(); playBtn.click(); } };
    setFoot({ onclick: next });
  }

  /** Small "say it yourself" button on teach cards. Logs a speaking attempt. */
  function speakMini(target) {
    if (!speech.canListen()) return null;
    const step = queue[i];
    const btn = h("button", { class: "play slow micbtn", "aria-label": "Say it", html: ICON.mic });
    btn.onclick = async () => {
      btn.classList.add("speaking");
      try {
        const alts = await speech.listen(lang).promise;
        const r = await api.post("/api/answer", { lang, item_id: step.item_id, skill: "speaking", type: "speak", transcripts: alts, session_kind: kind, session_id: sessionId });
        toast(r.grade === "correct" ? "🎉 Clear!" : r.grade === "almost" ? `Almost. Work on: ${r.detail.missed.join(", ")}` : `Heard: “${r.detail.heard || "nothing"}”`);
        if (r.grade === "correct") burst(btn, 8);
      } catch { toast("Microphone not available"); }
      btn.classList.remove("speaking");
    };
    return btn;
  }

  // ------------------------------------------------------------ exercises
  function kicker(ex) {
    return h("div", { class: "p-kicker" }, h("span", { class: "skill-tag", html: SKILL_ICON[ex.skill] + ex.skill }),
      ex.level > 2 ? h("span", { class: "chip level-chip", title: "Challenge level: the app raises it when you're coasting" }, `Lv ${ex.level}`) : null,
      ex.why?.startsWith("focus") ? h("span", { class: "chip sun" }, "targeted drill") : ex.why === "gap" ? h("span", { class: "chip sun" }, "gap") : null);
  }

  function audioRow(text, slowOk = true) {
    const p = h("button", { class: "play", "aria-label": "Play audio", html: ICON.play });
    const s = slowOk ? h("button", { class: "play slow", "aria-label": "Play slowly", html: ICON.slow }) : h("span", { class: "chip", title: "Expert level: no slow-motion replays" }, "no slow replay");
    p.onclick = () => speech.say(text, lang, { btn: p });
    if (slowOk) s.onclick = () => speech.say(text, lang, { slow: true, btn: s });
    return { row: h("div", { class: "audio-row" }, p, s, h("span", { class: "muted small" }, h("span", { class: "kbd" }, "space"), " replay")), play: p };
  }

  function renderExercise(ex, node) {
    const started = Date.now();
    node.append(kicker(ex), h("h2", { class: "p-prompt" }, ex.prompt));
    let getAnswer = () => null, markResult = () => {}, transcripts = null;
    const submit = async (extra = {}) => {
      if (primary) primary.disabled = true;
      const answer = extra.answer ?? getAnswer();
      let res;
      try {
        res = await api.post("/api/answer", { lang, item_id: ex.item_id, skill: ex.skill, type: ex.type, answer: answer ?? "",
          transcripts: extra.transcripts || [], session_kind: kind, session_id: sessionId, seconds: (Date.now() - started) / 1000 });
      } catch (e) { toast("Couldn't check: " + e.message); if (primary) primary.disabled = false; return; }
      results.push({ ex, res });
      xp += res.xp; xpPill.textContent = `${xp} XP`; xpPill.classList.remove("bump"); void xpPill.offsetWidth; xpPill.classList.add("bump");
      markResult(res);
      if (res.grade === "wrong" && ex.why !== "retry" && !requeued.has(ex.eid) && !["checkpoint", "testout"].includes(kind)) {
        requeued.add(ex.eid); queue.push({ step: "exercise", ex: { ...ex, eid: ex.eid + "r", why: "retry" } });
      }
      showFeedback(ex, res);
    };
    const ready = (on) => { if (primary) primary.disabled = !on; };
    const replayKey = (play) => (e) => { if (e.key === " " && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) { e.preventDefault(); play.click(); } };

    // --- multiple choice (meaning / spelling)
    if (["listen_choose", "read_choose", "listen_spell", "letter_listen"].includes(ex.type)) {
      if (ex.type !== "read_choose") {
        const { row, play } = audioRow(ex.audio, ex.slow_audio !== false); node.append(row);
        setTimeout(() => !closed && play.click(), 250);
        keyHandler = replayKey(play);
      } else {
        const p = h("button", { class: "icon-btn", "aria-label": "Hear it", html: ICON.speaker, onclick: () => speech.say(ex.show, lang) });
        node.append(h("div", { class: "card row", style: { justifyContent: "space-between" } }, tagged(ex.tags), p));
      }
      const btns = ex.options.map((o, k) => h("button", { class: "opt", onclick: () => choose(k) }, h("span", { class: "k" }, k + 1), o));
      let chosen = null;
      const choose = (k) => { if (chosen != null) return; chosen = k; btns[k].classList.add("sel"); submit({ answer: ex.options[k] }); };
      node.append(h("div", { class: "options" }, btns));
      const prev = keyHandler;
      keyHandler = (e) => { const n = parseInt(e.key, 10); if (n >= 1 && n <= btns.length) choose(n - 1); else prev?.(e); };
      markResult = (res) => btns.forEach((b, k) => {
        const val = ex.options[k];
        if (val === res.expected || (res.correct && k === chosen)) b.classList.add("right");
        else if (k === chosen) b.classList.add("wrong");
      });
      return setFoot({ button: "Check", disabled: true, hidden: true, onclick: () => {}, content: h("span", { class: "muted small" }, "Press ", h("span", { class: "kbd" }, "1–4"), " to answer") });
    }

    // --- gender
    if (ex.type === "gender") {
      const gmap = lang === "de" ? { der: "m", die: "f", das: "n" } : { le: "m", la: "f" };
      node.append(h("div", { class: "card" }, h("div", { class: "gender-word" }, ex.word), h("div", { class: "muted", style: { textAlign: "center" } }, ex.en)));
      let chosen = null;
      const btns = ex.options.map((a, k) => h("button", { class: `gopt g-${gmap[a]}`, onclick: () => choose(k) }, shape(gmap[a], 44), a));
      const choose = (k) => { if (chosen != null) return; chosen = k; submit({ answer: ex.options[k] }); };
      node.append(h("div", { class: "gender-opts", style: { "--cols": ex.options.length } }, btns));
      keyHandler = (e) => { const n = parseInt(e.key, 10); if (n >= 1 && n <= btns.length) choose(n - 1); };
      markResult = (res) => btns.forEach((b, k) => {
        if (res.expected.toLowerCase().startsWith(ex.options[k] + " ") || res.expected.endsWith(`(${ex.options[k]})`)) b.classList.add("right");
        else if (k === chosen) b.classList.add("wrong");
      });
      return setFoot({ button: "Check", disabled: true, hidden: true, onclick: () => {}, content: h("span", { class: "muted small" }, "■ masculine · ● feminine", lang === "de" ? " · ▲ neuter" : "", "  ·  keys ", h("span", { class: "kbd" }, "1–" + ex.options.length)) });
    }

    // --- typing (dictation / translate)
    if (ex.type === "dictation" || ex.type === "translate" || ex.type === "spell") {
      if (ex.type === "spell") node.append(h("p", { class: "muted" }, "You'll hear a word spelled letter by letter. It means: ", h("b", {}, ex.hint)));
      if (ex.type === "dictation" || ex.type === "spell") {
        const { row, play } = audioRow(ex.audio, ex.slow_audio !== false); node.append(row);
        setTimeout(() => !closed && play.click(), 250);
        keyHandler = replayKey(play);
      } else {
        node.append(h("div", { class: "en-prompt" }, ex.en));
      }
      const inp = h("input", { type: "text", class: "answer-input", autocomplete: "off", autocapitalize: "off", spellcheck: "false",
        placeholder: ex.type === "spell" ? "Type the word…" : ex.type === "dictation" ? "Type what you hear…" : `In ${lang === "de" ? "German" : "French"}…`, oninput: () => ready(inp.value.trim().length > 0) });
      node.append(inp, accentBar(lang, () => inp));
      if (ex.type === "translate" && ex.hint_g) node.append(h("div", { class: "muted small" }, "Include the article (", lang === "de" ? "der / die / das" : "le / la / l'", ")"));
      getAnswer = () => inp.value;
      markResult = () => { inp.disabled = true; };
      setTimeout(() => inp.focus(), 60);
      return setFoot({ button: "Check", disabled: true, onclick: () => submit() });
    }

    // --- sentence builder
    if (ex.type === "build") {
      node.append(h("div", { class: "en-prompt" }, ex.en));
      const area = h("div", { class: "build-area", "aria-label": "Your sentence" });
      const bank = h("div", { class: "bank" });
      const placed = [];
      const tiles = ex.tiles.map((t, k) => {
        const cls = ["noun", "art"].includes(t.pos) ? gclass(t.g) : gclass(null, t.pos);
        const b = h("button", { class: `tile ${cls}`, onclick: () => toggle(k) }, (t.pos === "noun" && t.g) ? shape(t.g, 12) : null, t.t);
        return b;
      });
      const toggle = (k) => {
        const at = placed.indexOf(k);
        if (at >= 0) { placed.splice(at, 1); } else { placed.push(k); }
        draw();
      };
      const draw = () => {
        area.innerHTML = ""; bank.innerHTML = "";
        placed.forEach((k) => { const c = tiles[k].cloneNode(true); c.classList.remove("ghost"); c.onclick = () => toggle(k); area.append(c); });
        tiles.forEach((tb, k) => { tb.classList.toggle("ghost", placed.includes(k)); bank.append(tb); });
        area.classList.toggle("filled", placed.length > 0);
        ready(ex.decoys ? placed.length > 0 : placed.length === tiles.length);
      };
      node.append(area, bank, h("div", { class: "muted small" }, ex.decoys
        ? `Careful: ${ex.decoys} tile${ex.decoys > 1 ? "s don't" : " doesn't"} belong. Tiles still wear their grammar colour.`
        : "Tiles wear their grammar colour: articles and nouns by gender, verbs in orange."));
      draw();
      getAnswer = () => placed.map((k) => ex.tiles[k].t);
      markResult = () => { area.style.pointerEvents = "none"; bank.style.pointerEvents = "none"; };
      return setFoot({ button: "Check", disabled: true, onclick: () => submit() });
    }

    // --- speaking
    if (ex.type === "speak" || ex.type === "speak_translate") {
      if (ex.type === "speak") {
        const p = h("button", { class: "icon-btn", "aria-label": "Hear model", html: ICON.speaker, onclick: () => speech.say(ex.audio, lang, { btn: p }) });
        node.append(h("div", { class: "card row", style: { justifyContent: "space-between" } }, h("div", {}, tagged(ex.tags), h("div", { class: "muted small" }, ex.en)), p));
        setTimeout(() => !closed && speech.say(ex.audio, lang), 250);
      } else {
        node.append(h("div", { class: "en-prompt" }, ex.en));
      }
      const heard = h("div", { class: "heard" }, speech.canListen() ? "Tap the mic and speak" : "");
      const bars = h("div", { class: "bars" }, h("i"), h("i"), h("i"), h("i"), h("i"));
      if (speech.canListen()) {
        const mic = h("button", { class: "mic", "aria-label": "Start speaking", html: ICON.mic });
        let rec = null;
        mic.onclick = async () => {
          if (rec) { rec.stop(); return; }
          speech.stop();
          mic.classList.add("live"); bars.classList.add("on"); heard.textContent = "Listening…";
          rec = speech.listen(lang, { onInterim: (t) => { heard.textContent = t ? `“${t}”` : "Listening…"; } });
          try {
            const alts = await rec.promise;
            heard.textContent = alts[0] ? `“${alts[0]}”` : "I didn't catch anything. Try again closer to the mic.";
            if (alts.length) submit({ transcripts: alts, answer: alts[0] });
          } catch (e) {
            heard.textContent = e.message === "not-allowed" ? "Microphone blocked. Allow it in the address bar." : "Speech recognition error: " + e.message;
          }
          mic.classList.remove("live"); bars.classList.remove("on"); rec = null;
        };
        node.append(h("div", { class: "stack", style: { justifyItems: "center" } }, mic, bars, heard));
        keyHandler = (e) => { if (e.key === " ") { e.preventDefault(); mic.click(); } };
        return setFoot({ button: "Skip", onclick: () => next(), content: h("span", { class: "muted small" }, h("span", { class: "kbd" }, "space"), " start / stop the mic") });
      }
      // no speech recognition → honest self-check
      node.append(h("div", { class: "card stack" }, h("b", {}, "Your browser can't recognise speech. Use Chrome or Edge for automatic scoring."),
        h("span", { class: "muted" }, "Say it out loud, then reveal the answer and judge yourself.")));
      return setFoot({ button: "Reveal", onclick: () => {
        node.append(h("div", { class: "card" }, h("b", {}, "Model: "), ex.audio || ""));
        setFoot({ content: h("span", {}, "How did it go?"), button: "I said it right", onclick: () => submit({ transcripts: [ex.audio || ex.en] }),
          secondary: h("button", { class: "btn ghost big", onclick: () => submit({ transcripts: [""] }) }, "Not yet") });
      } });
    }

    // --- reading passage
    if (ex.type === "reading_passage") {
      const p = h("button", { class: "icon-btn", "aria-label": "Read aloud", html: ICON.speaker, onclick: () => speech.say(ex.show, lang, { btn: p }) });
      node.append(h("div", { class: "passage" }, h("div", { class: "row", style: { justifyContent: "space-between", marginBottom: "8px" } }, h("h3", {}, ex.title), p), tagged(ex.tags)));
      const picks = ex.questions.map(() => null);
      const qs = ex.questions.map((q, qi) => {
        const btns = q.options.map((o, k) => h("button", { class: "opt", onclick: () => { picks[qi] = o; btns.forEach((b, j) => b.classList.toggle("sel", j === k)); ready(picks.every((x) => x)); } }, o));
        return { el: h("div", { class: "question" }, h("b", {}, `${qi + 1}. ${q.q}`), h("div", { class: "options" }, btns)), btns };
      });
      node.append(...qs.map((q) => q.el));
      getAnswer = () => picks;
      markResult = (res) => {
        qs.forEach((q, qi) => q.btns.forEach((b) => {
          b.disabled = true;
          if (b.textContent === res.right[qi]) b.classList.add("right");
          else if (b.classList.contains("sel")) b.classList.add("wrong");
        }));
        if (res.translation) node.append(h("details", { class: "card fold" }, h("summary", {}, "Show translation"), h("p", { class: "muted", style: { marginTop: "8px" } }, res.translation)));
      };
      return setFoot({ button: "Check", disabled: true, onclick: () => submit() });
    }
    node.append(h("p", {}, "Unknown exercise type " + ex.type));
    setFoot({ onclick: next });
  }

  function showFeedback(ex, res) {
    const state = res.grade;
    const fb = h("div", { class: "fb" });
    fb.append(h("div", { class: "head" }, h("span", { class: "badge", html: state === "wrong" ? ICON.x : ICON.check }), HEAD[lang][state],
      h("span", { class: "small muted", style: { fontFamily: "var(--font)", fontWeight: 700 } }, SUB[state])));
    if (state !== "correct" || ["dictation", "translate", "build", "speak_translate"].includes(ex.type)) {
      if (res.diff?.length && state !== "correct") {
        const ans = h("div", { class: "ans" });
        res.diff.forEach((d, k) => { if (k) ans.append(" "); ans.append(h("span", { class: d.s }, d.t)); });
        fb.append(h("div", { class: "small muted" }, ex.type.startsWith("speak") ? "What we expected (red = unclear):" : "Correct answer:"), ans);
      } else if (state !== "correct" || ex.type === "speak_translate") {
        fb.append(h("div", { class: "ans" }, res.expected));
      }
    }
    if (res.text && state !== "correct") fb.append(h("div", { class: "small" }, ex.type === "read_choose" ? "You read: " : "You heard: ", h("b", {}, res.text), " = ", res.expected));
    if (res.tip && ["listen_spell", "letter_listen"].includes(ex.type)) fb.append(h("div", { class: "small" }, res.tip));
    if (ex.type === "spell") fb.append(h("div", { class: "small muted" }, `Spelled: ${res.spelled} · ${res.en || ""}`));
    if (res.note && state !== "correct") fb.append(h("div", { class: "small" }, res.note));
    if (res.detail?.heard && state !== "correct") fb.append(h("div", { class: "small muted" }, `Heard: “${res.detail.heard}”`));
    res.categories?.forEach((c) => fb.append(h("div", { class: "cat" }, h("b", {}, c.label), h("span", { html: md(c.tip) }))));
    if (res.level_change) {
      const up = res.level_change.to > res.level_change.from;
      fb.append(h("div", { class: "level-change " + (up ? "up" : "down") }, h("b", {}, up ? `⬆ Level up: ${res.level_change.name}` : `⬇ Easing to ${res.level_change.name}`),
        h("div", { class: "small" }, res.level_change.reason, " ", res.level_change.desc)));
      toast(up ? `⬆ Challenge level ${res.level_change.to}: ${res.level_change.name}` : `Challenge level ${res.level_change.to}: ${res.level_change.name}`);
    }
    if (ex.type === "dictation" && res.en) fb.append(h("div", { class: "small muted" }, "Meaning: " + res.en));
    const replay = (["dictation", "translate", "build", "listen_choose", "read_choose", "speak_translate", "gender", "letter_listen", "spell"].includes(ex.type))
      ? h("button", { class: "btn ghost big", "aria-label": "Hear the answer", onclick: () => speech.say(res.say || res.text || res.expected.replace(/\s*\(.*\)$/, ""), lang) }, "▶") : null;
    setFoot({ state, content: fb, button: "Continue", onclick: next, secondary: replay });
    if (state === "correct") { burst(primary, 12); }
    else if (["dictation", "translate", "build", "spell"].includes(ex.type)) speech.say(res.expected, lang);
    else if (ex.type === "letter_listen") speech.say(res.say, lang);
    primary.focus();
  }

  // ------------------------------------------------------------ writing
  function renderWrite(step, node) {
    node.append(h("div", { class: "p-kicker" }, h("span", { class: "skill-tag", html: SKILL_ICON.writing + "writing" }), h("span", { class: "chip" }, "free writing")),
      h("h2", { class: "p-prompt" }, step.prompt));
    const ta = h("textarea", { placeholder: lang === "de" ? "Schreib hier…" : "Écris ici…", oninput: () => { primary.disabled = ta.value.trim().length < 3; } });
    node.append(ta, accentBar(lang, () => ta), h("div", { class: "muted small" }, h("span", { class: "kbd" }, "Ctrl"), " + ", h("span", { class: "kbd" }, "Enter"), " to submit"));
    setTimeout(() => ta.focus(), 60);
    const send = async () => {
      primary.disabled = true; primary.innerHTML = '<span class="spinner" style="width:20px;height:20px;border-width:3px"></span> Checking…';
      try {
        const fb = await api.post("/api/writing", { lang, text: ta.value, prompt: step.prompt, unit_id: step.unit_id });
        ta.disabled = true;
        node.append(writingFeedback(fb, step.model, lang));
        xp += 15; xpPill.textContent = `${xp} XP`;
        results.push({ ex: { type: "write", skill: "writing" }, res: { grade: fb.errors?.length ? "almost" : "correct", categories: [] } });
        setFoot({ onclick: next });
      } catch (e) { toast(e.message); setFoot({ button: "Try again", onclick: send }); }
    };
    setFoot({ button: "Get feedback", disabled: true, onclick: send });
  }

  // ------------------------------------------------------------ finish
  async function finish() {
    setProgress(); keyHandler = null;
    stage.innerHTML = "";
    const scored = results.filter((r) => r.ex.type !== "write");
    const right = scored.filter((r) => r.res.grade !== "wrong").length;
    const cats = {};
    scored.forEach((r) => r.res.categories?.forEach((c) => { cats[c.label] = (cats[c.label] || 0) + 1; }));
    const mistakes = scored.filter((r) => r.res.grade === "wrong");
    let extra = null;
    try { extra = await onComplete?.(); } catch (e) { toast(e.message); }
    const node = h("div", { class: "done-screen enter" });
    const acc = scored.length ? right / scored.length : 1;
    const cheer = { de: ["Super gemacht!", "Gut gemacht!", "Weiter so!"], fr: ["Bien joué !", "Pas mal !", "Courage !"] }[lang][acc >= 0.8 ? 0 : acc >= 0.5 ? 1 : 2];
    node.append(trophy(), h("h1", {}, cheer), h("p", { class: "muted" }, acc < 0.5 ? `${title}. Tough one! Every miss is now scheduled to come back sooner.` : title));
    const mins = Math.max(1, Math.round((Date.now() - startedAt) / 60000));
    node.append(h("div", { class: "done-stats" },
      h("div", { class: "card stat" }, h("b", {}, xp), h("span", { class: "muted small" }, "XP")),
      h("div", { class: "card stat" }, h("b", {}, scored.length ? pct(right / scored.length) : "–"), h("span", { class: "muted small" }, "accuracy")),
      h("div", { class: "card stat" }, h("b", {}, mins), h("span", { class: "muted small" }, "minutes"))));
    if (extra?.testout) {
      const box = h("div", { class: "card stack testout " + (extra.passed ? "pass" : "fail"), style: { width: "100%", maxWidth: "520px", textAlign: "left" } },
        h("h3", {}, extra.passed ? `✓ You already know “${extra.title}”` : `Not quite yet: ${pct(extra.score)} (you need ${pct(0.85)})`),
        h("p", { class: "muted" }, extra.passed
          ? "It's marked done, and its words will come back in your reviews in a few days to make sure they stick."
          : "No problem: now you know exactly what to learn. The lesson will teach it properly."));
      if (extra.missed?.length) box.append(h("div", { class: "row" }, h("span", { class: "small muted" }, "To learn:"), extra.missed.slice(0, 8).map((m) => h("span", { class: "chip" }, m))));
      if (!extra.passed && onRetry) box.append(h("div", {}, h("button", { class: "btn sun", onclick: () => { close(false); onRetry(); } }, "Start the lesson")));
      node.append(box);
    }
    if (extra?.scores) {
      node.append(h("div", { class: "card stack", style: { width: "100%", maxWidth: "520px", textAlign: "left" } }, h("h3", {}, "Checkpoint by skill"),
        ...Object.entries(extra.scores).map(([s, v]) => h("div", { class: "bar-row" }, h("span", { html: SKILL_ICON[s] + " " + s, class: "row" }), h("div", { class: "track" }, h("i", { style: { width: pct(v) } })), h("span", { class: "val" }, pct(v))))));
    }
    if (Object.keys(cats).length) {
      node.append(h("div", { class: "card stack", style: { width: "100%", maxWidth: "520px", textAlign: "left" } }, h("h3", {}, "Mistake patterns this session"),
        h("div", { class: "row" }, Object.entries(cats).sort((a, b) => b[1] - a[1]).map(([k, v]) => h("span", { class: "chip" }, `${k} × ${v}`))),
        h("p", { class: "muted small" }, "These feed your Insights page and get extra slots in upcoming mixes.")));
    }
    if (mistakes.length) {
      node.append(h("details", { class: "card fold", style: { width: "100%", maxWidth: "520px", textAlign: "left" } }, h("summary", {}, `Review ${mistakes.length} miss${mistakes.length > 1 ? "es" : ""}`),
        h("div", { class: "stack", style: { marginTop: "10px" } }, mistakes.map((m) => h("div", { class: "row" },
          h("button", { class: "icon-btn", html: ICON.speaker, onclick: () => speech.say(m.res.text || m.res.expected, lang) }),
          h("div", {}, h("b", {}, m.res.text || m.res.expected), h("div", { class: "muted small" }, m.res.en || "")))))));
    }
    stage.append(node);
    setTimeout(() => burst(node.querySelector(".trophy"), 24), 200);
    setFoot({ button: "Done", onclick: () => close(false) });
  }
  const startedAt = Date.now();

  render();
  return { close };
}

function table(rows) {
  const t = h("table", { class: "gt" });
  rows.forEach((r, k) => t.append(h("tr", {}, r.map((c) => h(k === 0 ? "th" : "td", { html: md(c) })))));
  return t;
}
export { table as grammarTable };

function trophy() {
  const w = h("div", { class: "trophy" });
  w.innerHTML = `<svg viewBox="0 0 150 150" class="trophy"><circle cx="75" cy="75" r="46" fill="var(--sun)"/><path d="M52 78 l16 16 l30 -34" fill="none" stroke="#2A2000" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
  <g class="s"><rect x="8" y="64" width="16" height="16" rx="2" fill="var(--m)"/><circle cx="134" cy="72" r="9" fill="var(--f)"/><path d="M75 4 l9 16 h-18z" fill="var(--n)"/><path d="M75 128 l9 9 l-9 9 l-9 -9z" fill="var(--pl)"/></g></svg>`;
  return w.firstChild;
}

export function writingFeedback(fb, model, lang) {
  const box = h("div", { class: "card stack" });
  if (fb.source === "claude") {
    box.append(h("div", { class: "row" }, h("span", { class: "chip level" }, fb.cefr || "?"), h("b", { style: { fontSize: "1.4rem", fontFamily: "var(--display)" } }, `${fb.score}/100`), h("span", { class: "muted" }, fb.summary)));
    if (fb.praise) box.append(h("div", { class: "chip sun", style: { justifySelf: "start" } }, "👏 " + fb.praise));
    if (fb.errors?.length) {
      box.append(h("h3", {}, "Corrections"));
      fb.errors.forEach((e) => box.append(h("div", { class: "gap-row", style: { gridTemplateColumns: "1fr" } },
        h("div", {}, h("s", { class: "muted" }, e.original), " → ", h("b", {}, e.correction), " ", h("span", { class: "chip" }, e.category.replace("_", " "))),
        h("div", { class: "small muted" }, e.explanation))));
    }
    box.append(h("div", { class: "ex", style: { background: "var(--surface-2)", padding: "12px", borderRadius: "12px" } }, h("div", { class: "tiny muted" }, "Corrected"), fb.corrected,
      h("button", { class: "btn ghost", style: { marginLeft: "8px", padding: "4px 10px" }, onclick: () => speech.say(fb.corrected, lang) }, "▶")));
    if (fb.next_focus) box.append(h("p", {}, h("b", {}, "Next focus: "), fb.next_focus));
  } else {
    box.append(h("h3", {}, "Self-check"));
    fb.checks?.forEach((c) => box.append(h("div", { class: "row" }, c.ok ? "✅" : "⚠️", c.text)));
    const m = fb.model || model;
    if (m) box.append(h("div", { class: "ex", style: { background: "var(--surface-2)", padding: "12px", borderRadius: "12px" } }, h("div", { class: "tiny muted" }, "Model answer"), m,
      h("button", { class: "btn ghost", style: { marginLeft: "8px", padding: "4px 10px" }, onclick: () => speech.say(m, lang) }, "▶")));
    box.append(h("p", { class: "muted small" }, fb.ai_error ? "Claude error: " + fb.ai_error : fb.summary));
  }
  return box;
}

const BRIDGE_LABEL = { same: "🌉 English", hook: "🌉 Remember it by", lit: "🌉 Literally", false: "⚠ False friend" };


/** 'Build on what you already know': English bridge + the same word in the language you've already learned. */
export function bridgeBoxes(it, { compact = false } = {}) {
  const out = [];
  if (it.bridge) {
    out.push(h("div", { class: `bridge ${it.bridge.kind}` }, h("b", {}, BRIDGE_LABEL[it.bridge.kind] + ": "), it.bridge.note));
  }
  for (const c of it.cross || []) {
    const word = h("b", { class: gclass(c.g, c.pos), style: { color: c.g ? "var(--g)" : "" } }, c.text);
    out.push(h("div", { class: "bridge cross" + (c.clash ? " clash" : "") }, flag(c.lang), h("b", {}, " You know: "),
      c.g ? shape(c.g, 14) : null, " ", word, compact || !c.note ? null : h("div", { class: "small" }, c.note)));
  }
  return out.length ? h("div", { class: "bridges" }, out) : null;
}
