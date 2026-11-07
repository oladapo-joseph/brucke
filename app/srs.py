"""Spaced repetition (a gentle SM-2 variant).

One card per (item, skill): you can know 'der Hund' when reading it but still
mishear it, so listening, speaking, reading and writing are scheduled separately.
"""
from __future__ import annotations

import time

DAY = 86400.0
QUALITY = {"correct": 5, "almost": 3, "wrong": 1}


def review(con, item_id: str, skill: str, lang: str, grade: str, now: float | None = None) -> dict:
    now = now or time.time()
    row = con.execute("SELECT * FROM cards WHERE item_id=? AND skill=?", (item_id, skill)).fetchone()
    ease, interval, reps, lapses = (row["ease"], row["interval"], row["reps"], row["lapses"]) if row else (2.5, 0.0, 0, 0)
    q = QUALITY[grade]
    if q < 3:
        reps, lapses = 0, lapses + 1
        interval = 0.0
        due = now + 10 * 60          # see it again in ~10 minutes
        ease = max(1.3, ease - 0.2)
    else:
        reps += 1
        if reps == 1:
            interval = 1.0
        elif reps == 2:
            interval = 3.0
        else:
            interval = round(interval * ease, 1)
        if q == 3:
            interval = max(1.0, interval * 0.6)
        ease = max(1.3, ease + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        due = now + interval * DAY
    con.execute(
        "INSERT OR REPLACE INTO cards (item_id, skill, lang, ease, interval, due, reps, lapses, last_seen) "
        "VALUES (?,?,?,?,?,?,?,?,?)", (item_id, skill, lang, ease, interval, due, reps, lapses, now))
    return {"interval_days": interval, "reps": reps, "due": due}


def seed(con, item_id: str, skill: str, lang: str, due_in_days: float = 1.0):
    """Create a card for something just taught, without overwriting history."""
    con.execute("INSERT OR IGNORE INTO cards (item_id, skill, lang, due, last_seen) VALUES (?,?,?,?,?)",
                (item_id, skill, lang, time.time() + due_in_days * DAY, time.time()))


def strength(interval: float, reps: int) -> float:
    """0–1 mastery estimate: ~3 weeks of stable recall ≈ fully known."""
    if reps == 0:
        return 0.05
    return min(1.0, 0.2 + interval / 21.0)
