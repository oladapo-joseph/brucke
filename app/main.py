"""Brücke: a personal German + French trainer. Run: uvicorn app.main:app --reload"""
from __future__ import annotations

import json
import re
import time
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import ai, challenge, db, insights, schedule, srs
from .content import LANGS, LEVELS, STAGES, course
from .evaluate import CATEGORIES, TIPS, check_choice, check_speech, check_text
from .exercises import (KIND_SKILLS, TESTOUT_PASS, build_checkpoint, build_session, display, known_ids, lesson_steps,
                        spelled, testout_steps, unit_parts)

STATIC = Path(__file__).resolve().parents[1] / "static"
XP = {"correct": 10, "almost": 6, "wrong": 2}

app = FastAPI(title="Brücke", version="1.1")
db.init()


def _migrate_progress():
    """Content v2 added alphabet parts to the front of stage 1 and more number parts to stage 4.
    Progress is stored by part index, so shift finished parts to where they now live."""
    with db.db() as con:
        row = con.execute("SELECT value FROM settings WHERE key='content_version'").fetchone()
        if row and json.loads(row["value"]) >= 2:
            return
        for lang in LANGS:
            u1, u4 = course.unit(lang, 1), course.unit(lang, 4)
            shifts = []
            if u1:
                shifts.append((u1["id"], 0, sum(p["kind"] == "letters" for p in unit_parts(u1))))
            if u4:  # stage 4 used to have 3 "Words" parts
                shifts.append((u4["id"], 3, sum(p["kind"] == "words" for p in unit_parts(u4)) - 3))
            for uid, from_part, by in shifts:
                if by > 0:
                    con.execute("UPDATE progress SET part = part + 1000 WHERE unit_id=? AND part>=?", (uid, from_part))
                    con.execute("UPDATE progress SET part = part - 1000 + ? WHERE unit_id=? AND part>=1000", (by, uid))
        con.execute("INSERT OR REPLACE INTO settings VALUES ('content_version', '2')")


_migrate_progress()


def _lang(lang: str) -> str:
    if lang not in LANGS:
        raise HTTPException(404, "Unknown language")
    return lang


# ---------------------------------------------------------------- state & settings
@app.get("/api/state")
def state():
    s = db.get_settings()
    return {"settings": s, "ai": ai.available(), "langs": LANGS, "levels": LEVELS, "stages": STAGES,
            "categories": CATEGORIES, "streak": insights.streak(),
            "today": {l: insights.today_stats(l) for l in LANGS}}


class SettingsIn(BaseModel):
    values: dict[str, Any]


@app.put("/api/settings")
def put_settings(body: SettingsIn):
    v = dict(body.values)
    if "start_date" in v:
        try:
            date.fromisoformat(v["start_date"])
        except (TypeError, ValueError):
            raise HTTPException(400, "start_date must be YYYY-MM-DD")
    if "daily_minutes" in v:
        v["daily_minutes"] = max(15, min(480, int(v["daily_minutes"])))
    if "challenge_mode" in v and str(v["challenge_mode"]) not in ("auto", "1", "2", "3", "4", "5"):
        raise HTTPException(400, "challenge_mode must be auto or 1–5")
    if "stretch_goal" in v:
        v["stretch_goal"] = bool(v["stretch_goal"])
    if "second_lang_start_week" in v:
        v["second_lang_start_week"] = max(1, min(20, int(v["second_lang_start_week"])))
    db.set_settings(v)
    return db.get_settings()


# ---------------------------------------------------------------- course
@app.get("/api/units")
def units(lang: str):
    _lang(lang)
    s = db.get_settings()
    sched = schedule.build()
    stretch = schedule.stretch_unlocked(s, lang)
    st = schedule.unit_status(lang, stretch)
    out = []
    for stage in st["units"]:
        o = course.outline(lang, stage)
        o.update(st["units"][stage])
        out.append(o)
    return {"units": out, "current_stage": st["current_stage"], "stretch": stretch, "pace": schedule.pace(s, lang),
            "expected_stage": schedule.expected_stage(s, lang, sched["week_capped"]), "week": sched["week"]}


@app.get("/api/units/{uid}")
def unit(uid: str):
    u = course.units.get(uid)
    if not u:
        lang, stage = uid.split("-")
        return {"outline": course.outline(_lang(lang), int(stage)), "has_content": False, "ai": ai.available()}
    with db.db() as con:
        done = {r["part"] for r in con.execute("SELECT part FROM progress WHERE unit_id=?", (uid,))}
    parts = [{"n": p["n"], "title": p["title"], "kind": p["kind"], "count": len(p["items"]), "done": p["n"] in done}
             for p in unit_parts(u)]
    ids = u["item_ids"]
    known = known_ids()
    vocab = [course.items[i] for i in ids["vocab"]]
    recognisable = sum(1 for it in vocab if (it.get("bridge") or {}).get("kind") in ("same", "hook", "lit"))
    return {"has_content": True, "recognisable": recognisable, "vocab_total": len(vocab), "id": uid, "lang": u["lang"], "stage": u["stage"], "level": u["level"], "title": u["title"],
            "native": u.get("native", ""), "can_do": u.get("can_do", []), "grammar": u.get("grammar", []),
            "parts": parts, "source": u["source"],
            "letters": [display(course.items[i]) for i in ids.get("letters", [])],
            "sounds": [display(course.items[i]) for i in ids["sounds"]],
            "vocab": [display(course.items[i], known) for i in ids["vocab"]],
            "sentences": [display(course.items[i]) for i in ids["sentences"]],
            "writing_prompt": u.get("writing_prompt"), "writing_model": u.get("writing_model")}


@app.get("/api/lesson/{uid}/{part}")
def lesson(uid: str, part: int, mode: str = "learn"):
    u = course.units.get(uid)
    if not u:
        raise HTTPException(404, "Unit has no content yet")
    parts = unit_parts(u)
    if not 0 <= part < len(parts):
        raise HTTPException(404, "No such part")
    return {"unit_id": uid, "lang": u["lang"], "title": u["title"], "part": parts[part]["title"], "n": part,
            "total_parts": len(parts), "mode": mode,
            "level": challenge.level(u["lang"]),
            "steps": testout_steps(u, part) if mode == "testout" else lesson_steps(u, part, known_ids(), challenge.level(u["lang"]))}


class TestoutIn(BaseModel):
    unit_id: str
    part: int
    session_id: str


@app.post("/api/testout/finish")
def testout_finish(body: TestoutIn):
    """Score a test-out. Pass → the part counts as done and its cards start further out (you already know it)."""
    u = course.units.get(body.unit_id)
    if not u:
        raise HTTPException(404, "Unknown unit")
    part = unit_parts(u)[body.part]
    with db.db() as con:
        rows = con.execute("SELECT item_id, correct FROM attempts WHERE session_id=? AND session_kind='testout'",
                           (body.session_id,)).fetchall()
        n = len(rows)
        score = sum(r["correct"] for r in rows) / n if n else 0.0
        passed = n > 0 and n >= len(part["items"]) * 0.8 and score >= TESTOUT_PASS
        missed = sorted({r["item_id"] for r in rows if not r["correct"]})
        if passed:
            con.execute("INSERT OR REPLACE INTO progress VALUES (?,?,?,?)", (u["id"], body.part, u["lang"], time.time()))
            for iid in part["items"]:
                for skill in KIND_SKILLS[course.items[iid]["kind"]]:
                    srs.seed(con, iid, skill, u["lang"], due_in_days=3)
    return {"testout": True, "passed": passed, "score": round(score, 2), "answered": n,
            "missed": [course.items[i]["text"] for i in missed if i in course.items],
            "unit_id": u["id"], "part": body.part, "title": part["title"]}


class ProgressIn(BaseModel):
    unit_id: str
    part: int


@app.post("/api/progress")
def progress(body: ProgressIn):
    u = course.units.get(body.unit_id)
    if not u:
        raise HTTPException(404, "Unknown unit")
    part = unit_parts(u)[body.part]
    with db.db() as con:
        con.execute("INSERT OR REPLACE INTO progress VALUES (?,?,?,?)", (u["id"], body.part, u["lang"], time.time()))
        for iid in part["items"]:
            for skill in KIND_SKILLS[course.items[iid]["kind"]]:
                srs.seed(con, iid, skill, u["lang"], due_in_days=1)
    return {"ok": True, "status": schedule.unit_status(u["lang"])["units"][u["stage"]]}


@app.post("/api/units/{lang}/{stage}/generate")
def generate(lang: str, stage: int):
    _lang(lang)
    try:
        u = ai.generate_unit(lang, stage)
    except ai.AIError as e:
        raise HTTPException(400, str(e))
    return {"ok": True, "id": u["id"], "title": u["title"]}


@app.get("/api/item/{item_id:path}")
def item(item_id: str):
    it = course.items.get(item_id)
    if not it:
        raise HTTPException(404, "Unknown item")
    return display(it, known_ids())


# ---------------------------------------------------------------- practice
@app.get("/api/session")
def session(lang: str, size: int | None = None, focus: str | None = None):
    return build_session(_lang(lang), max(5, min(40, size)) if size else None, focus or None)


@app.get("/api/checkpoint")
def checkpoint(lang: str):
    return build_checkpoint(_lang(lang))


class CheckpointDone(BaseModel):
    lang: str
    session_id: str


@app.post("/api/checkpoint/finish")
def checkpoint_finish(body: CheckpointDone):
    with db.db() as con:
        rows = con.execute("SELECT skill, COUNT(*) n, SUM(correct) c FROM attempts WHERE session_id=? GROUP BY skill",
                           (body.session_id,)).fetchall()
        scores = {r["skill"]: round((r["c"] or 0) / r["n"], 2) for r in rows}
        stage = schedule.unit_status(body.lang)["current_stage"]
        con.execute("INSERT INTO checkpoints (ts, lang, stage, scores) VALUES (?,?,?,?)",
                    (time.time(), body.lang, stage, json.dumps(scores)))
    return {"scores": scores, "stage": stage}


class AnswerIn(BaseModel):
    lang: str
    item_id: str
    skill: str
    type: str
    answer: str | list[str] = ""
    transcripts: list[str] = Field(default_factory=list)
    session_kind: str = "mix"
    session_id: str = ""
    seconds: float = 0


def _gender_article(it: dict) -> str:
    if it["lang"] == "de":
        return {"m": "der", "f": "die", "n": "das"}[it["g"]]
    return {"m": "le", "f": "la"}[it["g"]]


@app.post("/api/answer")
def answer(a: AnswerIn):
    it = course.items.get(a.item_id)
    if not it:
        raise HTTPException(404, "Unknown item")
    lang, t = it["lang"], a.type
    ans = a.answer if isinstance(a.answer, str) else ""
    extra: dict[str, Any] = {}
    if t in ("listen_choose", "read_choose"):
        res = check_choice(ans, it["en_all"], it["en"], a.skill)
        extra["text"] = it["text"]
    elif t == "letter_listen":
        res = check_choice(ans, [it["letter"]], it["letter"], "listening")
        if not res.correct:
            res.categories = ["letters"]
            res.note = f"You heard {it['letter']}, called '{it['name']}' (sounds like '{it['like']}')."
        extra.update(tip=it.get("tip"), name=it["name"], like=it["like"], say=it["say"])
    elif t == "spell":
        res = check_text(ans, [it["word"]], lang)
        if res.grade == "wrong":
            res.categories = ["letters"] + [c for c in res.categories if c not in ("vocabulary", "letters")]
        extra.update(spelled=spelled(it["word"], lang, "name"), en=it["word_en"])
    elif t == "listen_spell":
        res = check_choice(ans, [it["text"]], it["text"], "listening")
        extra["tip"] = it.get("tip")
    elif t == "gender":
        exp = _gender_article(it)
        ok = ans.strip().lower() == exp
        res = check_choice(ans, [exp], f"{exp} {it['bare']}" if it.get("article") != "l'" else f"{it['text']} ({exp})", "writing")
        if not ok:
            res.categories = ["gender"]
            res.note = f"It's {exp} {it['bare']}."
        extra["g"] = it["g"]
        ans = f"{ans} {it['bare']}"
    elif t in ("dictation", "translate", "build"):
        if t == "build" and isinstance(a.answer, list):
            ans = " ".join(a.answer)
        res = check_text(ans, it["accept"], lang)
        if t == "dictation" and res.grade == "wrong" and "listening" not in res.categories:
            res.categories.append("listening")
    elif t in ("speak", "speak_translate"):
        heard = [x for x in (a.transcripts or [ans]) if x is not None]
        best = None
        for target in ([it["word"]] if it["kind"] == "letter" else it["accept"]):
            r = check_speech(heard, target, lang)
            if best is None or r.score > best.score:
                best = r
        res = best
        ans = res.detail.get("heard", "")
    elif t == "reading_passage":
        chosen = a.answer if isinstance(a.answer, list) else []
        right = [q["options"][q["a"]] for q in it["questions"]]
        per = [i < len(chosen) and chosen[i] == r for i, r in enumerate(right)]
        frac = sum(per) / len(per)
        res = check_choice("", [""], "", "reading")
        res.grade = "correct" if frac == 1 else ("almost" if frac >= 0.66 else "wrong")
        res.categories = [] if frac == 1 else ["comprehension"]
        res.score, res.expected = frac, " · ".join(right)
        res.note = f"{sum(per)} of {len(per)} correct"
        extra.update(per_question=per, right=right, translation=it.get("en"))
        ans = json.dumps(chosen, ensure_ascii=False)
    else:
        raise HTTPException(400, f"Unknown exercise type {t}")

    lvl = challenge.level(lang)
    if challenge.STRICT_ACCENTS[lvl] and res.grade == "almost" and set(res.categories) & {"accents", "capitalization"}:
        res.grade = "wrong"
        res.note = (res.note + " · " if res.note else "") + f"At level {lvl} ({challenge.LEVELS[lvl]['name']}), accent and capital slips count."
    xp = XP[res.grade] + (2 * (lvl - 2) if res.grade == "correct" and lvl > 2 else 0)  # tougher = more XP
    now = time.time()
    with db.db() as con:
        con.execute(
            "INSERT INTO attempts (ts, day, lang, item_id, skill, ex_type, grade, correct, categories, given, expected, detail, "
            "session_kind, session_id, seconds, xp) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (now, date.today().isoformat(), lang, it["id"], a.skill, t, res.grade, int(res.correct),
             json.dumps(res.categories), ans[:500], res.expected[:500], json.dumps(res.detail, ensure_ascii=False),
             a.session_kind, a.session_id, min(a.seconds, 120), xp))
        sched = srs.review(con, it["id"], a.skill, lang, res.grade, now)
        level_change = challenge.update(con, lang) if a.session_kind != "testout" else None
    return {"grade": res.grade, "correct": res.correct, "expected": res.expected, "note": res.note, "diff": res.diff,
            "score": res.score, "xp": xp, "detail": res.detail, "level_change": level_change, "en": it.get("en"), "next_review_days": sched["interval_days"],
            "categories": [{"id": c, "label": CATEGORIES[c]["label"], "tip": TIPS[lang].get(c, "")} for c in res.categories],
            **extra}


class ActivityIn(BaseModel):
    lang: str
    seconds: float


@app.post("/api/activity")
def activity(body: ActivityIn):
    _lang(body.lang)
    secs = max(0.0, min(body.seconds, 90.0))
    with db.db() as con:
        con.execute("INSERT INTO activity (day, lang, seconds) VALUES (?,?,?) "
                    "ON CONFLICT(day, lang) DO UPDATE SET seconds = seconds + excluded.seconds",
                    (date.today().isoformat(), body.lang, secs))
    return {"ok": True}


# ---------------------------------------------------------------- writing
class WritingIn(BaseModel):
    lang: str
    text: str
    prompt: str = ""
    unit_id: str | None = None


@app.post("/api/writing")
def writing(body: WritingIn):
    lang = _lang(body.lang)
    text = body.text.strip()
    if len(text) < 3:
        raise HTTPException(400, "Write a little more first.")
    u = course.units.get(body.unit_id or "")
    stage = u["stage"] if u else schedule.unit_status(lang)["current_stage"]
    prompt = body.prompt or (u.get("writing_prompt") if u else "") or "Free writing"
    if ai.available():
        try:
            fb = ai.grade_writing(lang, stage, prompt, text)
        except ai.AIError as e:
            fb = _offline_feedback(lang, text, u) | {"ai_error": str(e)}
    else:
        fb = _offline_feedback(lang, text, u)
    now = time.time()
    with db.db() as con:
        cur = con.execute("INSERT INTO writings (ts, lang, unit_id, prompt, text, feedback) VALUES (?,?,?,?,?,?)",
                          (now, lang, body.unit_id, prompt, text, json.dumps(fb, ensure_ascii=False)))
        wid = cur.lastrowid
        # every tagged error feeds the same insight engine as drills
        for err in fb.get("errors", []):
            if err.get("category") in CATEGORIES:
                con.execute("INSERT INTO attempts (ts, day, lang, item_id, skill, ex_type, grade, correct, categories, given, "
                            "expected, detail, session_kind, session_id, xp) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (now, date.today().isoformat(), lang, f"{lang}:write:{wid}", "writing", "free_writing", "wrong", 0,
                             json.dumps([err["category"]]), err.get("original", ""), err.get("correction", ""), "{}",
                             "write", str(wid), 0))
        con.execute("INSERT INTO attempts (ts, day, lang, item_id, skill, ex_type, grade, correct, categories, given, expected, "
                    "detail, session_kind, session_id, xp) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (now, date.today().isoformat(), lang, f"{lang}:write:{wid}", "writing", "free_writing",
                     "correct" if not fb.get("errors") else "almost", 1, "[]", text[:500], "", "{}", "write", str(wid), 15))
    return {"id": wid, **fb}


def _offline_feedback(lang: str, text: str, u: dict | None) -> dict:
    """Without Claude: a few rule-based checks plus the model answer for self-comparison."""
    checks = []
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    checks.append({"ok": len(sentences) >= 3, "text": f"{len(sentences)} sentence(s). Aim for at least 3."})
    if lang == "de":
        lex = course.lexicon["de"]
        lower_nouns = sorted({w for w in re.findall(r"\b[a-zäöüß]+\b", text)
                              if lex.get(w, {}).get("pos") == "noun"})
        checks.append({"ok": not lower_nouns, "text": "Nouns capitalised" if not lower_nouns
                       else "Capitalise these nouns: " + ", ".join(w.capitalize() for w in lower_nouns)})
    if lang == "fr":
        missing = [w for w in ("etre", "tres", "ecole", "francais", "ca") if re.search(rf"\b{w}\b", text.lower())]
        checks.append({"ok": not missing, "text": "Accents look fine" if not missing else "Check accents on: " + ", ".join(missing)})
    return {"source": "offline", "checks": checks, "model": (u or {}).get("writing_model", ""), "errors": [],
            "summary": "Compare your text with the model answer and read both aloud. Add an Anthropic API key for full corrections."}


@app.get("/api/writing")
def writing_history(lang: str):
    with db.db() as con:
        rows = con.execute("SELECT * FROM writings WHERE lang=? ORDER BY ts DESC LIMIT 20", (_lang(lang),)).fetchall()
    return [dict(r) | {"feedback": json.loads(r["feedback"])} for r in rows]


# ---------------------------------------------------------------- analytics & plan
@app.get("/api/insights")
def get_insights(lang: str):
    return insights.build(_lang(lang))


@app.get("/api/schedule")
def get_schedule():
    return schedule.build()


# ---------------------------------------------------------------- frontend
@app.middleware("http")
async def revalidate_frontend(request, call_next):
    # Make the browser re-check the HTML/JS/CSS on every load (cheap 304s via ETag), so an
    # update never mixes a stale cached module with new ones and leaves a blank page.
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")
