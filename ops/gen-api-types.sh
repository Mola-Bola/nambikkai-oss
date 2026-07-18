#!/usr/bin/env bash
# ============================================================================
# Regenerate the frontend's API types from FastAPI's OpenAPI schema.
# (FOUNDATIONS add-now item 6 — backend/frontend drift dies as a class.)
#
# Run after ANY change to a request/response model in app/backend/main.py:
#   make api-types
# Then `npx tsc -b` in app/frontend will fail loudly if the UI used a field the
# backend no longer sends.
# ============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/app/frontend/src/api-types.ts"

# Importing the app mints a session token; point it at a throwaway dir so schema
# generation never touches the real journal.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

NAMBIKKAI_DATA="$TMP" PYTHONPATH="$ROOT/app/backend" "$ROOT/.venv/bin/python" -c "
import json
from main import app
print(json.dumps(app.openapi()))
" > "$TMP/openapi.json"

cd "$ROOT/app/frontend"
npx --yes openapi-typescript "$TMP/openapi.json" -o "$OUT"
echo "wrote $OUT"
