"""Adaptive difficulty: keep the learner in the 'sweet spot' (about 85% correct).

Research (Wilson et al., 2019, "The Eighty Five Percent Rule for optimal learning") suggests learning is fastest
when you get roughly 85% right. Near 100% means the material is too easy (complacency); below ~70% means it's too
hard (frustration). After every answer we look at the recent window of answers and nudge the challenge level.

Levels change *how* you're tested, never what you're taught:
  1 Gentle   – more multiple choice, longer recognition phase
  2 Steady   – the default balance
  3 Stretch  – production (typing / speaking from memory) from the first review, confusable options, decoy tiles
  4 Hard     – production even inside new lessons, accent slips count as mistakes, 2 decoy tiles
  5 Expert   – no slow-motion audio, longer sessions
"""
from __future__ import annotations

import json
import time

from .db import db, get_settings

LEVELS = {
    1: {"name": "Gentle", "desc": "More multiple choice while things settle."},
    2: {"name": "Steady", "desc": "The default balance of recognising and producing."},
    3: {"name": "Stretch", "desc": "Type and speak from memory sooner, trickier options, decoy tiles."},
    4: {"name": "Hard", "desc": "Production inside new lessons too, and accent slips count as mistakes."},
    5: {"name": "Expert", "desc": "No slow-motion replays, longer sessions, maximum production."},
}
DEFAULT_LEVEL = 2
WINDOW = 40          # answers considered
MIN_BETWEEN = 25     # answers needed after a change before the next one (prevents ping-pong)
UP_AT = 0.93         # coasting → harder
DOWN_AT = 0.70       # struggling → easier
TARGET = 0.85

# what each level does (used by exercises.py and main.py)
PRODUCTION_AFTER_REPS = {1: 3, 2: 2, 3: 1, 4: 0, 5: 0}   # reviews in recognition mode before production
DECOY_TILES = {1: 0, 2: 0, 3: 1, 4: 2, 5: 2}
SESSION_SIZE = {1: 12, 2: 15, 3: 18, 4: 20, 5: 24}
STRICT_ACCENTS = {1: False, 2: False, 3: False, 4: True, 5: True}
SLOW_AUDIO = {1: True, 2: True, 3: True, 4: True, 5: False}
CONFUSABLE_OPTIONS = {1: False, 2: False, 3: True, 4: True, 5: True}
LESSON_PRODUCTION = {1: False, 2: False, 3: False, 4: True, 5: True}


def _key(lang: str) -> str:
    return f"challenge_{lang}"


def _state(con, lang: str) -> dict:
    row = con.execute("SELECT value FROM settings WHERE key=?", (_key(lang),)).fetchone()
    st = json.loads(row["value"]) if row else {}
    st.setdefault("level", DEFAULT_LEVEL)
    st.setdefault("changed_at_n", 0)
    st.setdefault("history", [])
    return st


def level(lang: str) -> int:
    """The level in force: a manual setting wins over the automatic one."""
    mode = str(get_settings().get("challenge_mode", "auto"))
    if mode.isdigit() and int(mode) in LEVELS:
        return int(mode)
    with db() as con:
        return _state(con, lang)["level"]


def recent_accuracy(con, lang: str, n: int = WINDOW) -> tuple[float | None, int]:
    rows = con.execute(
        "SELECT grade FROM attempts WHERE lang=? AND ex_type!='free_writing' AND session_kind!='testout' "
        "ORDER BY ts DESC LIMIT ?", (lang, n)).fetchall()
    if not rows:
        return None, 0
    score = sum({"correct": 1.0, "almost": 0.5}.get(r["grade"], 0.0) for r in rows) / len(rows)
    return score, len(rows)


def update(con, lang: str) -> dict | None:
    """Call after each logged answer. Returns {'from', 'to', 'reason'} when the level changes."""
    if str(get_settings().get("challenge_mode", "auto")) != "auto":
        return None
    st = _state(con, lang)
    total = con.execute("SELECT COUNT(*) n FROM attempts WHERE lang=? AND ex_type!='free_writing'", (lang,)).fetchone()["n"]
    if total - st["changed_at_n"] < MIN_BETWEEN:
        return None
    acc, n = recent_accuracy(con, lang)
    if acc is None or n < MIN_BETWEEN:
        return None
    new = st["level"]
    if acc >= UP_AT and st["level"] < 5:
        new, reason = st["level"] + 1, f"{round(acc * 100)}% on your last {n} answers: you're coasting, so it gets tougher."
    elif acc <= DOWN_AT and st["level"] > 1:
        new, reason = st["level"] - 1, f"{round(acc * 100)}% on your last {n} answers: easing off a little so it sticks."
    if new == st["level"]:
        return None
    change = {"from": st["level"], "to": new, "reason": reason, "name": LEVELS[new]["name"], "desc": LEVELS[new]["desc"],
              "ts": time.time()}
    st.update(level=new, changed_at_n=total)
    st["history"] = (st["history"] + [change])[-30:]
    con.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (_key(lang), json.dumps(st)))
    return change


def summary(lang: str) -> dict:
    with db() as con:
        st = _state(con, lang)
        acc, n = recent_accuracy(con, lang)
    lv = level(lang)
    zone = None if acc is None else ("coasting" if acc >= UP_AT else "struggling" if acc <= DOWN_AT else "sweet spot")
    return {"level": lv, "name": LEVELS[lv]["name"], "desc": LEVELS[lv]["desc"], "auto": str(get_settings().get("challenge_mode", "auto")) == "auto",
            "recent_accuracy": acc, "window": n, "zone": zone, "target": TARGET, "history": st["history"][-8:],
            "levels": LEVELS}
