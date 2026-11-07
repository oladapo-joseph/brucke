// Small DOM toolkit + the visual grammar language (shapes, colours, tagged text).

export function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "html") el.innerHTML = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "style" && typeof v === "object") for (const [sk, sv] of Object.entries(v)) sk.startsWith("--") ? el.style.setProperty(sk, sv) : (el.style[sk] = sv);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid == null || kid === false) continue;
    el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

/** Markdown-lite for grammar notes: **bold**, *italic*, ~~silent~~, ■●▲◆ coloured, newlines. */
export function md(s) {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/~~(.+?)~~/g, '<span class="silent">$1</span>')
    .replace(/■/g, '<span class="glyph g-m">■</span>').replace(/●/g, '<span class="glyph g-f">●</span>')
    .replace(/▲/g, '<span class="glyph g-n">▲</span>').replace(/◆/g, '<span class="glyph g-pl">◆</span>')
    .replace(/\n/g, "<br>");
}

export function gclass(g, pos) {
  if (g && ["m", "f", "n", "pl"].includes(g)) return `g-${g}`;
  if (pos === "verb") return "p-verb";
  if (pos === "adj") return "p-adj";
  return "";
}

export const GENDER_NAME = { m: "masculine", f: "feminine", n: "neuter", pl: "plural" };

/** The shape that goes with each gender / part of speech. */
export function shape(g, size = 18, pos) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("width", size); svg.setAttribute("height", size);
  svg.setAttribute("class", `shape ${gclass(g, pos)}`);
  svg.setAttribute("aria-hidden", "true");
  const p = document.createElementNS(ns, "path");
  const d = {
    m: "M4 4h16v16H4z",
    f: "M12 2a10 10 0 1 0 0 20a10 10 0 1 0 0-20z",
    n: "M12 2.5L22.5 21H1.5z",
    pl: "M12 1.5L22.5 12L12 22.5L1.5 12z",
    verb: "M3 9h10V3l9 9l-9 9v-6H3z",
    adj: "M2 13c3-6 6-6 10 0s7 6 10 0v4c-3 6-6 6-10 0s-7-6-10 0z",
  }[g || pos] || "M12 7a5 5 0 1 0 0 10a5 5 0 1 0 0-10z";
  p.setAttribute("d", d);
  if (g === "m") p.setAttribute("d", "M5 5h14v14H5z");
  svg.append(p);
  return svg;
}

/** Render tagged tokens: words are underlined in their grammar colour. */
export function tagged(tokens, { big = false } = {}) {
  const wrap = h("span", { class: "tagged" + (big ? " big" : "") });
  tokens.forEach((t, i) => {
    if (t.pos === "punct") { wrap.append(t.t); return; }
    if (i > 0 && wrap.childNodes.length) wrap.append(" ");
    const cls = gclass(t.g, t.pos);
    const coloured = cls && ["noun", "art", "verb", "adj"].includes(t.pos);
    wrap.append(h("span", { class: `w ${t.pos} ${coloured ? "c " + cls : ""}`, title: t.pos !== "other" ? posLabel(t) : null }, t.t));
  });
  return wrap;
}

export function posLabel(t) {
  if (t.pos === "noun" || t.pos === "art") return `${t.pos === "art" ? "article" : "noun"}${t.g ? " · " + GENDER_NAME[t.g] : ""}`;
  return { verb: "verb", adj: "adjective / adverb", pron: "pronoun", prep: "preposition", conj: "connector", q: "question word", det: "possessive", adv: "adverb", num: "number" }[t.pos] || t.pos;
}

/** Word with its article coloured: 'der Hund' → [■ der] Hund */
export function wordLabel(item) {
  const cls = gclass(item.g, item.pos);
  const m = item.text.match(/^(der|die|das|le|la|les|l')\s?(.*)$/i);
  const t = h("span", { class: "t" });
  if (m && item.pos === "noun") t.append(h("span", { class: "art" }, m[1] + (m[1].endsWith("'") ? "" : " ")), m[2]);
  else t.append(item.text);
  return { el: t, cls };
}

export const ICON = {
  play: '<svg viewBox="0 0 24 24"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.5-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z"/></svg>',
  slow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 16c0-5 4-9 9-9 4 0 7 3 7 6v3"/><path d="M19 16h2M3 16h16"/><circle cx="20" cy="10" r="1.5" fill="currentColor"/><path d="M6 16v3M15 16v3"/></svg>',
  mic: '<svg viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>',
  check: '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7"/></svg>',
  x: '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  dot: '<svg viewBox="0 0 24 24"><path d="M12 8v5M12 16.5v.5"/></svg>',
  close: '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  arrow: '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
  speaker: '<svg viewBox="0 0 24 24"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/></svg>',
};
export const SKILL_ICON = {
  listening: '<svg viewBox="0 0 24 24" class="ico"><path d="M6 15a7 7 0 1 1 12-5c0 3-2 4-3 5s-1 2-1 3a3 3 0 0 1-6 0"/><path d="M10 10a2 2 0 1 1 4 0"/></svg>',
  speaking: '<svg viewBox="0 0 24 24" class="ico"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>',
  reading: '<svg viewBox="0 0 24 24" class="ico"><path d="M2 5h6a4 4 0 0 1 4 4v11a3 3 0 0 0-3-3H2zM22 5h-6a4 4 0 0 0-4 4v11a3 3 0 0 1 3-3h7z"/></svg>',
  writing: '<svg viewBox="0 0 24 24" class="ico"><path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/></svg>',
};

export function flag(lang, big) { return h("span", { class: `flag ${lang}${big ? " big" : ""}`, "aria-hidden": "true" }); }

let toastTimer;
export function toast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg; t.classList.add("on");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove("on"), 2600);
}

const reduceMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Celebrate with the grammar shapes themselves. */
export function burst(fromEl, count = 12) {
  if (reduceMotion() || !fromEl) return;
  const r = fromEl.getBoundingClientRect();
  const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  const kinds = ["m", "f", "n", "pl"];
  for (let i = 0; i < count; i++) {
    const s = shape(kinds[i % 4], 14);
    s.classList.add("burst");
    s.style.left = cx + "px"; s.style.top = cy + "px";
    document.body.append(s);
    const ang = (Math.PI * 2 * i) / count + Math.random() * 0.5;
    const dist = 60 + Math.random() * 90;
    s.animate([
      { transform: "translate(-50%,-50%) scale(.4) rotate(0deg)", opacity: 1 },
      { transform: `translate(calc(-50% + ${Math.cos(ang) * dist}px), calc(-50% + ${Math.sin(ang) * dist - 30}px)) scale(1) rotate(${Math.random() * 360}deg)`, opacity: 0 },
    ], { duration: 700 + Math.random() * 300, easing: "cubic-bezier(.2,.8,.2,1)" }).onfinish = () => s.remove();
  }
}

export const ACCENTS = { de: ["ä", "ö", "ü", "ß", "Ä", "Ö", "Ü"], fr: ["é", "è", "ê", "à", "â", "ç", "ô", "û", "ù", "î", "ï", "ë", "œ", "É"] };

export function accentBar(lang, getInput) {
  return h("div", { class: "accents", "aria-label": "Special characters" },
    ACCENTS[lang].map((c) => h("button", {
      type: "button", tabindex: "-1", onmousedown: (e) => e.preventDefault(),
      onclick: () => {
        const inp = getInput(); if (!inp) return;
        const s = inp.selectionStart ?? inp.value.length, e = inp.selectionEnd ?? inp.value.length;
        inp.value = inp.value.slice(0, s) + c + inp.value.slice(e);
        inp.focus(); inp.setSelectionRange(s + 1, s + 1);
        inp.dispatchEvent(new Event("input"));
      },
    }, c)));
}

/** Hover tooltip for chart marks. */
export function tipOn(el, html) {
  const tip = document.getElementById("tip");
  el.addEventListener("mouseenter", () => { tip.innerHTML = html; tip.hidden = false; });
  el.addEventListener("mousemove", (e) => { tip.style.left = Math.min(e.clientX + 14, innerWidth - 270) + "px"; tip.style.top = e.clientY + 14 + "px"; });
  el.addEventListener("mouseleave", () => { tip.hidden = true; });
}

export function ring(value, size = 76) {
  const r = 32, c = 2 * Math.PI * r;
  const wrap = document.createElement("div");
  wrap.innerHTML = `<svg class="ring" viewBox="0 0 76 76" width="${size}" height="${size}"><circle class="bg" cx="38" cy="38" r="${r}"/><circle class="fg" cx="38" cy="38" r="${r}" stroke-dasharray="${c}" stroke-dashoffset="${c}"/></svg>`;
  const fg = wrap.querySelector(".fg");
  requestAnimationFrame(() => requestAnimationFrame(() => { fg.style.strokeDashoffset = c * (1 - Math.max(0, Math.min(1, value))); }));
  return wrap.firstChild;
}

export function pct(x) { return x == null ? "–" : Math.round(x * 100) + "%"; }
