"""Optional Claude features. Everything else in the app works without them.

  • grade_writing  – corrects free writing and tags each error with the app's mistake categories,
                     so AI feedback feeds the same insights engine as the drills
  • generate_unit  – turns a syllabus outline (stages 9–26) into a full unit in the app's schema

Credentials: ANTHROPIC_API_KEY (or ANTHROPIC_AUTH_TOKEN / an `ant auth login` profile).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .content import GENERATED_DIR, LANGS, course, level_for
from .content.syllabus import OUTLINE
from .db import get_settings
from .evaluate import CATEGORIES

try:
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AIError(Exception):
    pass


def available() -> bool:
    if anthropic is None:
        return False
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    return (Path.home() / ".config" / "anthropic").exists()


def _client():
    if not available():
        raise AIError("Claude isn't configured. Set ANTHROPIC_API_KEY and restart the app.")
    return anthropic.Anthropic()


def _structured(system: str, user: str, schema: dict, effort: str, max_tokens: int) -> dict:
    client = _client()
    model = get_settings().get("ai_model") or "claude-opus-5-5"
    try:
        with client.beta.messages.stream(
            model=model,
            max_tokens=max_tokens,
            betas=[FALLBACK_BETA],
            fallbacks="default",
            system=system,
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
            messages=[{"role": "user", "content": user}],
        ) as stream:
            msg = stream.get_final_message()
    except anthropic.AuthenticationError:
        raise AIError("Your Anthropic API key was rejected.")
    except anthropic.RateLimitError:
        raise AIError("Rate limited by the API. Try again in a minute.")
    except anthropic.APIConnectionError:
        raise AIError("Couldn't reach the Anthropic API. Check your internet connection.")
    except anthropic.APIStatusError as e:
        raise AIError(f"API error {e.status_code}: {e.message}")
    if msg.stop_reason == "refusal":
        raise AIError("Claude declined this request.")
    if msg.stop_reason == "max_tokens":
        raise AIError("The response was cut off. Try again.")
    text = next((b.text for b in msg.content if b.type == "text"), "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise AIError("Claude returned an unexpected format. Try again.")


# ---------------------------------------------------------------- writing feedback
WRITING_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["corrected", "score", "cefr", "summary", "praise", "errors", "next_focus"],
    "properties": {
        "corrected": {"type": "string", "description": "The learner's text, minimally corrected."},
        "score": {"type": "integer", "description": "0–100 for accuracy and task completion at the target level."},
        "cefr": {"type": "string", "description": "Estimated CEFR level of this text, e.g. A1, A2-, A2, B1."},
        "summary": {"type": "string"},
        "praise": {"type": "string"},
        "next_focus": {"type": "string"},
        "errors": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["original", "correction", "category", "explanation"],
            "properties": {
                "original": {"type": "string"}, "correction": {"type": "string"},
                "category": {"type": "string", "enum": list(CATEGORIES)},
                "explanation": {"type": "string"},
            }}},
    },
}


def grade_writing(lang: str, stage: int, prompt: str, text: str) -> dict:
    name = LANGS[lang]["name"]
    level = level_for(stage)
    system = (
        f"You are a warm, precise {name} tutor. The learner is a native English speaker working through a "
        f"6-month A1→B1 course (currently stage {stage}/26, level {level}). They study German and French in parallel. "
        "Correct only real errors; don't rewrite for style. Keep explanations in English, short, concrete, and "
        "pitched at their level. Tag each error with exactly one category from the schema. Use 'gender' for wrong "
        "noun gender/article, 'case' for case endings, 'conjugation' for verb forms, 'endings' for adjective/participle "
        "agreement, 'word_order' for position errors, 'accents' for missing or wrong diacritics, 'capitalization' for "
        "German noun capitals, 'missing_word' for omitted or extra words, 'vocabulary' for the wrong word, and 'spelling' "
        "for other typos. Score against what's expected at their level, not at native level."
    )
    user = f"Task given to the learner:\n{prompt}\n\nTheir text ({name}):\n{text}"
    out = _structured(system, user, WRITING_SCHEMA, effort="medium", max_tokens=8000)
    out["source"] = "claude"
    return out


# ---------------------------------------------------------------- unit generation
_STR_LIST = {"type": "array", "items": {"type": "string"}}
UNIT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "native", "can_do", "grammar", "vocab", "sentences", "reading", "writing_prompt", "writing_model"],
    "properties": {
        "title": {"type": "string"}, "native": {"type": "string"}, "can_do": _STR_LIST,
        "grammar": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["title", "body", "table"],
            "properties": {"title": {"type": "string"}, "body": {"type": "string"},
                           "table": {"type": "array", "items": _STR_LIST}}}},
        "vocab": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["w", "en", "pos", "g", "pl", "forms", "ex_t", "ex_en", "en_alt"],
            "properties": {
                "w": {"type": "string"}, "en": {"type": "string"},
                "pos": {"type": "string", "enum": ["noun", "verb", "adj", "pron", "det", "prep", "conj", "q", "num", "phrase"]},
                "g": {"type": "string", "enum": ["m", "f", "n", "pl", ""]},
                "pl": {"type": "string"}, "forms": _STR_LIST, "ex_t": {"type": "string"}, "ex_en": {"type": "string"},
                "en_alt": _STR_LIST}}},
        "sentences": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["t", "en", "alt", "en_alt"],
            "properties": {"t": {"type": "string"}, "en": {"type": "string"}, "alt": _STR_LIST, "en_alt": _STR_LIST}}},
        "reading": {"type": "object", "additionalProperties": False, "required": ["title", "text", "en", "questions"],
                    "properties": {"title": {"type": "string"}, "text": {"type": "string"}, "en": {"type": "string"},
                                   "questions": {"type": "array", "items": {
                                       "type": "object", "additionalProperties": False, "required": ["q", "options", "a"],
                                       "properties": {"q": {"type": "string"}, "options": _STR_LIST, "a": {"type": "integer"}}}}}},
        "writing_prompt": {"type": "string"}, "writing_model": {"type": "string"},
    },
}


def generate_unit(lang: str, stage: int) -> dict:
    if stage not in OUTLINE[lang]:
        raise AIError("Only stages 9–32 are generated. Stages 1–8 are built in.")
    if course.unit(lang, stage):
        raise AIError("This stage already has content.")
    title, grammar, can_do, themes = OUTLINE[lang][stage]
    name = LANGS[lang]["name"]
    level = level_for(stage)
    known = course.learned_vocab(lang, stage - 1)
    prev = [course.outline(lang, s)["title"] + (": " + course.outline(lang, s).get("grammar_focus", "") if not course.unit(lang, s) else "")
            for s in range(1, stage)]
    system = (
        f"You write units for a personal {name} course for a native English speaker going from A1 to B1 in 26 stages, "
        "with stretch stages 27–32 towards B2 for when they're ahead of schedule. "
        "They learn German and French in parallel, German first. The app colour-codes grammar: masculine ■ blue, feminine ● rose, "
        "neuter ▲ green, plural ◆ violet, verbs orange. Explanations are in English: friendly, short, concrete, never academic. "
        "Grammar `body` supports **bold**, *italic*, ~~silent letters~~ and line breaks (\\n), with no HTML. Use `table` for "
        "conjugations or article grids (first row = header) or [] if not needed. Where it helps, contrast with the other language "
        "the learner is studying. Everything must be correct, natural, standard "
        f"{name}. Make sure every `alt` sentence is genuinely correct."
    )
    user = f"""Write stage {stage} ({level}) of the {name} course.

Title: {title}
Grammar focus: {grammar}
Can-do goal: {can_do}
Vocabulary themes: {themes}

Previous stages: {"; ".join(prev)}
Words the learner already knows (do NOT repeat these as vocab items): {", ".join(known)}

Requirements:
- 2–4 grammar notes building the focus step by step, with tables where useful.
- 14–16 vocab items. Nouns: `w` includes the article ({"der/die/das" if lang == "de" else "le/la/l'/les"}), `g` is m/f/n/pl, and `pl` is the plural with its article. Verbs: `w` is the infinitive and `forms` lists the present-tense forms you use (plus participles if relevant). Other pos: `g` "" and `pl` "". Give every vocab item an example sentence (`ex_t`/`ex_en`).
- 8–10 sentences that use the grammar focus and the new vocabulary, short enough to type (max ~12 words), with accepted alternative word orders or forms in `alt` and alternative English meanings in `en_alt`.
- A reading text of {"70–110" if level == "A2" else "120–170" if level == "B1" else "180–240"} words, with an English translation in `en` and 3 multiple-choice questions in English, 4 options each. `a` is the index of the correct option; vary its position.
- A writing prompt in English that makes the learner use the grammar focus, plus a short model answer.
- `can_do`: 3 short goals. `native`: the title in {name}."""
    data = _structured(system, user, UNIT_SCHEMA, effort="high", max_tokens=32000)
    unit = _to_internal(lang, stage, data)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    (GENERATED_DIR / f"{lang}-{stage:02d}.json").write_text(json.dumps(unit, ensure_ascii=False, indent=2), "utf-8")
    course.reload()
    return course.unit(lang, stage)


def _to_internal(lang: str, stage: int, d: dict) -> dict:
    vocab = []
    for v in d["vocab"]:
        item = {"kind": "vocab", "pos": v["pos"], "w": v["w"].strip(), "en": v["en"].strip(), "en_alt": v.get("en_alt", []),
                "ex": [v["ex_t"], v["ex_en"]] if v.get("ex_t") else None}
        if v["pos"] == "noun":
            item["g"] = v["g"] or "m"
            item["pl"] = v["pl"] or None
        if v["pos"] == "verb":
            item["forms"] = v.get("forms", [])
        vocab.append(item)
    reading = dict(d["reading"], kind="passage")
    for q in reading["questions"]:
        q["a"] = max(0, min(int(q["a"]), len(q["options"]) - 1))
    return {"lang": lang, "stage": stage, "title": d["title"], "native": d["native"], "can_do": d["can_do"],
            "grammar": [{"title": g["title"], "body": g["body"], "table": g["table"] or None} for g in d["grammar"]],
            "vocab": vocab, "sounds": [],
            "sentences": [{"kind": "sentence", "t": s["t"], "en": s["en"], "alt": s.get("alt", []), "en_alt": s.get("en_alt", [])}
                          for s in d["sentences"]],
            "reading": reading, "writing_prompt": d["writing_prompt"], "writing_model": d["writing_model"]}
