"""26-week plan: German first, French joins later (staggered), with a concrete plan for every day."""
from __future__ import annotations

from datetime import date, timedelta

from . import challenge
from .content import LANGS, STAGES, course, level_for
from .content.syllabus import STRETCH_STAGES
from .db import db, get_settings
from .exercises import unit_parts

WEEKS = 26
CHECKPOINT_WEEKS = {4, 8, 13, 17, 22, 26}
PHASES = [
    (1, 8, "A1", "Foundations: sounds, the core verbs, gender, everyday phrases"),
    (9, 17, "A2", "Everyday life: past tense, modals, shopping, travel"),
    (18, 26, "B1", "Independence: opinions, subordinate clauses, telling stories"),
]
GUIDED_HOURS_B1 = (350, 400)   # common estimate for A1→B1 with guided study


def _week_of(start: date, d: date) -> int:
    return (d - start).days // 7 + 1


def lang_order(s: dict) -> list[str]:
    first = s.get("first_lang", "de")
    return [first, "fr" if first == "de" else "de"]


def lang_start_week(s: dict, lang: str) -> int:
    return 1 if lang == lang_order(s)[0] else int(s.get("second_lang_start_week", 3))


def expected_stage(s: dict, lang: str, week: int) -> int:
    """Which syllabus stage this language should be on in a given week (0 = not started yet)."""
    sw = lang_start_week(s, lang)
    if week < sw:
        return 0
    avail = WEEKS - sw + 1          # spread all 26 stages evenly over the weeks left
    if avail <= 1:
        return STAGES
    return max(1, min(STAGES, 1 + round((week - sw) * (STAGES - 1) / (avail - 1))))


def minutes_split(s: dict, week: int) -> dict[str, int]:
    total = int(s.get("daily_minutes", 120))
    first, second = lang_order(s)
    if week < lang_start_week(s, second):
        return {first: total, second: 0}
    a = round(total * 0.55 / 5) * 5
    return {first: a, second: total - a}


def unit_status(lang: str, stretch: bool = False) -> dict:
    """Completed parts per unit + the first unit that still has work left (stretch stages only if unlocked)."""
    with db() as con:
        done = {(r["unit_id"], r["part"]) for r in con.execute("SELECT unit_id, part FROM progress WHERE lang=?", (lang,))}
    status, current = {}, None
    for stage in list(range(1, STAGES + 1)) + (list(STRETCH_STAGES) if stretch else []):
        u = course.unit(lang, stage)
        if not u:
            status[stage] = {"parts": 0, "done": 0, "complete": False, "has_content": False}
            if current is None:
                current = stage
            continue
        parts = unit_parts(u)
        n_done = sum((u["id"], p["n"]) in done for p in parts)
        complete = n_done == len(parts)
        status[stage] = {"parts": len(parts), "done": n_done, "complete": complete, "has_content": True,
                         "next_part": next((p["n"] for p in parts if (u["id"], p["n"]) not in done), None)}
        if not complete and current is None:
            current = stage
    return {"units": status, "current_stage": current or max(status)}


def pace(s: dict, lang: str, today: date | None = None) -> dict | None:
    """How fast you're really going, and where that gets you. None = this language hasn't started yet."""
    today = today or date.today()
    lang_start = date.fromisoformat(s["start_date"]) + timedelta(weeks=lang_start_week(s, lang) - 1)
    days = (today - lang_start).days + 1
    if days < 1:
        return None
    st = unit_status(lang)["units"]
    done = sum(1.0 if v["complete"] else (v["done"] / v["parts"] if v["parts"] else 0) for k, v in st.items() if k <= STAGES)
    weeks_avail = WEEKS - lang_start_week(s, lang) + 1
    expected_done = min(STAGES, (days / 7) / weeks_avail * STAGES)
    ahead = round(done - expected_done, 1)
    out = {"stages_done": round(done, 1), "expected_done": round(expected_done, 1), "ahead": ahead,
           "status": "ahead" if ahead >= 1 else "behind" if ahead <= -1 else "on track", "days": days}
    if days >= 7 and done > 0:
        rate = done / (days / 7)                                 # stages per week, as measured
        finish = lang_start_week(s, lang) - 1 + STAGES / rate    # in plan weeks
        out.update(stages_per_week=round(rate, 2), finish_week=round(finish, 1), weeks_early=round(WEEKS - finish, 1))
    return out


def stretch_unlocked(s: dict, lang: str, p: dict | None = None) -> bool:
    """More scope for fast learners: the B2 stretch stages open when you're 2+ stages ahead or nearly done."""
    if s.get("stretch_goal"):
        return True
    p = p if p is not None else pace(s, lang)
    return bool(p and (p["ahead"] >= 2 or p["stages_done"] >= STAGES - 2))


def _day_blocks(lang: str, minutes: int, weekday: int, week: int, cur_stage: int, behind: int, fast: bool = False,
                stretch: bool = False) -> list[dict]:
    if minutes <= 0:
        return []
    name = LANGS[lang]["name"]
    u = course.unit(lang, cur_stage)
    st = unit_status(lang, stretch)["units"].get(cur_stage, {})
    next_part = st.get("next_part")
    lesson_action = ({"type": "lesson", "unit_id": u["id"], "part": next_part} if u and next_part is not None
                     else {"type": "unit", "stage": cur_stage})
    lesson_title = (f"New lesson: {u['title']} · part {next_part + 1}" if u and next_part is not None
                    else f"Unlock stage {cur_stage} (generate it with Claude, or add it yourself)")
    if weekday == 6:  # Sunday: consolidate
        blocks = [{"title": f"Fix my gaps ({name})", "minutes": round(minutes * 0.4), "action": {"type": "gaps"}}]
        if week in CHECKPOINT_WEEKS:
            blocks.append({"title": f"Checkpoint test, week {week}", "minutes": round(minutes * 0.35), "action": {"type": "checkpoint"}})
        else:
            blocks.append({"title": "Free writing, then check your insights", "minutes": round(minutes * 0.35), "action": {"type": "write"}})
        blocks.append({"title": "Easy listening (podcast / show) without subtitles", "minutes": minutes - sum(b["minutes"] for b in blocks),
                       "action": {"type": "offline"}})
        return blocks
    lesson_share = 0.35 + (0.1 if behind > 0 or fast else 0)
    suffix = " (+ catch-up)" if behind > 0 else (" · fast track: aim for 2 parts" if fast else "")
    blocks = [
        {"title": "Warm-up: daily mix (spaced review)", "minutes": max(10, round(minutes * 0.25)), "action": {"type": "mix"}},
        {"title": lesson_title + suffix, "minutes": round(minutes * lesson_share), "action": lesson_action},
    ]
    if weekday in (1, 3, 5):
        blocks.append({"title": "Writing studio", "minutes": round(minutes * 0.15), "action": {"type": "write"}})
        blocks.append({"title": "Speaking drill (shadowing)", "minutes": 0, "action": {"type": "drill", "focus": "speaking"}})
    else:
        blocks.append({"title": "Listening drill", "minutes": 0, "action": {"type": "drill", "focus": "listening"}})
    blocks[-1]["minutes"] = minutes - sum(b["minutes"] for b in blocks)
    return blocks


def today_done(lang: str) -> dict:
    today = date.today().isoformat()
    with db() as con:
        kinds = {r["session_kind"] for r in con.execute("SELECT DISTINCT session_kind FROM attempts WHERE lang=? AND day=?", (lang, today))}
        lessons = con.execute("SELECT COUNT(*) n FROM progress WHERE lang=? AND date(completed_at,'unixepoch','localtime')=?",
                              (lang, today)).fetchone()["n"]
        wrote = con.execute("SELECT COUNT(*) n FROM writings WHERE lang=? AND date(ts,'unixepoch','localtime')=?", (lang, today)).fetchone()["n"]
        secs = con.execute("SELECT seconds FROM activity WHERE lang=? AND day=?", (lang, today)).fetchone()
    return {"kinds": kinds, "lessons": lessons, "wrote": wrote, "minutes": round((secs["seconds"] if secs else 0) / 60)}


def build(today: date | None = None) -> dict:
    s = get_settings()
    today = today or date.today()
    start = date.fromisoformat(s["start_date"])
    week = max(1, _week_of(start, today))
    wk = min(week, WEEKS)
    split = minutes_split(s, wk)
    langs = {}
    for lang in lang_order(s):
        exp = expected_stage(s, lang, wk)
        p = pace(s, lang, today)
        stretch = stretch_unlocked(s, lang, p)
        st = unit_status(lang, stretch)
        behind = max(0, exp - st["current_stage"]) if exp else 0
        cur = st["current_stage"] if exp else 1
        lvl = challenge.level(lang)
        fast = behind == 0 and ((p or {}).get("status") == "ahead" or lvl >= 3)
        blocks = _day_blocks(lang, split[lang], today.weekday(), wk, cur, behind, fast, stretch)
        done = today_done(lang)
        for b in blocks:
            t = b["action"]["type"]
            b["done"] = ((t == "mix" and "mix" in done["kinds"]) or (t == "lesson" and done["lessons"] > 0)
                         or (t == "write" and done["wrote"] > 0) or (t == "gaps" and "gaps" in done["kinds"])
                         or (t == "checkpoint" and "checkpoint" in done["kinds"])
                         or (t == "drill" and f"drill-{b['action'].get('focus')}" in done["kinds"]))
        langs[lang] = {"lang": lang, "name": LANGS[lang]["name"], "minutes": split[lang], "expected_stage": exp,
                       "current_stage": st["current_stage"], "behind": behind, "starts_week": lang_start_week(s, lang),
                       "blocks": blocks, "done_minutes": done["minutes"], "pace": p, "stretch": stretch, "fast_track": fast,
                       "challenge": challenge.summary(lang)}

    # 26-week timeline
    timeline = []
    for w in range(1, WEEKS + 1):
        row = {"week": w, "start": (start + timedelta(weeks=w - 1)).isoformat(), "checkpoint": w in CHECKPOINT_WEEKS}
        for lang in lang_order(s):
            stg = expected_stage(s, lang, w)
            row[lang] = {"stage": stg, "level": level_for(stg) if stg else None,
                         "title": course.outline(lang, stg)["title"] if stg else None}
        timeline.append(row)

    # honest hours projection
    proj = {}
    for lang in lang_order(s):
        mins = sum(minutes_split(s, w)[lang] * 7 for w in range(1, WEEKS + 1))
        proj[lang] = round(mins / 60)
    return {"week": week, "week_capped": wk, "weeks_total": WEEKS, "start_date": s["start_date"],
            "phase": next(p for p in PHASES if p[0] <= wk <= p[1]), "today": today.isoformat(),
            "weekday": today.strftime("%A"), "langs": langs, "order": lang_order(s), "timeline": timeline,
            "projection": {"hours": proj, "b1_guided_hours": GUIDED_HOURS_B1}, "daily_minutes": s["daily_minutes"]}
