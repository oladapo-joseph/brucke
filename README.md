# Brücke 🌉 · German & French, A1 → B1 in 26 weeks

A personal language trainer built with FastAPI and plain JavaScript. English is the bridge (*die Brücke*): every
explanation is in English, and the two languages are compared with each other wherever that helps.

## Run it

```bash
pip install -r requirements.txt
# optional: put ANTHROPIC_API_KEY=sk-ant-... in a .env file next to this README (it's git-ignored)
./run.sh                                # → http://localhost:8000
```

Use **Chrome or Edge**. They have the best German/French voices and speech recognition. Allow the microphone when asked.
Your progress lives in `data/bruecke.db` (one SQLite file; back it up to keep your history).

## What's inside

| | |
|---|---|
| **4 skills, scheduled separately** | Every item has a listening, speaking, reading and writing card. You can read *der Hund* and still mishear it. |
| **Recognition → production** | New cards get multiple choice; as they mature they switch to dictation, translation and speaking from memory. |
| **Mistake diagnosis** | Every wrong answer is classified: gender, case, conjugation, endings, word order, accents, noun capitals, spelling, missing words, vocabulary, listening, pronunciation, comprehension. |
| **Learns from your gaps** | The daily mix gives ~30% of its slots to your top recurring mistake types, weights weaker skills higher, and brings back items you keep missing. Insights shows trends, persistent gaps and gender slips. |
| **Colour + shape grammar** | ■ blue = masculine, ● rose = feminine, ▲ green = neuter, ◆ violet = plural, ➜ orange = verbs. The same everywhere: words, sentences, tiles, gender buttons, even the celebration confetti. The shapes mean it still works for colour-blind eyes. |
| **Staggered schedule** | German from week 1, French from week 3 (configurable). Each day has a concrete plan; Sundays are for review; checkpoint tests in weeks 4, 8, 13, 17, 22 and 26; catch-up blocks if you fall behind. |
| **Speaking** | Hear native-speed and slow audio, then speak. You're scored word by word, with unclear words highlighted. |

## Content

* **Stages 1–8 (A1)** are hand-written for both languages: the alphabet and spelling, sounds, greetings, gender,
  numbers 0–100, family, daily routine, food, time.
  * **Alphabet (stage 1, week 1):** every letter's name, with the traps for English speakers drilled extra
    (German E/I/J/V/W/Z, French G/J swap, spelled-out accents). Spelling drills use words built only from letters you've learned.
  * **Numbers (stage 4):** 0–20, the tens, German "backwards" numbers (einundzwanzig), French 70–99 (soixante-dix, quatre-vingts).
* **Stages 9–26 (A2–B1)** are outlines (`app/content/syllabus.py`). With an API key, open one in **Journey** and press
  *Generate*: Claude writes the full unit in the same format and saves it to `data/generated/<lang>-<stage>.json`,
  where you can edit it. You can also write units by hand in `app/content/de.py` / `fr.py`.

## How it teaches

**1. Start from what you already know** (Ausubel: *"the most important single factor influencing learning is what the learner already knows"*)
* 🌉 **Bridges**: most words link to English you already own: a cognate (*Haus* → house), a memory hook (*Hund* → hound,
  *chien* → canine), the literal meaning (*Wochenende* → week-end) or a ⚠ false friend (*Handy* = mobile phone). Edit them in `app/content/bridges.py`.
* **Decoding rules**: the English↔German consonant shifts (t→z/ss, d→t, p→f, k→ch) and English↔French patterns (-té = -ty, é- = s-).
* **German → French**: French cards show the German word you've already learned, and flag it when the gender differs (*der Tisch* vs *la table*).
* **"I know this"**: test out of any lesson part. 85% or more and it's marked done, so you never sit through what you already know.

**2. Keep you in the sweet spot** (the "85% rule": learning is fastest at about 85% correct)
* **Challenge level 1–5 per language**, adjusted automatically from your last 40 answers: above 93% it gets tougher, below 70% it eases off.
  Higher levels mean typing and speaking from memory sooner, look-alike options, decoy tiles, strict accent grading, longer sessions and no slow replays.
  You can pin a level in Settings.
* **Pace**: the plan measures your real speed, forecasts your B1 finish week, adds a fast-track push when you're ahead or coasting,
  and unlocks **stretch stages 27–32 (towards B2)** once you're 2 stages ahead (or on demand in Settings).

## Claude features (optional)

With `ANTHROPIC_API_KEY` set:
* **Writing studio**: corrections, a score, a CEFR estimate, and every error tagged with the same categories as the drills, so free writing feeds your Insights too.
* **Unit generation** for stages 9–26.

Uses `claude-opus-5-5` (changeable via the `ai_model` setting) with structured JSON output and server-side refusal fallback.
Without a key, everything else works offline; writing gets rule-based checks plus a model answer.

## Keyboard

`Enter` check / continue · `1–4` pick an answer · `Space` replay audio / start the mic · `Esc` leave · `Ctrl+Enter` submit writing.

## Code map

```
app/main.py          FastAPI routes
app/evaluate.py      answer checking + mistake diagnosis (the heart of "learn from my mistakes")
app/exercises.py     lessons, adaptive daily mix, drills, checkpoints
app/srs.py           spaced repetition (SM-2 variant, one card per item × skill)
app/insights.py      analytics + recommendations
app/schedule.py      26-week staggered plan + daily blocks
app/ai.py            optional Claude features
app/content/         course content, syllabus, lexicon/colour tagging
static/              single-page UI (no build step)
tests/               pytest suite: python -m pytest -q
```
