// Text-to-speech and speech recognition via the browser's Web Speech API.
// Chrome/Edge ship good German and French voices and online speech recognition.

const LOCALE = { de: "de-DE", fr: "fr-FR" };
let voices = [];
const loadVoices = () => { voices = speechSynthesis.getVoices(); };
if ("speechSynthesis" in window) { loadVoices(); speechSynthesis.onvoiceschanged = loadVoices; }

export const speech = {
  rate: 0.95,
  preferred: { de: "", fr: "" },

  voicesFor(lang) {
    const loc = LOCALE[lang];
    return voices.filter((v) => v.lang?.replace("_", "-").toLowerCase().startsWith(loc.slice(0, 2)));
  },

  pickVoice(lang) {
    const list = this.voicesFor(lang);
    return list.find((v) => v.name === this.preferred[lang])
      || list.find((v) => /google/i.test(v.name) && v.lang.startsWith(LOCALE[lang]))
      || list.find((v) => /natural|neural|premium|enhanced/i.test(v.name))
      || list.find((v) => v.lang === LOCALE[lang]) || list[0] || null;
  },

  canSpeak: () => "speechSynthesis" in window,
  canListen: () => !!(window.SpeechRecognition || window.webkitSpeechRecognition),

  /** Speak text. Resolves when finished. `btn` gets a .speaking class while audio plays. */
  say(text, lang, { slow = false, btn = null } = {}) {
    return new Promise((resolve) => {
      if (!this.canSpeak() || !text) return resolve();
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = LOCALE[lang];
      const v = this.pickVoice(lang);
      if (v) u.voice = v;
      u.rate = slow ? Math.max(0.5, this.rate * 0.62) : this.rate;
      const done = () => { btn?.classList.remove("speaking"); resolve(); };
      u.onstart = () => btn?.classList.add("speaking");
      u.onend = done; u.onerror = done;
      speechSynthesis.speak(u);
      setTimeout(done, 15000);
    });
  },

  stop() { if (this.canSpeak()) speechSynthesis.cancel(); },

  /** Listen once. onInterim(text) streams partial results. Resolves to a list of alternatives. */
  listen(lang, { onInterim, maxMs = 9000 } = {}) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return { promise: Promise.reject(new Error("unsupported")), stop() {} };
    const rec = new SR();
    rec.lang = LOCALE[lang]; rec.interimResults = true; rec.maxAlternatives = 3; rec.continuous = false;
    let finals = [], timer;
    const promise = new Promise((resolve, reject) => {
      rec.onresult = (e) => {
        let interim = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
          const res = e.results[i];
          if (res.isFinal) finals = Array.from(res).map((a) => a.transcript.trim());
          else interim += res[0].transcript;
        }
        onInterim?.(finals[0] || interim);
      };
      rec.onerror = (e) => { clearTimeout(timer); e.error === "no-speech" ? resolve([]) : reject(new Error(e.error)); };
      rec.onend = () => { clearTimeout(timer); resolve(finals); };
      this.stop();
      rec.start();
      timer = setTimeout(() => rec.stop(), maxMs);
    });
    return { promise, stop: () => rec.stop() };
  },
};
