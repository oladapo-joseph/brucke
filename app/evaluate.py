"""Answer checking and *mistake diagnosis*.

The point isn't just right/wrong: every mistake gets one or more category tags
(gender, word order, conjugation…) so the insights engine can find patterns.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from .content import course

CATEGORIES = {
    "letters":       {"label": "Letter names & spelling", "drill": "letter_listen"},
    "gender":        {"label": "Gender & articles",      "drill": "gender"},
    "case":          {"label": "Case endings",           "drill": "build"},
    "conjugation":   {"label": "Verb conjugation",       "drill": "translate"},
    "endings":       {"label": "Word endings & agreement", "drill": "translate"},
    "word_order":    {"label": "Word order",             "drill": "build"},
    "accents":       {"label": "Accents & umlauts",      "drill": "dictation"},
    "capitalization": {"label": "Noun capitals",         "drill": "dictation"},
    "spelling":      {"label": "Spelling",               "drill": "dictation"},
    "missing_word":  {"label": "Missing / extra words",          "drill": "build"},
    "vocabulary":    {"label": "Vocabulary recall",      "drill": "translate"},
    "listening":     {"label": "Listening",              "drill": "listen"},
    "pronunciation": {"label": "Pronunciation",          "drill": "speak"},
    "comprehension": {"label": "Reading comprehension",  "drill": "read"},
}

TIPS = {
    "de": {
        "letters": "The traps for English speakers: E sounds like 'ay', I like 'ee', J is 'yot', V is 'fow', W is 'vay', Z is 'tset'.",
        "gender": "Say every noun out loud *with* its article (der Tisch, die Lampe). Colour + shape = gender: ■ der, ● die, ▲ das.",
        "case": "Only masculine changes in the accusative: der → den, ein → einen. After 'haben', 'möchten' and 'nehmen' you need the accusative.",
        "conjugation": "Check the ending against the person: ich -e, du -st, er/sie/es -t, wir/sie/Sie -en.",
        "endings": "Look at the end of the word: it has to match the person or the noun.",
        "word_order": "The conjugated verb goes in position 2. If a time word comes first, the subject moves *after* the verb. Separable prefixes go to the end.",
        "accents": "Umlauts change the word: schon (already) ≠ schön (beautiful). Type ae/oe/ue if you have to.",
        "capitalization": "All German nouns start with a capital letter, even in the middle of a sentence.",
        "spelling": "Listen again at slow speed and spell it syllable by syllable.",
        "missing_word": "German rarely drops words. Check for articles and small words like 'ein' or 'nicht'.",
        "vocabulary": "This word hasn't stuck yet. It will come back more often until it does.",
        "listening": "Replay at slow speed and try to catch the stressed syllable first.",
        "pronunciation": "Shadow the audio: play it, then speak *with* it at the same time. Focus on the words highlighted in red.",
        "comprehension": "Skim for nouns (they're capitalised) to get the topic, then read the question again.",
    },
    "fr": {
        "letters": "The traps for English speakers: G is 'zhay' and J is 'zhee' (swapped vs English), E is 'uh', I is 'ee', and accents are spelled out (e accent aigu).",
        "gender": "Learn every noun with le/la, especially l' words, where the article hides the gender. ■ le, ● la.",
        "case": "Check the article: du / de la / des after verbs like manger or boire, and de after a negative.",
        "conjugation": "Most -er forms sound the same but are spelled differently: je parle, tu parles, ils parlent.",
        "endings": "Adjectives and participles agree: grand → grande (f), grands (pl).",
        "word_order": "Negation wraps the verb (ne … pas). Most adjectives go after the noun.",
        "accents": "Accents change sound and meaning: ou (or) ≠ où (where), a (has) ≠ à (to).",
        "capitalization": "French keeps capitals for names and the start of sentences, not days or languages.",
        "spelling": "Many final letters are silent but still written. Listen, then check the ending.",
        "missing_word": "French needs small words: articles (le, du), ne … pas, and que.",
        "vocabulary": "This word hasn't stuck yet. It will come back more often until it does.",
        "listening": "French links words together (liaison). Replay slowly and listen for the word boundaries.",
        "pronunciation": "Shadow the audio and exaggerate the nasal vowels and the throaty r.",
        "comprehension": "Look for words you recognise from English (cognates), then reread the question.",
    },
}

ARTICLES = {
    "de": {"der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einem", "einer", "eines",
           "kein", "keine", "keinen", "keinem", "keiner", "mein", "meine", "meinen", "dein", "deine", "deinen",
           "sein", "seine", "seinen", "ihr", "ihre", "ihren", "unser", "unsere"},
    "fr": {"le", "la", "l'", "les", "un", "une", "des", "du", "de", "d'", "mon", "ma", "mes", "ton", "ta", "tes",
           "son", "sa", "ses", "ce", "cet", "cette", "ces", "au", "aux"},
}
DE_NOMINATIVE = {"der", "die", "das"}

NUMBERS = {
    "de": ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf",
           "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn", "zwanzig"],
    "fr": ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze",
           "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf", "vingt"],
}
TENS = {
    "de": {20: "zwanzig", 30: "dreißig", 40: "vierzig", 50: "fünfzig", 60: "sechzig", 70: "siebzig", 80: "achtzig", 90: "neunzig"},
    "fr": {20: "vingt", 30: "trente", 40: "quarante", 50: "cinquante", 60: "soixante"},
}


def number_word(n: int, lang: str) -> str | None:
    """0–100 as words: 21 → 'einundzwanzig' / 'vingt et un', 97 → 'quatre-vingt-dix-sept'."""
    units = NUMBERS[lang]
    if 0 <= n < len(units):
        return units[n]
    if n == 100:
        return "hundert" if lang == "de" else "cent"
    if not 20 < n < 100:
        return None
    t, o = divmod(n, 10)
    if lang == "de":
        return TENS["de"][t * 10] if o == 0 else ("ein" if o == 1 else units[o]) + "und" + TENS["de"][t * 10]
    if n < 70:
        base = TENS["fr"][t * 10]
        return base if o == 0 else (f"{base} et un" if o == 1 else f"{base}-{units[o]}")
    if n < 80:  # 70–79 = soixante + 10–19
        return "soixante et onze" if n == 71 else f"soixante-{units[n - 60]}"
    if n == 80:
        return "quatre-vingts"
    return f"quatre-vingt-{units[n - 80]}"  # 81–99 = quatre-vingt + 1–19


# ---------------------------------------------------------------- normalisation
def norm(s: str, lang: str = "") -> str:
    s = s.replace("’", "'").replace("‘", "'").replace("´", "'").strip()
    s = re.sub(r"[.,!?;:«»\"“”„()\[\]–—…¿¡]", " ", s)
    s = re.sub(r"\s+-\s+", " ", s)
    if lang == "fr":  # split elisions so l'école ≡ l' école
        s = re.sub(r"\b(l|d|j|n|m|t|s|c|qu)'\s*", r"\1' ", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip()


def tokens(s: str, lang: str = "", keep_case=False) -> list[str]:
    n = norm(s, lang)
    return (n if keep_case else n.lower()).split()


def fold_umlaut(s: str) -> str:
    """ä→ae etc. then strip any remaining accent — 'Maedchen' and 'Mädchen' fold the same."""
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = s.replace("œ", "oe").replace("æ", "ae")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def fold_plain(s: str) -> str:
    s = s.lower().replace("ß", "ss").replace("œ", "oe")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# ---------------------------------------------------------------- result
@dataclass
class Check:
    grade: str                      # correct | almost | wrong
    expected: str
    categories: list[str] = field(default_factory=list)
    diff: list[dict] = field(default_factory=list)   # [{t, s: ok|wrong|missing|extra}]
    note: str = ""
    score: float = 1.0
    detail: dict = field(default_factory=dict)

    @property
    def correct(self) -> bool:
        return self.grade != "wrong"


def _diff(user_t: list[str], exp_t: list[str], exp_display: list[str]) -> list[dict]:
    out = []
    sm = SequenceMatcher(None, [fold_umlaut(t) for t in user_t], [fold_umlaut(t) for t in exp_t], autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out += [{"t": exp_display[j], "s": "ok"} for j in range(j1, j2)]
        elif op == "replace":
            out += [{"t": exp_display[j], "s": "wrong", "you": " ".join(user_t[i1:i2])} for j in range(j1, j2)]
        elif op == "insert":
            out += [{"t": exp_display[j], "s": "missing"} for j in range(j1, j2)]
        elif op == "delete":
            out += [{"t": user_t[i], "s": "extra"} for i in range(i1, i2)]
    return out


def _is_verb_form(lang: str, tok: str) -> bool:
    return course.lexicon[lang].get(tok, {}).get("pos") == "verb"


def check_text(user: str, accepted: list[str], lang: str) -> Check:
    """Compare a typed answer against all accepted answers and diagnose the mistake."""
    user = user.strip()
    if not user:
        exp = accepted[0]
        return Check("wrong", exp, ["vocabulary"], [{"t": t, "s": "missing"} for t in tokens(exp, lang, True)], "No answer given.", 0.0)

    # pick the accepted answer closest to what the user wrote
    best = max(accepted, key=lambda a: ratio(fold_umlaut(norm(user, lang)), fold_umlaut(norm(a, lang))))
    u, e = tokens(user, lang), tokens(best, lang)
    e_disp = tokens(best, lang, keep_case=True)

    if u == e:
        if lang == "de":  # nouns must be capitalised
            uc, ec = tokens(user, lang, True), e_disp
            bad = [ec[i] for i in range(1, len(ec)) if i < len(uc) and ec[i][:1].isupper() and uc[i][:1].islower()]
            if bad:
                return Check("almost", best, ["capitalization"],
                             [{"t": t, "s": "wrong" if t in bad else "ok"} for t in ec],
                             f"Capitalise the noun{'s' if len(bad) > 1 else ''}: {', '.join(bad)}", 0.9)
        return Check("correct", best, [], [{"t": t, "s": "ok"} for t in e_disp], score=1.0)

    diff = _diff(u, e, e_disp)
    # accents / umlauts only
    if [fold_umlaut(t) for t in u] == [fold_umlaut(t) for t in e] or [fold_plain(t) for t in u] == [fold_plain(t) for t in e]:
        wrong = [e_disp[i] for i in range(len(e)) if i < len(u) and u[i] != e[i]]
        return Check("almost", best, ["accents"],
                     [{"t": t, "s": "wrong" if t in wrong else "ok"} for t in e_disp],
                     f"Watch the accents: {', '.join(wrong)}", 0.9)
    # same words, different order
    if Counter(fold_umlaut(t) for t in u) == Counter(fold_umlaut(t) for t in e):
        return Check("wrong", best, ["word_order"], [{"t": t, "s": "ok"} for t in e_disp],
                     "All the right words, but the order is off.", 0.6)

    cats: list[str] = []
    notes: list[str] = []
    arts = ARTICLES[lang]
    sm = SequenceMatcher(None, [fold_umlaut(t) for t in u], [fold_umlaut(t) for t in e], autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        ut, et = u[i1:i2], e[j1:j2]
        if op == "replace" and len(ut) == len(et):
            for k, (a, b) in enumerate(zip(ut, et)):
                bd = e_disp[j1 + k]
                is_noun = course.lexicon[lang].get(b, {}).get("pos") == "noun" or (lang == "de" and bd[:1].isupper() and j1 + k > 0)
                if a in arts and b in arts:
                    if lang == "de" and not (a in DE_NOMINATIVE and b in DE_NOMINATIVE):
                        cats.append("case"); notes.append(f"'{bd}' not '{a}'")
                    else:
                        cats.append("gender"); notes.append(f"'{bd}' not '{a}'")
                elif not is_noun and ratio(fold_umlaut(a), fold_umlaut(b)) >= 0.6 and _common_prefix(a, b) >= max(3, len(fold_umlaut(b)) - 3):
                    cats.append("conjugation" if _is_verb_form(lang, b) else "endings")
                    notes.append(f"'{bd}' not '{a}'")
                elif ratio(fold_umlaut(a), fold_umlaut(b)) >= 0.7:
                    cats.append("spelling"); notes.append(f"'{bd}' not '{a}'")
                else:
                    cats.append("vocabulary"); notes.append(f"'{bd}' not '{a}'")
        elif op == "insert":
            if all(t in arts for t in et):
                cats.append("gender"); notes.append(f"missing article '{' '.join(et)}'")
            else:
                cats.append("missing_word"); notes.append(f"missing '{' '.join(et)}'")
        elif op == "delete":
            cats.append("gender" if all(t in arts for t in ut) else "missing_word"); notes.append(f"extra '{' '.join(ut)}'")
        else:  # unequal replace
            r = ratio(fold_umlaut(" ".join(ut)), fold_umlaut(" ".join(et)))
            cats.append("spelling" if r >= 0.75 else "vocabulary"); notes.append(f"'{' '.join(et)}' not '{' '.join(ut)}'")

    cats = list(dict.fromkeys(cats)) or ["vocabulary"]
    overall = ratio(fold_umlaut(" ".join(u)), fold_umlaut(" ".join(e)))
    # single small slip in a longer answer → almost
    grade = "almost" if (len(notes) == 1 and cats[0] in ("spelling",) and overall >= 0.9) else "wrong"
    return Check(grade, best, cats, diff, "; ".join(notes[:3]), round(overall, 2))


def _common_prefix(a: str, b: str) -> int:
    n = 0
    for x, y in zip(fold_umlaut(a), fold_umlaut(b)):
        if x != y:
            break
        n += 1
    return n


# ---------------------------------------------------------------- speech
def _num_words(tok: str, lang: str) -> str:
    tok = re.sub(r":00$", "", tok)
    if tok.isdigit():
        return number_word(int(tok), lang) or tok
    return tok


def _sp(t: str) -> str:
    return t.lower().replace("ß", "ss")


def check_speech(transcripts: list[str], target: str, lang: str) -> Check:
    """Score what the recogniser heard against the target sentence, word by word."""
    if lang == "fr":  # recognisers differ on 'vingt-et-un' vs 'vingt et un': compare without hyphens
        target = target.replace("-", " ")
        transcripts = [t.replace("-", " ") for t in (transcripts or [])]
    e_disp = tokens(target, lang, keep_case=True)
    # speech: keep umlauts/accents (the recogniser spells them), so 'schon' ≠ 'schön'
    e = [_sp(t) for t in tokens(target, lang)]
    best_score, best_diff, best_heard = 0.0, [], ""
    for tr in transcripts or [""]:
        expanded = " ".join(_num_words(t, lang) for t in tokens(tr, lang))  # '21' → 'vingt et un'
        if lang == "fr":
            expanded = expanded.replace("-", " ")
        u = [_sp(t) for t in tokens(expanded, lang)]
        sm = SequenceMatcher(None, u, e, autojunk=False)
        matched = sum(b.size for b in sm.get_matching_blocks())
        # partial credit for near-miss words (recogniser spelling quirks)
        near = 0.0
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "replace":
                for a, b in zip(u[i1:i2], e[j1:j2]):
                    if ratio(a, b) >= 0.8:
                        near += 0.7
        score = (matched + near) / max(1, len(e))
        if score > best_score or not best_heard:
            best_score, best_heard = score, tr
            best_diff = []
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                for j in range(j1, j2):
                    # near-misses earn partial credit but are still flagged, so you know what to work on
                    best_diff.append({"t": e_disp[j], "s": "ok" if op == "equal" else ("missing" if op == "insert" else "wrong")})
    best_score = min(1.0, best_score)
    missed = [d["t"] for d in best_diff if d["s"] != "ok"]
    if best_score >= 0.85:
        grade, cats, note = "correct", [], "Clear!"
    elif best_score >= 0.6:
        grade, cats, note = "almost", ["pronunciation"], f"Almost. Work on: {', '.join(missed[:4])}"
    else:
        grade, cats, note = "wrong", ["pronunciation"], "Let's try that again slowly."
    return Check(grade, target, cats, best_diff, note, round(best_score, 2),
                 detail={"heard": best_heard, "missed": missed})


# ---------------------------------------------------------------- multiple choice
def check_choice(chosen: str, correct_options: list[str], expected_display: str, skill: str) -> Check:
    ok = norm(chosen).lower() in {norm(c).lower() for c in correct_options}
    if ok:
        return Check("correct", expected_display, [], score=1.0)
    cat = {"listening": "listening", "reading": "vocabulary"}.get(skill, "vocabulary")
    return Check("wrong", expected_display, [cat], note=f"You chose “{chosen}”.", score=0.0, detail={"chosen": chosen})
