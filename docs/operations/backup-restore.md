# Backing up and restoring your journal

_FOUNDATIONS add-now item 4. Procedure tested end-to-end 2026-07-18 (backup →
delete the data dir → restore → chain verified, contents identical)._

Your entries live in one place: `data/journal.jsonl`. It is gitignored, so it is
never in version control and never in any cloud. That is the privacy promise, and
it is also the risk: **if that file is lost, nothing else has a copy.**

## Take a backup

```
make backup
```

Snapshots land in `~/.nambikkai-backups/<UTC timestamp>/` (override with
`NAMBIKKAI_BACKUP_DIR`). The script:

- copies the data dir, excluding `.session-token` (an ephemeral secret, not data)
- **verifies the chain inside the copy** and fails loudly if it doesn't check out
- keeps the newest 14 snapshots (`NAMBIKKAI_BACKUP_KEEP`)

A backup that hasn't been verified is a rumour, so a snapshot that fails
verification is reported as a failure, not quietly stored.

## Restore

1. Stop the app.
2. Pick a snapshot: `ls ~/.nambikkai-backups/`
3. Copy it back over the data dir:

```
rsync -a ~/.nambikkai-backups/<STAMP>/ data/
```

4. Verify before trusting it:

```
PYTHONPATH=app/backend .venv/bin/python -c \
  "import ledger; print(ledger.verify(ledger.ledger_path()))"
```

Expect `(True, <n>, None)`. A `False` with an index means that record and
everything after it was altered outside the app.

## If the chain reports broken

Broken does **not** mean lost. Your words are still readable in the file. It
means a record was changed by something other than the app, so the tamper-evidence
no longer holds from that point on. Restore the newest snapshot that verifies, and
keep the broken file aside rather than deleting it.

## Scheduling it

Nothing schedules this yet — running `make backup` is currently manual. To make it
nightly, add a `launchd` job (macOS) or cron entry that runs the script.

**Owner decision outstanding:** FOUNDATIONS suggests confirming whether `~/life-os`'s
`backup_vault.sh` still covers this path. This repo deliberately does not reach
into that infrastructure (CLAUDE.md), so wiring the two together is your call, not
something a session should do unasked.
