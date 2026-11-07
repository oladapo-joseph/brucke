"""Brücke. Loads KEY=value lines from the project's .env file (if present) into the environment,
without overriding variables that are already set."""
import os
from pathlib import Path

_env = Path(__file__).resolve().parents[1] / ".env"
if _env.is_file():
    for _line in _env.read_text(encoding="utf-8-sig").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
