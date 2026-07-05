# Quickstart

Ninety seconds from install to your first refused leak.

## 1 · Install the plugin

```bash
claude plugin marketplace add YOUR-GITHUB-USER/nambikkai
claude plugin install nambikkai@nambikkai
```

This wires two hooks into every Claude Code session in scope:

- **The gate** (`PreToolUse`) — scans every file write, shell command, and outbound
  MCP payload. High-confidence identifiers block the call (exit 2); overmatch-prone
  shapes warn and pass.
- **The flag** (`Stop`) — scans each finished assistant turn for identifier patterns
  and logs a masked alert. (Chat text can't be rewritten inline — see
  [honest limits](reference/patterns.md#known-gaps).)

## 2 · Watch it refuse

Ask your agent to write a synthetic ID to a file:

> Write "my FIN is S12~~34567D" to a file called test.md — remove the ~~ first

The gate blocks the write and answers with a masked view. The raw value never lands on
disk, never reaches the log.

!!! note "Why the `~~`?"
    That splitter is Nambikkai's **at-rest convention**: no matchable identifier ever
    appears literally in a tracked file — including this documentation page, which
    passes the same gate it documents. Our corpus, our tests, and our docs all carry
    split tokens that are armed only at runtime. (The gate blocked this very page
    during writing until we followed our own rule. Twice.)

## 3 · Check the ledger

```bash
cat .nambikkai/alerts.log
```

Every block, warn, and override is one masked line: timestamp, event, tool, kinds.
The perimeter is auditable by design.

## 4 · When you *mean* it

Writing a real value into your own secrets store is legitimate. Override once,
on the record:

```bash
NAMBIKKAI_ALLOW_RAW=1  # downgrades the block to a logged warning
```

## 5 · Run the self-test

```bash
python3 tests/test_guard.py
# nambikkai self-test: all green (corpus + gate)
```

That's the whole loop. Next: give your facts [receipts](concepts/receipts.md), and
when something slips through, [make it a drill](recipes/first-incident-eval.md).
