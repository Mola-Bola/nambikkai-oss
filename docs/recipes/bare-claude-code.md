# Bare Claude Code project

No agent OS — just a repo where Claude Code handles material you'd rather not leak.

## Install

```bash
claude plugin marketplace add YOUR-GITHUB-USER/nambikkai
claude plugin install nambikkai@nambikkai
```

Done — the perimeter is live for every session. Verify:

```bash
python3 tests/test_guard.py   # from a clone of this repo
```

or just ask your agent to write a split synthetic ID (see the
[quickstart](../quickstart.md)) and watch the refusal.

## Housekeeping

```bash
echo ".nambikkai/" >> .gitignore   # the alert log is telemetry, not history
```

## Recommended minimum posture

1. **A secrets directory that never syncs.** Keep raw identifiers/documents in one
   gitignored folder; everywhere else, reference them by pointer. The gate makes the
   wrong path annoying; the folder makes the right path easy.
2. **Receipts on durable facts** — even in a plain project, `[src | date | tier | ttl]`
   on the facts your agent relies on pays for itself the first time something goes
   stale. See [Receipts](../concepts/receipts.md).
3. **Read the alert log occasionally.** A WARN pattern that keeps repeating is either
   a false-positive shape worth a `must_stay` corpus PR, or a habit worth changing.

## CI self-test (optional)

```yaml
# .github/workflows/nambikkai.yml
name: nambikkai
on: [push]
jobs:
  selftest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 tests/test_guard.py
```

The corpus replays on every push; a drifted rule fails the build.
