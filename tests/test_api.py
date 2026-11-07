import os
import tempfile

os.environ["BRUECKE_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.content import course  # noqa: E402
from app.main import app  # noqa: E402
from app.schedule import expected_stage  # noqa: E402

c = TestClient(app)


def test_course_loaded():
    assert len([u for u in course.units if u.startswith("de-")]) == 8
    assert len([u for u in course.units if u.startswith("fr-")]) == 8
    for it in course.items.values():  # every reading question points at a real option
        for q in it.get("questions", []):
            assert 0 <= q["a"] < len(q["options"])


def test_every_lesson_part_renders():
    for uid in course.units:
        parts = c.get(f"/api/units/{uid}").json()["parts"]
        for p in parts:
            r = c.get(f"/api/lesson/{uid}/{p['n']}")
            assert r.status_code == 200 and r.json()["steps"], (uid, p)


def test_staggered_schedule():
    s = {"first_lang": "de", "second_lang_start_week": 3}
    assert [expected_stage(s, "fr", w) for w in (1, 2, 3, 26)] == [0, 0, 1, 26]
    assert [expected_stage(s, "de", w) for w in (1, 13, 26)] == [1, 13, 26]


def test_learning_loop_feeds_insights():
    assert c.get("/api/session", params={"lang": "de"}).json()["empty"] is True
    c.post("/api/progress", json={"unit_id": "de-03", "part": 0})
    item = course.items["de:v:der-tisch"]
    for _ in range(3):
        r = c.post("/api/answer", json={"lang": "de", "item_id": item["id"], "skill": "writing", "type": "gender", "answer": "die"}).json()
        assert r["grade"] == "wrong" and r["categories"][0]["id"] == "gender"
    ins = c.get("/api/insights", params={"lang": "de"}).json()
    assert ins["categories"][0]["id"] == "gender"
    assert ins["gaps"][0]["item_id"] == item["id"]
    assert ins["confusions"][0]["word"] == "Tisch"
    # the adaptive mix now includes targeted gender drills
    s = c.get("/api/session", params={"lang": "de"}).json()
    assert "gender" in s["focus_categories"]
    assert any(e["type"] == "gender" for e in s["exercises"])


def test_writing_offline_feedback():
    r = c.post("/api/writing", json={"lang": "de", "text": "der hund ist groß. Ich habe eine katze. Gut.", "unit_id": "de-03"}).json()
    assert r["id"] and ("errors" in r)


def test_ai_unit_schema_conversion():
    from app.ai import _to_internal
    u = _to_internal("de", 9, {
        "title": "T", "native": "N", "can_do": ["x"], "grammar": [{"title": "g", "body": "b", "table": []}],
        "vocab": [{"w": "der Bahnhof", "en": "station", "pos": "noun", "g": "m", "pl": "die Bahnhöfe", "forms": [], "ex_t": "Wo ist der Bahnhof?", "ex_en": "Where is the station?", "en_alt": []}],
        "sentences": [{"t": "Ich gehe zum Bahnhof.", "en": "I'm going to the station.", "alt": [], "en_alt": []}],
        "reading": {"title": "r", "text": "t", "en": "e", "questions": [{"q": "q", "options": ["a", "b"], "a": 7}]},
        "writing_prompt": "w", "writing_model": "m"})
    assert u["vocab"][0]["g"] == "m" and u["reading"]["questions"][0]["a"] == 1


def test_mix_shares_focus_slots_between_categories():
    from app.exercises import build_session
    c.post("/api/progress", json={"unit_id": "de-01", "part": 0})
    for _ in range(4):  # create a second recurring category: listening
        c.post("/api/answer", json={"lang": "de", "item_id": "de:snd:u-mude", "skill": "listening", "type": "listen_spell", "answer": "ja"})
    s = build_session("de", 15)
    whys = {e["why"] for e in s["exercises"]}
    assert {"focus:gender", "focus:listening"} <= whys


def test_alphabet_comes_first_in_stage_1():
    for lang in ("de", "fr"):
        parts = c.get(f"/api/units/{lang}-01").json()["parts"]
        assert [p["title"] for p in parts[:4]] == ["Alphabet 1", "Alphabet 2", "Alphabet 3", "Alphabet 4"]
        assert len(c.get(f"/api/units/{lang}-01").json()["letters"]) == 30


def test_letter_answers():
    r = c.post("/api/answer", json={"lang": "de", "item_id": "de:ltr:E", "skill": "listening", "type": "letter_listen", "answer": "I"}).json()
    assert r["grade"] == "wrong" and r["categories"][0]["id"] == "letters"
    r = c.post("/api/answer", json={"lang": "de", "item_id": "de:ltr:W", "skill": "writing", "type": "spell", "answer": "Wasser"}).json()
    assert r["grade"] == "correct" and "Doppel-Es" in r["spelled"]
    r = c.post("/api/answer", json={"lang": "fr", "item_id": "fr:ltr:é", "skill": "writing", "type": "spell", "answer": "cafe"}).json()
    assert r["grade"] == "almost"  # missing accent
    r = c.post("/api/answer", json={"lang": "fr", "item_id": "fr:ltr:G", "skill": "speaking", "type": "speak", "transcripts": ["gare"]}).json()
    assert r["grade"] == "correct"


def test_letter_drill_types_fall_back():
    from app.exercises import make_exercise
    assert make_exercise(course.items["de:ltr:V"], "listening", "dictation")["type"] == "letter_listen"
    assert make_exercise(course.items["de:ltr:V"], "writing", "translate")["type"] == "spell"
    assert make_exercise(course.items["de:v:der-tisch"], "writing", "spell")["type"] != "spell"


def test_numbers():
    from app.evaluate import check_speech, number_word
    assert number_word(97, "fr") == "quatre-vingt-dix-sept" and number_word(71, "fr") == "soixante et onze"
    assert number_word(45, "de") == "fünfundvierzig" and number_word(21, "de") == "einundzwanzig"
    assert check_speech(["ça coûte 70 euros"], "Ça coûte soixante-dix euros.", "fr").grade == "correct"
    assert "fr:v:quatre-vingt-dix" in course.items and "de:v:siebzehn" in course.items


def test_progress_migration_shifts_old_parts():
    from app import db as appdb
    from app.main import _migrate_progress
    with appdb.db() as con:
        con.execute("DELETE FROM settings WHERE key='content_version'")
        con.execute("DELETE FROM progress")
        con.execute("INSERT INTO progress VALUES ('de-01', 0, 'de', 0)")   # old 'Sounds 1'
        con.execute("INSERT INTO progress VALUES ('de-04', 3, 'de', 0)")   # old 'Sentences 1'
    _migrate_progress()
    _migrate_progress()  # idempotent
    with appdb.db() as con:
        rows = {(r["unit_id"], r["part"]) for r in con.execute("SELECT unit_id, part FROM progress")}
    parts1 = c.get("/api/units/de-01").json()["parts"]
    parts4 = c.get("/api/units/de-04").json()["parts"]
    assert rows == {("de-01", 4), ("de-04", 6)}
    assert parts1[4]["title"] == "Sounds 1" and parts1[4]["done"]
    assert parts4[6]["title"] == "Sentences 1" and parts4[6]["done"]


def test_bridges_match_real_words():
    from app.content.bridges import BRIDGES
    for lang, table in BRIDGES.items():
        texts = {course.items[i]["text"] for i in course.by_lang[lang]}
        assert set(table) <= texts, set(table) - texts
    assert course.items["de:v:das-haus"]["bridge"]["note"] == "house"
    assert course.items["de:v:das-handy"]["bridge"]["kind"] == "false"


def test_french_card_builds_on_known_german():
    from app.exercises import display
    table = course.items["fr:v:la-table"]
    assert "cross" not in display(table, {"fr:v:la-table"}) or display(table, {"fr:v:la-table"})["cross"] == []
    links = display(table, {"de:v:der-tisch"})["cross"]       # learned der Tisch in German
    assert links[0]["text"] == "der Tisch" and links[0]["clash"]  # masculine vs feminine
    same = display(course.items["fr:v:la-porte"], {"de:v:die-tur"})["cross"]
    assert "Same gender" in same[0]["note"]


def _testout(uid, part, correct=True):
    import uuid as _u
    sid = _u.uuid4().hex[:10]
    steps = c.get(f"/api/lesson/{uid}/{part}", params={"mode": "testout"}).json()["steps"]
    assert steps and all(s["step"] == "exercise" for s in steps)
    for s in steps:
        it = course.items[s["ex"]["item_id"]]
        ans = it["letter"] if s["ex"]["type"] == "letter_listen" else it["text"]
        if not correct:
            ans = "x"
        c.post("/api/answer", json={"lang": it["lang"], "item_id": it["id"], "skill": s["ex"]["skill"], "type": s["ex"]["type"],
                                    "answer": ans, "session_kind": "testout", "session_id": sid})
    return c.post("/api/testout/finish", json={"unit_id": uid, "part": part, "session_id": sid}).json()


def test_testout_pass_and_fail():
    bad = _testout("fr-04", 0, correct=False)
    assert not bad["passed"] and bad["missed"]
    good = _testout("fr-04", 1, correct=True)
    assert good["passed"]
    parts = c.get("/api/units/fr-04").json()["parts"]
    assert parts[1]["done"] and not parts[0]["done"]


def _fake_answers(lang, grade, n=40):
    import time as _t
    from app import db as appdb
    with appdb.db() as con:
        for k in range(n):
            con.execute("INSERT INTO attempts (ts, day, lang, item_id, skill, ex_type, grade, correct, categories, given, expected, "
                        "detail, session_kind, session_id, xp) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (_t.time() + 1000 + k, "2099-01-01", lang, f"{lang}:v:x", "writing", "translate", grade,
                         int(grade != "wrong"), "[]", "", "", "{}", "mix", "", 0))


def test_challenge_rises_when_coasting_and_eases_when_struggling():
    from app import challenge, db as appdb
    with appdb.db() as con:
        con.execute("DELETE FROM settings WHERE key IN ('challenge_fr', 'challenge_mode')")
    assert challenge.level("fr") == 2
    _fake_answers("fr", "correct")
    with appdb.db() as con:
        change = challenge.update(con, "fr")
    assert change and change["to"] == 3 and challenge.level("fr") == 3
    with appdb.db() as con:                       # no ping-pong right after a change
        assert challenge.update(con, "fr") is None
    _fake_answers("fr", "wrong")
    with appdb.db() as con:
        change = challenge.update(con, "fr")
    assert change and change["to"] == 2


def test_manual_challenge_mode_wins():
    from app import challenge
    c.put("/api/settings", json={"values": {"challenge_mode": "5"}})
    assert challenge.level("de") == 5
    assert c.put("/api/settings", json={"values": {"challenge_mode": "9"}}).status_code == 400
    c.put("/api/settings", json={"values": {"challenge_mode": "auto"}})


def test_higher_levels_mean_harder_exercises():
    from app.exercises import choose_type, make_exercise
    tisch, sent = course.items["de:v:der-tisch"], course.items["de:s:ich-habe-einen-hund"]
    assert choose_type(tisch, "listening", 0, level=2) == "listen_choose"
    assert choose_type(tisch, "listening", 0, level=4) == "dictation"      # production straight away
    assert choose_type(tisch, "writing", 0, level=4) == "translate"        # no gender multiple choice
    assert make_exercise(sent, "writing", "build", level=2)["decoys"] == 0
    ex = make_exercise(sent, "writing", "build", level=4)
    assert ex["decoys"] >= 1 and len(ex["tiles"]) > 4
    assert make_exercise(tisch, "listening", "dictation", level=5)["slow_audio"] is False


def test_strict_accents_at_hard_level():
    c.put("/api/settings", json={"values": {"challenge_mode": "4"}})
    r = c.post("/api/answer", json={"lang": "fr", "item_id": "fr:v:l-ecole", "skill": "writing", "type": "translate", "answer": "l'ecole"}).json()
    assert r["grade"] == "wrong"
    c.put("/api/settings", json={"values": {"challenge_mode": "auto"}})
    r = c.post("/api/answer", json={"lang": "fr", "item_id": "fr:v:l-ecole", "skill": "writing", "type": "translate", "answer": "l'ecole"}).json()
    assert r["grade"] == "almost"


def test_stretch_goal_adds_scope():
    units = c.get("/api/units", params={"lang": "de"}).json()
    assert max(u["stage"] for u in units["units"]) == 26 and not units["stretch"]
    c.put("/api/settings", json={"values": {"stretch_goal": True}})
    units = c.get("/api/units", params={"lang": "de"}).json()
    assert units["stretch"] and max(u["stage"] for u in units["units"]) == 32
    assert units["units"][-1]["level"] == "B2"
    c.put("/api/settings", json={"values": {"stretch_goal": False}})


def test_pace_projection():
    from datetime import date, timedelta
    from app import schedule
    s = {"start_date": (date.today() - timedelta(days=13)).isoformat(), "first_lang": "de", "second_lang_start_week": 3}
    p = schedule.pace(s, "de")
    assert p["days"] == 14 and "status" in p
    assert schedule.pace(s, "fr") is None   # French hasn't started in week 2
