"""Learner analytics: where you're strong, where you keep slipping, and what to do next."""
from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from datetime import date, timedelta

from . import challenge
from .content import LANGS, course
from .db import db
from .evaluate import CATEGORIES, TIPS
from .exercises import SKILLS, category_counts, skill_accuracy, weak_items
from .srs import strength

DAY = 86400


def streak() -> int:
    with db() as con:
        days = {r["day"] for r in con.execute("SELECT DISTINCT day FROM attempts")}
    d, n = date.today(), 0
    if d.isoformat() not in days:
        d -= timedelta(days=1)
    while d.isoformat() in days:
        n += 1
        d -= timedelta(days=1)
    return n


def today_stats(lang: str) -> dict:
    today = date.today().isoformat()
    with db() as con:
        r = con.execute("SELECT COUNT(*) n, SUM(correct) c, SUM(xp) xp FROM attempts WHERE lang=? AND day=?", (lang, today)).fetchone()
        a = con.execute("SELECT seconds FROM activity WHERE lang=? AND day=?", (lang, today)).fetchone()
        due = con.execute("SELECT COUNT(*) n FROM cards WHERE lang=? AND due<=?", (lang, time.time())).fetchone()["n"]
    return {"answers": r["n"], "correct": r["c"] or 0, "xp": r["xp"] or 0,
            "minutes": round((a["seconds"] if a else 0) / 60), "due": due}


def build(lang: str) -> dict:
    now = time.time()
    with db() as con:
        acc = skill_accuracy(con, lang, 14)
        acc_prev = {}
        for s in SKILLS:
            r = con.execute("SELECT COUNT(*) n, SUM(correct) c FROM attempts WHERE lang=? AND skill=? AND ts BETWEEN ? AND ?",
                            (lang, s, now - 28 * DAY, now - 14 * DAY)).fetchone()
            acc_prev[s] = (r["c"] or 0) / r["n"] if r["n"] else None
        cards = [dict(r) for r in con.execute("SELECT * FROM cards WHERE lang=?", (lang,))]
        counts_now = category_counts(con, lang, 14)
        counts_all = category_counts(con, lang, 28)
        weak = weak_items(con, lang, 21, 12)
        # most common category per weak item + what you actually wrote
        per_item: dict[str, Counter] = defaultdict(Counter)
        last_given: dict[str, str] = {}
        for r in con.execute("SELECT item_id, categories, given FROM attempts WHERE lang=? AND correct=0 AND ts>? ORDER BY ts",
                             (lang, now - 21 * DAY)):
            for c in json.loads(r["categories"]):
                per_item[r["item_id"]][c] += 1
            last_given[r["item_id"]] = r["given"]
        gender_rows = con.execute("SELECT item_id, given, expected FROM attempts WHERE lang=? AND categories LIKE '%gender%' "
                                  "AND ts>? ORDER BY ts DESC LIMIT 40", (lang, now - 28 * DAY)).fetchall()
        timeline = []
        for i in range(13, -1, -1):
            d = (date.today() - timedelta(days=i)).isoformat()
            r = con.execute("SELECT COUNT(*) n, SUM(correct) c FROM attempts WHERE lang=? AND day=?", (lang, d)).fetchone()
            a = con.execute("SELECT seconds FROM activity WHERE lang=? AND day=?", (lang, d)).fetchone()
            timeline.append({"day": d, "answers": r["n"], "accuracy": (r["c"] or 0) / r["n"] if r["n"] else None,
                             "minutes": round((a["seconds"] if a else 0) / 60)})
        checkpoints = [dict(r) | {"scores": json.loads(r["scores"])} for r in
                       con.execute("SELECT * FROM checkpoints WHERE lang=? ORDER BY ts DESC LIMIT 6", (lang,))]
        total_attempts = con.execute("SELECT COUNT(*) n FROM attempts WHERE lang=?", (lang,)).fetchone()["n"]

    cards = [c for c in cards if c["item_id"] in course.items]
    mastery = {}
    for s in SKILLS:
        cs = [c for c in cards if c["skill"] == s]
        mastery[s] = round(sum(strength(c["interval"], c["reps"]) for c in cs) / len(cs), 3) if cs else 0.0

    items_known = defaultdict(list)
    for c in cards:
        items_known[c["item_id"]].append(strength(c["interval"], c["reps"]))
    solid = sum(1 for v in items_known.values() if min(v) >= 0.6)

    cats = []
    for cat, n in counts_now.most_common():
        prev = counts_all[cat] - n
        cats.append({"id": cat, "label": CATEGORIES[cat]["label"], "count": n, "prev": prev,
                     "trend": "up" if n > prev else ("down" if n < prev else "flat"), "tip": TIPS[lang].get(cat, "")})

    gaps = []
    for w in weak:
        it = course.items[w["item_id"]]
        top = per_item[w["item_id"]].most_common(1)
        gaps.append({"item_id": it["id"], "text": it["text"] if it["kind"] != "passage" else it["title"],
                     "en": it.get("en", "") if it["kind"] != "passage" else "reading passage",
                     "misses": w["misses"], "category": top[0][0] if top else None,
                     "category_label": CATEGORIES[top[0][0]]["label"] if top else "", "g": it.get("g"),
                     "last_given": last_given.get(w["item_id"], ""), "kind": it["kind"]})

    confusions = Counter()
    for r in gender_rows:
        it = course.items.get(r["item_id"])
        if it and it.get("bare"):
            confusions[(it["bare"], it.get("article") or "", it.get("g"))] += 1
    confusions_out = [{"word": w, "article": a, "g": g, "times": n} for (w, a, g), n in confusions.most_common(8)]

    recs = _recommendations(lang, acc, mastery, cats, gaps, total_attempts)
    return {"lang": lang, "name": LANGS[lang]["name"], "skills": [
        {"skill": s, "accuracy": acc[s], "prev": acc_prev[s], "mastery": mastery[s],
         "cards": sum(1 for c in cards if c["skill"] == s)} for s in SKILLS],
        "categories": cats, "gaps": gaps, "confusions": confusions_out, "timeline": timeline,
        "checkpoints": checkpoints, "items_learned": len(items_known), "items_solid": solid,
        "recommendations": recs, "total_attempts": total_attempts, "streak": streak(), "challenge": challenge.summary(lang)}


def _recommendations(lang, acc, mastery, cats, gaps, total) -> list[dict]:
    recs = []
    if total < 15:
        return [{"title": "Keep going: patterns appear after ~15 answers",
                 "body": "Finish a few lesson parts and a daily mix. The app is already logging every slip.",
                 "action": {"type": "mix"}}]
    scored = {s: a for s, a in acc.items() if a is not None}
    if scored:
        weakest = min(scored, key=scored.get)
        if scored[weakest] < 0.85:
            recs.append({"title": f"Your weakest skill right now: {weakest}",
                         "body": f"{round(scored[weakest] * 100)}% accuracy over the last two weeks. A focused {weakest} drill gives it extra reps.",
                         "action": {"type": "drill", "focus": weakest}})
    if cats:
        top = cats[0]
        recs.append({"title": f"Recurring pattern: {top['label'].lower()} ({top['count']}×)",
                     "body": top["tip"], "action": {"type": "drill", "focus": top["id"]}})
    if len(gaps) >= 3:
        recs.append({"title": f"{len(gaps)} items keep slipping",
                     "body": "A 'Fix my gaps' session brings back only the things you've missed recently, across all four skills.",
                     "action": {"type": "gaps"}})
    unpracticed = [s for s, m in mastery.items() if m < 0.1]
    if "speaking" in unpracticed:
        recs.append({"title": "Your voice needs reps too", "body": "Speaking is the skill most people skip. Two minutes of shadowing a day pays off.",
                     "action": {"type": "drill", "focus": "speaking"}})
    return recs[:4]
