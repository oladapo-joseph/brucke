#!/usr/bin/env bash
# Start Brücke at http://localhost:8000  (export ANTHROPIC_API_KEY first to enable Claude features)
cd "$(dirname "$0")"
exec python3 -m uvicorn app.main:app --port "${PORT:-8000}" --reload
