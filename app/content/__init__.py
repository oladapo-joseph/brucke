"""Course registry: turns unit definitions into addressable items + a part-of-speech lexicon."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from . import de, fr
from .bridges import BRIDGES
from .syllabus import LEVELS, OUTLINE, level_for

LANGS = {
    "de": {"name": "German", "native": "Deutsch", "tts": "de-DE", "articles": ["der", "die", "das"]},
    "fr": {"name": "French", "native": "Français", "tts": "fr-FR", "articles": ["le", "la"]},
}
STAGES = 26
GENERATED_DIR = Path(__file__).resolve().parents[2] / "data" / "generated"

# ---------------------------------------------------------------- function-word lexicon
# pos codes: noun verb adj pron det prep conj q adv num phrase
_FUNC = {
    "de": {
        "pron": "ich du er sie es wir ihr mich dich mir dir uns euch ihn ihm man",
        "prep": "in im aus auf um am an mit nach von vom zu zum zur bei für ohne bis über unter vor",
        "conj": "und aber oder denn weil dass wenn als ob sondern",
        "q": "wie wo woher wohin was wer wann warum welche welcher wie viel",
        "adv": "nicht auch sehr gern heute morgen oft da dann noch schon hier dort lange gut sonst alles etwas",
        "det": "mein meine meinen meinem dein deine deinen sein seine ihre unser unsere euer",
    },
    "fr": {
        "pron": "je j' tu il elle on nous vous ils elles me m' te t' se s' moi toi lui leur y en ce c' ça",
        "prep": "à au aux de d' du des dans sur sous avec pour sans chez en jusqu'à",
        "conj": "et mais ou que qu' parce si quand",
        "q": "où comment quel quelle combien pourquoi qui quoi qu'est-ce",
        "adv": "ne n' pas très bien aussi souvent aujourd'hui demain ici là tout ensuite",
        "det": "mon ma mes ton ta tes son sa ses notre nos votre vos leur leurs",
    },
}
# article → gender colour (None = take the colour of the following noun)
_ARTICLES = {
    "de": {"der": None, "die": None, "das": "n", "den": "m", "dem": None, "des": None,
           "ein": None, "eine": "f", "einen": "m", "einem": None, "einer": None,
           "kein": None, "keine": None, "keinen": "m"},
    "fr": {"le": "m", "la": "f", "l'": None, "les": "pl", "un": "m", "une": "f", "des": "pl", "du": "m"},
}


def fold(s: str) -> str:
    """Lowercase, strip accents, ß→ss, œ→oe (used for slugs and lenient matching)."""
    s = s.lower().replace("ß", "ss").replace("œ", "oe").replace("æ", "ae").replace("’", "'")
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def meanings(item: dict) -> set[str]:
    """'to begin / to start' → {'begin', 'start'}; 'hour / time (o'clock)' → {'hour', 'time'}."""
    out = set()
    for en in item.get("en_all", []):
        for part in re.sub(r"\(.*?\)", "", en).split("/"):
            m = re.sub(r"^(to|a|an|the)\s+", "", part.strip().lower()).strip()
            if len(m) > 1:
                out.add(m)
    return out


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", fold(s)).strip("-")[:60]


def split_article(lang: str, w: str) -> tuple[str | None, str]:
    """'der Hund' → ('der', 'Hund'); "l'école" → ("l'", 'école'); 'lundi' → (None, 'lundi')."""
    if lang == "fr" and w.lower().startswith("l'"):
        return "l'", w[2:]
    parts = w.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() in ("der", "die", "das", "le", "la", "les"):
        return parts[0].lower(), parts[1]
    return None, w


class Course:
    def __init__(self):
        self.units: dict[str, dict] = {}
        self.items: dict[str, dict] = {}
        self.by_lang: dict[str, list[str]] = {"de": [], "fr": []}
        self.lexicon: dict[str, dict[str, dict]] = {"de": {}, "fr": {}}
        self.reload()

    # ------------------------------------------------------------ loading
    def reload(self):
        self.units.clear(); self.items.clear()
        self.by_lang = {"de": [], "fr": []}
        self.lexicon = {"de": {}, "fr": {}}
        for lang, mod in (("de", de), ("fr", fr)):
            for u in mod.UNITS:
                self._add_unit(lang, dict(u), source="built-in")
        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        for path in sorted(GENERATED_DIR.glob("*.json")):
            try:
                data = json.loads(path.read_text("utf-8"))
                lang = data["lang"]
                uid = f"{lang}-{int(data['stage']):02d}"
                if uid not in self.units:
                    self._add_unit(lang, data, source="claude")
            except Exception as e:  # a broken file shouldn't break the app
                print(f"[course] skipping {path.name}: {e}")
        self._build_lexicon()
        self._build_bridges()

    def _add_unit(self, lang: str, u: dict, source: str):
        stage = int(u["stage"])
        uid = f"{lang}-{stage:02d}"
        u.update(id=uid, lang=lang, level=level_for(stage), source=source)
        for k in ("grammar", "letters", "sounds", "vocab", "sentences"):
            u.setdefault(k, [])
        item_ids = {"letters": [], "sounds": [], "vocab": [], "sentences": [], "reading": []}
        for lt in u["letters"]:
            item_ids["letters"].append(self._add_item(lang, uid, stage, "letter", lt, key=lt["letter"], text=lt["letter"]))
        for s in u["sounds"]:
            item_ids["sounds"].append(self._add_item(lang, uid, stage, "sound", s,
                                                     key=f"{s['pattern']}-{s['ex']}", text=s["ex"]))
        for v in u["vocab"]:
            item_ids["vocab"].append(self._add_item(lang, uid, stage, "vocab", v, key=v["w"], text=v["w"]))
        for s in u["sentences"]:
            item_ids["sentences"].append(self._add_item(lang, uid, stage, "sentence", s, key=s["t"], text=s["t"]))
        if u.get("reading"):
            item_ids["reading"].append(self._add_item(lang, uid, stage, "passage", u["reading"], key=uid, text=u["reading"]["text"]))
        u["item_ids"] = item_ids
        self.units[uid] = u

    def _add_item(self, lang, uid, stage, kind, raw, key, text):
        prefix = {"letter": "ltr", "sound": "snd", "vocab": "v", "sentence": "s", "passage": "read"}[kind]
        # letters: keep case and accents distinct (é ≠ e, ß ≠ ss) in the id
        iid = f"{lang}:{prefix}:{key}" if kind == "letter" else f"{lang}:{prefix}:{slug(key)}"
        if iid in self.items:  # same word taught twice → keep the first one
            return iid
        it = dict(raw)
        it.update(id=iid, lang=lang, unit=uid, stage=stage, kind=kind, text=text)
        it["en_all"] = [it.get("en", "")] + list(it.get("en_alt", []))
        alts = [text] + list(it.get("alt", []))
        if kind == "vocab" and it.get("pos") == "noun":
            art, bare = split_article(lang, it["w"])
            it["article"], it["bare"] = art, bare
        it["accept"] = alts
        if isinstance(it.get("ex"), (list, tuple)) and it["ex"]:
            it["ex"] = list(it["ex"])
        self.items[iid] = it
        self.by_lang[lang].append(iid)
        return iid

    def _build_lexicon(self):
        for lang in ("de", "fr"):
            lx = self.lexicon[lang]
            for pos, words in _FUNC[lang].items():
                for w in words.split():
                    lx[w] = {"pos": pos}
            for art, g in _ARTICLES[lang].items():
                lx[art] = {"pos": "art", "g": g}
            for iid in self.by_lang[lang]:
                it = self.items[iid]
                if it["kind"] != "vocab":
                    continue
                pos = it.get("pos")
                if pos == "noun":
                    lx[it["bare"].lower()] = {"pos": "noun", "g": it.get("g")}
                    if it.get("pl"):
                        _, plb = split_article(lang, it["pl"])
                        lx.setdefault(plb.lower(), {"pos": "noun", "g": "pl"})
                elif pos == "verb":
                    base = it["w"].split()[-1].lower()
                    for f in [base] + it.get("forms", []):
                        lx.setdefault(f.lower(), {"pos": "verb"})
                elif pos in ("adj",) and " " not in it["w"]:
                    lx.setdefault(it["w"].lower(), {"pos": "adj"})

    # ------------------------------------------------------------ queries
    def unit(self, lang: str, stage: int) -> dict | None:
        return self.units.get(f"{lang}-{stage:02d}")

    def outline(self, lang: str, stage: int) -> dict:
        u = self.unit(lang, stage)
        if u:
            return {"id": u["id"], "stage": stage, "level": u["level"], "title": u["title"],
                    "native": u.get("native", ""), "can_do": u.get("can_do", []), "has_content": True,
                    "source": u["source"]}
        title, grammar, can_do, themes = OUTLINE[lang][stage]
        return {"id": f"{lang}-{stage:02d}", "stage": stage, "level": level_for(stage), "title": title, "native": "",
                "grammar_focus": grammar, "can_do": [can_do], "themes": themes, "has_content": False}

    def _build_bridges(self):
        """Attach English bridges, and index meanings so French words can point at German ones (and back)."""
        self.meaning_index = {"de": {}, "fr": {}}
        for lang in ("de", "fr"):
            for iid in self.by_lang[lang]:
                it = self.items[iid]
                if it["kind"] != "vocab":
                    continue
                b = BRIDGES[lang].get(it["text"])
                it["bridge"] = {"kind": b[0], "note": b[1]} if b else None
                for m in meanings(it):
                    self.meaning_index[lang].setdefault(m, []).append(iid)

    def cross_links(self, item: dict) -> list[dict]:
        """Words with the same meaning in the *other* language: la table → der Tisch."""
        if item["kind"] != "vocab":
            return []
        other = "de" if item["lang"] == "fr" else "fr"
        ids = []
        for m in meanings(item):
            ids += [i for i in self.meaning_index[other].get(m, []) if i not in ids]
        return [self.items[i] for i in ids]

    def learned_vocab(self, lang: str, upto_stage: int) -> list[str]:
        return [self.items[i]["text"] for i in self.by_lang[lang]
                if self.items[i]["kind"] == "vocab" and self.items[i]["stage"] <= upto_stage]

    def tag(self, lang: str, text: str) -> list[dict]:
        """Split text into display tokens with part-of-speech + gender for colour coding."""
        lx = self.lexicon[lang]
        raw = re.findall(r"[\w'’\-äöüÄÖÜßàâçéèêëîïôûùüÿœÀÂÇÉÈÊËÎÏÔÛÙŒ]+|[^\s\w]", text)
        toks = []
        for i, t in enumerate(raw):
            if not re.search(r"\w", t):
                toks.append({"t": t, "pos": "punct"}); continue
            low = t.lower().replace("’", "'")
            entry = lx.get(low)
            if entry is None and lang == "fr":
                m = re.match(r"^(l'|d'|j'|n'|m'|t'|s'|c'|qu')(.+)$", low)
                if m:
                    entry = lx.get(m.group(2)) or lx.get(m.group(1))
            if entry is None and lang == "de" and t[:1].isupper() and i > 0:
                entry = {"pos": "noun", "g": None}
            toks.append({"t": t, **(entry or {"pos": "other"})})
        # articles take their noun's colour
        for i, tk in enumerate(toks):
            if tk["pos"] == "art" and tk.get("g") is None:
                for nxt in toks[i + 1:i + 3]:
                    if nxt["pos"] == "noun" and nxt.get("g"):
                        tk["g"] = nxt["g"]; break
        return toks


course = Course()
__all__ = ["course", "Course", "LANGS", "LEVELS", "STAGES", "fold", "slug", "split_article", "level_for", "GENERATED_DIR"]
