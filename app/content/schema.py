"""Tiny helpers so course content stays compact and readable.

Every learnable thing is an *item*. Items come in four kinds:
  vocab     – a word or short phrase (nouns carry gender + plural)
  sentence  – a full sentence with accepted alternatives
  sound     – a pronunciation pattern with an example word
  passage   – a short reading text with comprehension questions
"""
from __future__ import annotations


def N(w: str, en: str, g: str, pl: str | None = None, ex: tuple[str, str] | None = None, en_alt=()):
    """Noun. `w` includes the article, e.g. 'der Hund' / 'le chien'. g in m/f/n/pl."""
    return {"kind": "vocab", "pos": "noun", "w": w, "en": en, "g": g, "pl": pl, "ex": ex, "en_alt": list(en_alt)}


def V(w: str, en: str, forms=(), ex: tuple[str, str] | None = None, en_alt=()):
    """Verb. `forms` lists conjugated forms so the app can recognise and colour them."""
    return {"kind": "vocab", "pos": "verb", "w": w, "en": en, "forms": list(forms), "ex": ex, "en_alt": list(en_alt)}


def A(w: str, en: str, ex: tuple[str, str] | None = None, en_alt=()):
    """Adjective / adverb."""
    return {"kind": "vocab", "pos": "adj", "w": w, "en": en, "ex": ex, "en_alt": list(en_alt)}


def W(w: str, en: str, pos: str = "phrase", ex: tuple[str, str] | None = None, en_alt=(), alt=()):
    """Any other word or fixed phrase (pron, num, q, phrase...)."""
    return {"kind": "vocab", "pos": pos, "w": w, "en": en, "ex": ex, "en_alt": list(en_alt), "alt": list(alt)}


def S(t: str, en: str, alt=(), en_alt=()):
    """Sentence. `alt` = other correct target-language answers, `en_alt` = other English meanings."""
    return {"kind": "sentence", "t": t, "en": en, "alt": list(alt), "en_alt": list(en_alt)}


def SND(pattern: str, ex: str, en: str, tip: str):
    """Sound pattern: the letters, an example word, its meaning, and how to say it."""
    return {"kind": "sound", "pattern": pattern, "ex": ex, "en": en, "tip": tip}


def L(letter: str, name: str, like: str, ex: str, en: str, confuse: str = "", tip: str = "", say: str | None = None):
    """Alphabet letter.
    name    – how the letter is called in the language (German 'Jott', French 'gé')
    like    – how that name sounds to an English speaker ('yot', 'zhay')
    ex / en – an example word and its meaning (used for speaking + spelling drills)
    confuse – letters an English speaker typically mixes it up with (used as quiz options)
    say     – what the voice engine should read for the letter name (defaults to the letter itself)
    """
    return {"kind": "letter", "letter": letter, "name": name, "like": like, "word": ex, "word_en": en,
            "en": f"the letter {letter} ({name})", "confuse": list(confuse), "tip": tip,
            "say": say or letter, "tricky": bool(tip)}


def G(title: str, body: str, table=None, at: str | None = None):
    """Grammar note. Body uses **bold**, *italic* and line breaks. Table = list of rows (first row = header).
    at = which lesson part shows it: 'letters', 'letters:last', 'sounds', 'words', 'sentences' (default: in order)."""
    return {"title": title, "body": body, "table": table, "at": at}


def Q(q: str, options: list[str], a: int):
    return {"q": q, "options": options, "a": a}


def P(title: str, text: str, en: str, questions: list):
    return {"kind": "passage", "title": title, "text": text, "en": en, "questions": questions}
