# Nambikkai — one command to run, one to test.
PY := $(shell command -v /opt/homebrew/bin/python3.13 || command -v python3)

dev: .venv/.ok app/frontend/node_modules
	bash ops/dev.sh

.venv/.ok: app/backend/requirements.txt
	$(PY) -m venv .venv
	.venv/bin/pip install -q -r app/backend/requirements.txt
	@touch .venv/.ok

app/frontend/node_modules: app/frontend/package.json
	cd app/frontend && npm install

test: .venv/.ok
	python3 tests/test_guard.py
	python3 tests/test_mcp.py
	.venv/bin/python tests/test_app.py

.PHONY: dev test
