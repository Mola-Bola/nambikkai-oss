#!/usr/bin/env bash
# Nambikkai dev runner — backend + frontend on 127.0.0.1; both die together
# on Ctrl-C. Ports: PORT (app, default 5173) · NAMBIKKAI_API_PORT (default 8787).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export PORT="${PORT:-5173}"
export NAMBIKKAI_API_PORT="${NAMBIKKAI_API_PORT:-8787}"

"$ROOT/.venv/bin/uvicorn" main:app --app-dir "$ROOT/app/backend" \
  --host 127.0.0.1 --port "$NAMBIKKAI_API_PORT" --log-level warning &
BACK=$!
trap 'kill "$BACK" 2>/dev/null || true' EXIT

echo
echo "  Nambikkai → http://127.0.0.1:$PORT"
echo

cd "$ROOT/app/frontend" && npx vite --host 127.0.0.1 --port "$PORT" --strictPort
