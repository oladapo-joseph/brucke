"""Exercise generation: lessons, the adaptive daily mix, focused drills and checkpoints.

Principles:
  • recognition before production: new cards get multiple choice, mature cards get typing / speaking from memory
  • four skills, scheduled separately
  • weak skills and recurring mistake categories get extra slots
"""
from __future__ import annotations

import json
import random
import time
import uuid
from collections import Counter

from .content import LANGS, course
from . import challenge as ch
from .db import db
from .evaluate import CATEGORIES

SKILLS = ["listening", "speaking", "reading", "writing"]
KIND_SKILLS = {"vocab": SKILLS, "sentence": SKILLS, "sound": ["listening", "speaking"], "passage": ["reading"],
               "letter": ["listening", "speaking", "writing"]}
LETTER_TYPES = {"letter_listen", "spell", "speak"}

INSTRUCTIONS = {
    "listen_choose": "Listen. What does it mean?",
    "listen_spell": "Which word did you hear?",
    "dictation": "Type what you hear",
    "read_choose": "What does this mean?",
    "translate": "Write it in {lang}",
    "gender": "Pick the article",
    "build": "Build the sentence",
    "speak": "Say it out loud",
    "speak_translate": "Say it in {lang}, from memory",
    "reading_passage": "Read, then answer",
    "letter_listen": "Which letter did you hear?",
    "spell": "Listen to the spelling. Type the word",
}


# ---------------------------------------------------------------- building blocks
GENDER_NAME = {"m": "masculine", "f": "feminine", "n": "neuter", "pl": "plural"}


def known_ids(lang: str | None = None) -> set[str]:
    """Items the learner has met (has at least one card for). This is 'what the learner already knows'."""
    with db() as con:
        q = "SELECT DISTINCT item_id FROM cards" + (" WHERE lang=?" if lang else "")
        return {r["item_id"] for r in con.execute(q, (lang,) if lang else ())}


def cross(item: dict, known: set[str]) -> list[dict]:
    """Same word in the other language, but only if you've already learned it there."""
    out = []
    for o in course.cross_links(item):
        if o["id"] not in known:
            continue
        link = {"text": o["text"], "g": o.get("g"), "pos": o.get("pos"), "lang": o["lang"], "note": ""}
        if item.get("pos") == "noun" and o.get("pos") == "noun" and item.get("g") and o.get("g"):
            if item["g"] == o["g"]:
                link["note"] = f"Same gender in both, {GENDER_NAME[item['g']]}. Lucky!"
            else:
                link["note"] = (f"Careful: {o['text']} is {GENDER_NAME[o['g']]}, but {item['text']} is "
                                f"{GENDER_NAME[item['g']]}. Gender doesn't carry over.")
                link["clash"] = True
        out.append(link)
    return out[:2]


def display(item: dict, known: set[str] | None = None) -> dict:
    """Everything the UI needs to *teach* an item, linked to what the learner already knows."""
    lang = item["lang"]
    d = {"item_id": item["id"], "kind": item["kind"], "text": item["text"], "en": item.get("en", ""),
         "tags": course.tag(lang, item["text"]), "pos": item.get("pos"), "g": item.get("g"),
         "pl": item.get("pl"), "audio": item["text"]}
    if item.get("ex"):
        d["ex"] = {"t": item["ex"][0], "en": item["ex"][1], "tags": course.tag(lang, item["ex"][0])}
    if item["kind"] == "sound":
        d.update(pattern=item["pattern"], tip=item["tip"])
    if item["kind"] == "letter":
        d.update(letter=item["letter"], name=item["name"], like=item["like"], tip=item["tip"], tricky=item["tricky"],
                 word=item["word"], word_en=item["word_en"], audio=item["say"], spelled=spelled(item["word"], lang, "name"),
                 tags=course.tag(lang, item["word"]))
    if item["kind"] == "vocab" and item.get("pos") == "verb" and item.get("forms"):
        d["forms"] = item["forms"]
    if item.get("bridge"):
        d["bridge"] = item["bridge"]
    if known:
        d["cross"] = cross(item, known)
    return d


DECOY_SWAPS = {
    "de": {"der": "die", "die": "das", "das": "der", "den": "der", "einen": "ein", "ein": "einen", "eine": "ein",
           "kein": "keinen", "keine": "kein", "ist": "sind", "bin": "bist", "habe": "hat", "hat": "habe", "mein": "meine"},
    "fr": {"le": "la", "la": "le", "un": "une", "une": "un", "du": "de la", "est": "es", "suis": "es", "ai": "a",
           "mon": "ma", "ma": "mon", "ne": "pas", "des": "les"},
}


def make_decoys(item: dict, words: list[str], n: int) -> list[str]:
    """Wrong-but-tempting tiles: the article with the wrong gender, the wrong verb form…"""
    if n <= 0:
        return []
    lang, out = item["lang"], []
    lower = [w.lower() for w in words]
    cands = [DECOY_SWAPS[lang][w] for w in lower if w in DECOY_SWAPS[lang]]
    random.shuffle(cands)
    for d in cands:
        if d not in lower and d not in out:
            out.append(d)
        if len(out) >= n:
            break
    return out


def _distractors(item: dict, n: int, field="en", confusable: bool = False) -> list[str]:
    if confusable:  # harder: options that *look* like the answer
        from difflib import SequenceMatcher
        target = item["en"] if field == "en" else item["text"]
        pool = [course.items[i] for i in course.by_lang[item["lang"]]
                if i != item["id"] and course.items[i]["kind"] == item["kind"] and course.items[i]["stage"] <= item["stage"] + 1]
        vals = list({(p.get("en", "") if field == "en" else p["text"]) for p in pool} - {target, ""})
        vals.sort(key=lambda v: -SequenceMatcher(None, v.lower(), target.lower()).ratio())
        if len(vals) >= n:
            top = vals[:n * 2]
            random.shuffle(top)
            return top[:n]
    lang, kind = item["lang"], item["kind"]
    mine = {x.lower() for x in (item.get("en_all", []) if field == "en" else [item["text"]])}
    pool = [course.items[i] for i in course.by_lang[lang] if i != item["id"]]
    same_kind = [p for p in pool if p["kind"] == kind and (kind != "vocab" or p.get("pos") == item.get("pos"))]
    near = [p for p in same_kind if abs(p["stage"] - item["stage"]) <= 1] or same_kind
    rest = [p for p in pool if p["kind"] == kind]
    out: list[str] = []
    for group in (near, same_kind, rest):
        random.shuffle(group)
        for p in group:
            val = p.get("en", "") if field == "en" else p["text"]
            if val and val.lower() not in mine and val not in out:
                out.append(val)
            if len(out) >= n:
                return out
    return out


def choose_type(item: dict, skill: str, reps: int, level: int = ch.DEFAULT_LEVEL) -> str:
    """Recognition first, production once the card has matured. Higher challenge = production sooner."""
    kind = item["kind"]
    thr = ch.PRODUCTION_AFTER_REPS[level]
    if kind == "passage":
        return "reading_passage"
    if kind == "sound":
        return {"listening": "listen_spell", "speaking": "speak"}.get(skill, "listen_spell")
    if kind == "letter":
        return {"listening": "letter_listen", "speaking": "speak", "writing": "spell"}.get(skill, "letter_listen")
    if skill == "listening":
        return "listen_choose" if reps < thr else "dictation"
    if skill == "reading":
        return "read_choose"
    if skill == "speaking":
        return "speak" if reps < thr else "speak_translate"
    # writing
    if kind == "vocab":
        if item.get("pos") == "noun" and item.get("g") in ("m", "f", "n") and reps < min(thr, 1):
            return "gender"
        return "translate"
    return "build" if reps < thr else "translate"


def make_exercise(item: dict, skill: str, ex_type: str | None = None, reps: int = 0, level: int = ch.DEFAULT_LEVEL) -> dict:
    lang = item["lang"]
    t = ex_type or choose_type(item, skill, reps, level)
    # a type that doesn't fit the item falls back gracefully
    if t == "gender" and not (item.get("pos") == "noun" and item.get("g") in ("m", "f", "n")):
        t = "translate"
    if t == "build" and item["kind"] != "sentence":
        t = "translate"
    # e.g. a 'dictation' drill that lands on a letter becomes a spelling drill, and vice versa
    if (item["kind"] == "letter" and t not in LETTER_TYPES) or (item["kind"] != "letter" and t in ("letter_listen", "spell")):
        t = choose_type(item, skill, reps, level)
    ex = {"eid": uuid.uuid4().hex[:10], "item_id": item["id"], "skill": skill, "type": t, "lang": lang,
          "prompt": INSTRUCTIONS[t].format(lang=LANGS[lang]["name"]), "kind": item["kind"], "level": level,
          "slow_audio": ch.SLOW_AUDIO[level]}
    if t in ("listen_choose", "read_choose"):
        opts = _distractors(item, 3, confusable=ch.CONFUSABLE_OPTIONS[level]) + [item["en"]]
        random.shuffle(opts)
        ex.update(options=opts)
        if t == "listen_choose":
            ex["audio"] = item["text"]
        else:
            ex.update(show=item["text"], tags=course.tag(lang, item["text"]))
    elif t == "listen_spell":
        opts = _distractors(item, 3, field="text", confusable=ch.CONFUSABLE_OPTIONS[level]) + [item["text"]]
        random.shuffle(opts)
        ex.update(audio=item["text"], options=opts, pattern=item.get("pattern"))
    elif t == "dictation":
        ex.update(audio=item["text"], hint=item.get("en"))
    elif t == "translate":
        ex.update(en=item["en"], hint_g=item.get("g") if item.get("pos") == "noun" else None)
    elif t == "gender":
        ex.update(word=item["bare"], en=item["en"], options=LANGS[lang]["articles"], audio=None)
    elif t == "build":
        words = [tk["t"] for tk in course.tag(lang, item["text"]) if tk["pos"] != "punct"]
        tags = {tk["t"]: tk for tk in course.tag(lang, item["text"])}
        tiles = [{"t": w, "pos": tags.get(w, {}).get("pos", "other"), "g": tags.get(w, {}).get("g")} for w in words]
        for _ in range(5):
            random.shuffle(tiles)
            if [x["t"] for x in tiles] != words or len(words) < 2:
                break
        decoys = make_decoys(item, words, ch.DECOY_TILES[level])
        tiles += [{"t": d, "pos": course.lexicon[lang].get(d.lower(), {}).get("pos", "other"),
                   "g": course.lexicon[lang].get(d.lower(), {}).get("g")} for d in decoys]
        random.shuffle(tiles)
        ex.update(en=item["en"], tiles=tiles, decoys=len(decoys))
    elif t == "letter_listen":
        ex.update(audio=item["say"], options=letter_options(item), show_name=False)
    elif t == "spell":
        ex.update(audio=spelled(item["word"], lang), hint=item["word_en"], spell=True)
    elif t == "speak" and item["kind"] == "letter":
        ex.update(show=item["word"], tags=course.tag(lang, item["word"]), en=item["word_en"], audio=item["word"])
    elif t == "speak":
        ex.update(show=item["text"], tags=course.tag(lang, item["text"]), en=item.get("en"), audio=item["text"])
    elif t == "speak_translate":
        ex.update(en=item["en"])
    elif t == "reading_passage":
        ex.update(title=item["title"], show=item["text"], tags=course.tag(lang, item["text"]),
                  questions=[{"q": q["q"], "options": q["options"]} for q in item["questions"]],
                  translation=item.get("en"))
        for q in ex["questions"]:
            random.shuffle(q["options"])
    return ex


# ---------------------------------------------------------------- lessons
def unit_parts(unit: dict) -> list[dict]:
    ids = unit["item_ids"]
    parts: list[dict] = []

    def chunk(lst, size):  # balanced chunks: 19 words → 5/5/5/4 and 31 → 6/5/5/5/5/5, never a lonely 1
        if not lst:
            return []
        n = -(-len(lst) // size)
        q, r = divmod(len(lst), n)
        out, i = [], 0
        for k in range(n):
            step = q + (1 if k < r else 0)
            out.append(lst[i:i + step]); i += step
        return out

    for i, c in enumerate(chunk(ids.get("letters", []), 8)):
        parts.append({"title": f"Alphabet {i + 1}", "kind": "letters", "items": c})
    for i, c in enumerate(chunk(ids["sounds"], 8)):
        parts.append({"title": f"Sounds {i + 1}", "kind": "sounds", "items": c})
    for i, c in enumerate(chunk(ids["vocab"], 6)):
        parts.append({"title": f"Words {i + 1}", "kind": "words", "items": c})
    for i, c in enumerate(chunk(ids["sentences"], 5)):
        parts.append({"title": f"Sentences {i + 1}", "kind": "sentences", "items": c})
    parts.append({"title": "Read & write", "kind": "final", "items": ids["reading"]})
    # spread grammar notes over the teaching parts, in order
    teaching = [p for p in parts if p["kind"] != "final"] or parts
    for p in parts:
        p["grammar"] = []
    # notes with `at` go to a named part kind ('letters', 'letters:last', 'sounds', …); the rest in order
    free = [g for g in unit.get("grammar", []) if not g.get("at")]
    for g in unit.get("grammar", []):
        if g.get("at"):
            kind, _, pos = g["at"].partition(":")
            match = [p for p in teaching if p["kind"] == kind] or teaching
            (match[-1] if pos == "last" else match[0])["grammar"].append(g)
    unplaced = [p for p in teaching if not p["grammar"]] or teaching
    for gi, g in enumerate(free):
        unplaced[min(gi, len(unplaced) - 1)]["grammar"].append(g)
    for n, p in enumerate(parts):
        p["n"] = n
    return parts


def lesson_steps(unit: dict, part_n: int, known: set[str] | None = None, level: int = ch.DEFAULT_LEVEL) -> list[dict]:
    part = unit_parts(unit)[part_n]
    hard = ch.LESSON_PRODUCTION[level]

    def mk(it, skill, t):  # same exercise mix, but harder forms when you're coasting
        if hard:
            t = {"listen_choose": "dictation", "read_choose": "translate", "gender": "translate", "listen_spell": "listen_spell"}.get(t, t)
        return make_exercise(it, skill, t, level=level)
    steps: list[dict] = [{"step": "grammar", **g} for g in part["grammar"]]
    items = [course.items[i] for i in part["items"]]
    if part["kind"] == "final":
        for it in items:
            steps.append({"step": "exercise", "ex": make_exercise(it, "reading", "reading_passage")})
        if unit.get("writing_prompt"):
            steps.append({"step": "write", "prompt": unit["writing_prompt"], "model": unit.get("writing_model", ""),
                          "unit_id": unit["id"]})
        return steps
    # teach 3 → quiz those 3 → teach the next 3 …, then a short mixed recap
    for g in range(0, len(items), 3):
        group = items[g:g + 3]
        steps += [{"step": "teach", **display(it, known)} for it in group]
        quiz = []
        for it in group:
            if it["kind"] == "letter":
                quiz += [mk(it, "listening", "letter_listen"), mk(it, "writing" if hard else "speaking", "spell" if hard else "speak")]
            elif it["kind"] == "sound":
                quiz += [mk(it, "listening", "listen_spell"), mk(it, "speaking", "speak")]
            elif it["kind"] == "sentence":
                quiz += [mk(it, "listening", "listen_choose"), mk(it, "writing", "build")]
            else:
                quiz.append(mk(it, "listening", "listen_choose"))
                quiz.append(mk(it, "writing", "gender") if it.get("pos") == "noun" and it.get("g") in ("m", "f", "n")
                            else mk(it, "reading", "read_choose"))
        random.shuffle(quiz)
        steps += [{"step": "exercise", "ex": e} for e in quiz]
    if part["kind"] == "letters":
        # spelling practice, using only words made of letters you've learned so far
        parts = unit_parts(unit)
        taught = {course.items[i]["letter"].lower() for p in parts[:part_n + 1] if p["kind"] == "letters" for i in p["items"]}
        pool = [course.items[i] for p in parts if p["kind"] == "letters" for i in p["items"]]
        ok = [it for it in pool if set(it["word"].lower()) <= taught]
        last = part_n == max(p["n"] for p in parts if p["kind"] == "letters")
        for it in random.sample(ok, min(3 if last else 2, len(ok))):
            steps.append({"step": "exercise", "ex": make_exercise(it, "writing", "spell")})
        return steps
    recap_pool = [it for it in items if it["kind"] != "sound"]
    for it in random.sample(recap_pool, min(2, len(recap_pool))):
        steps.append({"step": "exercise", "ex": mk(it, "speaking", "speak_translate" if hard else "speak")})
    return steps


def testout_steps(unit: dict, part_n: int) -> list[dict]:
    """'I already know this': one production question per item, no teaching. Pass → skip the part."""
    part = unit_parts(unit)[part_n]
    exs = []
    for iid in part["items"]:
        it = course.items[iid]
        if it["kind"] == "letter":
            exs.append(make_exercise(it, "listening", "letter_listen"))
        elif it["kind"] == "sound":
            exs.append(make_exercise(it, "listening", "listen_spell"))
        elif it["kind"] in ("vocab", "sentence"):
            exs.append(make_exercise(it, "writing", "translate"))
    random.shuffle(exs)
    return [{"step": "exercise", "ex": e} for e in exs]


TESTOUT_PASS = 0.85


# ---------------------------------------------------------------- alphabet helpers
DOUBLE = {"de": "Doppel-", "fr": "deux "}


def letter_item(lang: str, ch: str) -> dict | None:
    return course.items.get(f"{lang}:ltr:{ch}") or course.items.get(f"{lang}:ltr:{ch.upper()}")


def spelled(word: str, lang: str, field: str = "say") -> str:
    """'Wasser' → 'We, A, Doppel-S, E, Er': what a German would say when spelling it out."""
    out, chars, i = [], [c for c in word if not c.isspace()], 0
    while i < len(chars):
        it = letter_item(lang, chars[i])
        say = it[field] if it else chars[i]
        if i + 1 < len(chars) and chars[i + 1].lower() == chars[i].lower():
            out.append(DOUBLE[lang] + say); i += 2
        else:
            out.append(say); i += 1
    return ", ".join(out)


def letter_options(item: dict) -> list[str]:
    """The right letter plus the ones English speakers typically confuse it with."""
    lang = item["lang"]
    opts = [item["letter"]]
    for c in item.get("confuse", []):
        if letter_item(lang, c) and c not in opts:
            opts.append(c)
    others = [course.items[i]["letter"] for i in course.by_lang[lang] if course.items[i]["kind"] == "letter"]
    random.shuffle(others)
    for c in others:
        if len(opts) >= 4:
            break
        if c not in opts:
            opts.append(c)
    opts = opts[:4]
    random.shuffle(opts)
    return opts


# ---------------------------------------------------------------- learner model queries
def skill_accuracy(con, lang: str, days: int = 14) -> dict[str, float]:
    since = time.time() - days * 86400
    out = {}
    for s in SKILLS:
        r = con.execute("SELECT COUNT(*) n, SUM(correct) c FROM attempts WHERE lang=? AND skill=? AND ts>?",
                        (lang, s, since)).fetchone()
        out[s] = (r["c"] or 0) / r["n"] if r["n"] else None
    return out


def category_counts(con, lang: str, days: int = 14, weighted: bool = False) -> Counter:
    """How often each mistake category occurred. weighted=True counts near-misses ('almost') as half,
    so outright errors win when the coach decides what to drill."""
    since = time.time() - days * 86400
    c: Counter = Counter()
    for r in con.execute("SELECT categories, grade FROM attempts WHERE lang=? AND ts>? AND categories!='[]'", (lang, since)):
        w = 0.5 if (weighted and r["grade"] == "almost") else 1
        for cat in json.loads(r["categories"]):
            c[cat] += w
    return c


def weak_items(con, lang: str, days: int = 14, limit: int = 30) -> list[dict]:
    since = time.time() - days * 86400
    rows = con.execute(
        "SELECT item_id, COUNT(*) misses, MAX(ts) last FROM attempts WHERE lang=? AND ts>? AND correct=0 "
        "GROUP BY item_id ORDER BY misses DESC, last DESC LIMIT ?", (lang, since, limit)).fetchall()
    return [dict(r) for r in rows if r["item_id"] in course.items]


# ---------------------------------------------------------------- adaptive session
DRILL_TYPES = {  # mistake category → (skill, exercise type, item filter)
    "gender": ("writing", "gender", lambda it: it.get("pos") == "noun" and it.get("g") in ("m", "f", "n")),
    "case": ("writing", "build", lambda it: it["kind"] == "sentence"),
    "conjugation": ("writing", "translate", lambda it: it["kind"] == "sentence" or it.get("pos") == "verb"),
    "endings": ("writing", "translate", lambda it: it["kind"] == "sentence"),
    "word_order": ("writing", "build", lambda it: it["kind"] == "sentence"),
    "missing_word": ("writing", "build", lambda it: it["kind"] == "sentence"),
    "letters": ("listening", "letter_listen", lambda it: it["kind"] == "letter"),
    "accents": ("listening", "dictation", lambda it: it["kind"] in ("vocab", "sentence")),
    "capitalization": ("listening", "dictation", lambda it: it["kind"] in ("vocab", "sentence")),
    "spelling": ("listening", "dictation", lambda it: it["kind"] in ("vocab", "sentence", "letter")),
    "vocabulary": ("writing", "translate", lambda it: it["kind"] == "vocab"),
    "listening": ("listening", "listen_choose", lambda it: it["kind"] in ("vocab", "sentence", "letter")),
    "pronunciation": ("speaking", "speak", lambda it: it["kind"] in ("vocab", "sentence", "sound")),
    "comprehension": ("reading", "read_choose", lambda it: it["kind"] == "sentence"),
}


def build_session(lang: str, size: int | None = None, focus: str | None = None) -> dict:
    """The daily mix. focus = a skill name, a mistake category, or 'gaps'."""
    level = ch.level(lang)
    size = size or ch.SESSION_SIZE[level]
    now = time.time()
    with db() as con:
        cards = [dict(r) for r in con.execute("SELECT * FROM cards WHERE lang=?", (lang,))]
        cards = [c for c in cards if c["item_id"] in course.items]
        if not cards:
            return {"exercises": [], "empty": True, "reason": "Finish your first lesson part to unlock practice."}
        acc = skill_accuracy(con, lang)
        cats = category_counts(con, lang, weighted=True)
        weak = weak_items(con, lang)
    by_key = {(c["item_id"], c["skill"]): c for c in cards}
    known_items = sorted({c["item_id"] for c in cards}, key=lambda i: course.items[i]["stage"])
    picks: list[tuple[dict, str, str | None, str]] = []   # (item, skill, forced type, why)
    used: set[tuple[str, str]] = set()

    def add(item_id, skill, forced=None, why="review"):
        it = course.items[item_id]
        if skill not in KIND_SKILLS[it["kind"]] or (item_id, skill) in used:
            return False
        used.add((item_id, skill))
        picks.append((it, skill, forced, why))
        return True

    focus_cats: list[str] = []
    if focus in CATEGORIES:
        focus_cats = [focus]
    elif focus is None and cats:
        focus_cats = [c for c, _ in cats.most_common(2)]

    # 1) targeted drills for recurring mistakes (~40% of the mix, shared fairly between the top categories;
    #    the whole session if you picked a category yourself)
    n_focus = size if focus in CATEGORIES else (round(size * 0.4) if focus_cats else 0)
    weak_ids = [w["item_id"] for w in weak]
    quota = -(-n_focus // len(focus_cats)) if focus_cats else 0
    for cat in focus_cats:
        skill, etype, ok = DRILL_TYPES[cat]
        cands = list(dict.fromkeys([i for i in weak_ids if ok(course.items[i])] + [i for i in known_items if ok(course.items[i])]))
        got = 0
        for iid in cands:
            if got >= quota or sum(p[3].startswith("focus") for p in picks) >= n_focus:
                break
            got += add(iid, skill, etype, f"focus:{cat}")

    # 2) gaps-only session
    if focus == "gaps":
        for w in weak:
            it = course.items[w["item_id"]]
            for s in KIND_SKILLS[it["kind"]]:
                if len(picks) < size:
                    add(it["id"], s, None, "gap")

    # 3) due cards, weighted toward weaker skills
    skill_w = {s: 0.6 + 2.0 * (1 - (acc[s] if acc[s] is not None else 0.7)) for s in SKILLS}
    if focus in SKILLS:
        skill_w = {s: (5.0 if s == focus else 0.3) for s in SKILLS}
    due = sorted([c for c in cards if c["due"] <= now], key=lambda c: (c["due"], -c["lapses"]))
    while len(picks) < size and due:
        weights = [skill_w[c["skill"]] for c in due]
        c = random.choices(due, weights=weights, k=1)[0]
        due.remove(c)
        add(c["item_id"], c["skill"], None, "due")

    # 4) top up with the weakest known cards (lowest interval first)
    if len(picks) < size:
        rest = sorted(cards, key=lambda c: (c["interval"], -c["lapses"], random.random()))
        for c in rest:
            if len(picks) >= size:
                break
            if focus in SKILLS and c["skill"] != focus:
                continue
            add(c["item_id"], c["skill"], None, "strengthen")

    # 5) if focused on a skill and still short, create cards for known items in that skill
    if focus in SKILLS and len(picks) < size:
        for iid in known_items:
            if len(picks) >= size:
                break
            add(iid, focus, None, "stretch")

    random.shuffle(picks)
    # avoid the same item twice in a row
    for i in range(1, len(picks)):
        if picks[i][0]["id"] == picks[i - 1][0]["id"]:
            j = (i + 2) % len(picks)
            picks[i], picks[j] = picks[j], picks[i]
    exercises = []
    for it, skill, forced, why in picks:
        reps = by_key.get((it["id"], skill), {}).get("reps", 0)
        ex = make_exercise(it, skill, forced, reps, level)
        ex["why"] = why
        exercises.append(ex)
    return {"exercises": exercises, "focus": focus, "focus_categories": focus_cats, "level": level,
            "skill_accuracy": acc}


def build_checkpoint(lang: str, per_skill: int = 5) -> dict:
    """Production-only test across everything learned so far. Results stay separate from SRS."""
    with db() as con:
        rows = con.execute("SELECT DISTINCT item_id FROM cards WHERE lang=?", (lang,)).fetchall()
    known = [course.items[r["item_id"]] for r in rows if r["item_id"] in course.items]
    if len(known) < 8:
        return {"exercises": [], "empty": True, "reason": "Learn a few more lessons first (about 8 items)."}
    sid = uuid.uuid4().hex[:12]
    exs = []
    plan = {"listening": ("dictation", ["vocab", "sentence"]), "speaking": ("speak_translate", ["sentence", "vocab"]),
            "reading": ("read_choose", ["sentence"]), "writing": ("translate", ["sentence", "vocab"])}
    for skill, (etype, kinds) in plan.items():
        pool = [it for it in known if it["kind"] in kinds]
        pool.sort(key=lambda it: (-it["stage"], random.random()))
        for it in pool[:per_skill * 3][::3][:per_skill] or pool[:per_skill]:
            exs.append(make_exercise(it, skill, etype))
    passages = [it for it in known if it["kind"] == "passage"]
    if passages:
        exs.append(make_exercise(max(passages, key=lambda p: p["stage"]), "reading", "reading_passage"))
    random.shuffle(exs)
    return {"exercises": exs, "session_id": sid}
