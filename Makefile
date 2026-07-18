# Nambikkai — one command to run, one to test.
#
# TWO INTERPRETERS, DELIBERATELY:
#   .venv (3.13, uv-managed)  the web app — FastAPI, the ledger, the app suite
#   system python3 (3.9 here) the engine — plugin/hooks/* are Claude Code hooks
#                             invoked as bare `python3`, so the corpus suites
#                             MUST run there to prove hook compatibility. A ruff
#                             upgrade to datetime.UTC already broke this once.
PY := $(shell command -v /opt/homebrew/bin/python3.13 || command -v python3)
UV := .venv/bin/uv

dev: .venv/.ok app/frontend/node_modules
	bash ops/dev.sh

.venv/.ok: pyproject.toml uv.lock
	$(PY) -m venv .venv
	.venv/bin/pip install -q uv
	$(UV) sync --quiet
	@touch .venv/.ok

app/frontend/node_modules: app/frontend/package.json
	cd app/frontend && npm install

# Everything, both interpreters. This is the gate before any commit.
test: .venv/.ok
	python3 tests/test_guard.py
	python3 tests/test_mcp.py
	.venv/bin/python tests/test_app.py
	.venv/bin/python tests/test_vectors.py
	.venv/bin/python tests/test_journey.py
	.venv/bin/python tests/test_reflection.py

# The local embedding model (ADR 003). One explicit step, checksummed, run once.
# The app works without it: matching falls back to shared words until it lands.
model:
	bash ops/fetch-model.sh

# Rebuild the relevance index from the ledger. The index is a derived view, so
# this is always safe -- and it is the fix for anything that looks wrong there.
index: .venv/.ok
	.venv/bin/python app/backend/index.py --rebuild

# Convert a public-domain diary into an import file, for the optional real-life
# demo set. Reads corpus-data/ (gitignored) and writes build/ (gitignored), so
# the diary text never enters version control at either end. Stdlib only, so it
# runs on the system interpreter without the venv.
demo-diary:
	python3 ops/convert-diary.py

lint: .venv/.ok
	.venv/bin/ruff check .

fmt: .venv/.ok
	.venv/bin/ruff check --fix .

hooks: .venv/.ok
	.venv/bin/pre-commit install

# Regenerate app/frontend/src/api-types.ts from FastAPI's OpenAPI schema.
# Run after any change to a request/response model, then typecheck.
api-types: .venv/.ok app/frontend/node_modules
	bash ops/gen-api-types.sh
	cd app/frontend && npx tsc --noEmit

# Copy data/ somewhere safe; see docs/operations/backup-restore.md.
backup:
	bash ops/backup.sh

.PHONY: dev test lint fmt hooks backup api-types model index demo-diary
