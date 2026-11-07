"""SQLite storage. One file, no server, easy to back up (data/bruecke.db)."""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

DB_PATH = Path(os.environ.get("BRUECKE_DB", Path(__file__).resolve().parents[1] / "data" / "bruecke.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS cards (
    item_id TEXT, skill TEXT, lang TEXT,
    ease REAL DEFAULT 2.5, interval REAL DEFAULT 0, due REAL, reps INTEGER DEFAULT 0,
    lapses INTEGER DEFAULT 0, last_seen REAL, PRIMARY KEY (item_id, skill));
CREATE INDEX IF NOT EXISTS cards_due ON cards(lang, due);
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, day TEXT, lang TEXT, item_id TEXT, skill TEXT, ex_type TEXT,
    grade TEXT, correct INTEGER, categories TEXT, given TEXT, expected TEXT, detail TEXT,
    session_kind TEXT, session_id TEXT, seconds REAL DEFAULT 0, xp INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS attempts_lang_ts ON attempts(lang, ts);
CREATE TABLE IF NOT EXISTS progress (unit_id TEXT, part INTEGER, lang TEXT, completed_at REAL, PRIMARY KEY (unit_id, part));
CREATE TABLE IF NOT EXISTS activity (day TEXT, lang TEXT, seconds REAL DEFAULT 0, PRIMARY KEY (day, lang));
CREATE TABLE IF NOT EXISTS checkpoints (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, lang TEXT, stage INTEGER, scores TEXT);
CREATE TABLE IF NOT EXISTS writings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, lang TEXT, unit_id TEXT, prompt TEXT, text TEXT, feedback TEXT);
"""

DEFAULTS = {
    "start_date": None,          # filled with today on first run
    "daily_minutes": 120,
    "first_lang": "de",
    "second_lang_start_week": 3,
    "speech_rate": 0.95,
    "voice_de": "",
    "voice_fr": "",
    "grammar_colors": True,
    "current_lang": "de",
    "ai_model": "claude-opus-5-5",
    "challenge_mode": "auto",    # "auto" or a fixed level "1".."5"
    "stretch_goal": False,       # True = show the B2 stretch stages now
}


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    return con


@contextmanager
def db():
    con = connect()
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init():
    with db() as con:
        con.executescript(SCHEMA)
        if con.execute("SELECT 1 FROM settings WHERE key='start_date'").fetchone() is None:
            con.execute("INSERT INTO settings VALUES ('start_date', ?)", (json.dumps(date.today().isoformat()),))


def get_settings() -> dict:
    with db() as con:
        rows = {r["key"]: json.loads(r["value"]) for r in con.execute("SELECT key, value FROM settings")}
    out = dict(DEFAULTS)
    out.update(rows)
    return out


def set_settings(values: dict):
    with db() as con:
        for k, v in values.items():
            if k in DEFAULTS:
                con.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (k, json.dumps(v)))
