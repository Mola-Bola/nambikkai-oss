# Nambikkai

**Trust, with receipts.**

Your agents remember your life. Nambikkai is how you trust them with it — every fact
carries provenance, every leak-shaped byte stops at the boundary, every failure becomes
a permanent test.

Not an OS. A component. Install it into the agent system you already run.

```
claude plugin marketplace add YOUR-GITHUB-USER/nambikkai
claude plugin install nambikkai@nambikkai
```

Ninety seconds later, ask your agent to write a (synthetic) national ID to a file and
watch the gate refuse.

---

## Why this exists

The agent-OS race is real — PAI, LifeOS, a dozen folder-of-markdown operating systems,
each giving an AI persistent memory of your goals, money, health, and people. All of
them combine the three ingredients of the [lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/):
private data, tool access, and untrusted content. Almost none of them ship a control
for it beyond a promise in the prompt.

Scope, stated plainly: Nambikkai defends **one edge of that trifecta — the egress
edge**. It stops your private data leaking *out* through files, shells, and
connectors. It does not yet inspect untrusted content coming *in* (the
prompt-injection edge) — that's a roadmap line, not a shipped mechanism, and we'd
rather tell you than let the framing imply it.

Prompts are hopes. Nambikkai is mechanism:

| Pillar | What it means | What enforces it |
|---|---|---|
| **Receipts** | Every durable fact carries `[src \| date \| tier \| ttl]` — where it came from, when confirmed, how much to trust it, when to re-check | `provenance-lint` skill + the convention spec |
| **Perimeter** | Identifier-shaped bytes are stopped *at the harness boundary* — file writes, shell args, MCP payloads — before they leave | `PreToolUse` gate hook (exit 2 blocks the call) |
| **Drills** | Every incident becomes a corpus case the day it's resolved; the corpus replays on every test run | `incident-to-eval` skill + `tests/test_guard.py` |
| **Gate** | Autonomy is granted through approval gates, never assumed — agents propose, humans approve, mechanically | `conventions/stage-only-autonomy.md` pattern |

## The corpus is the point

One golden corpus — [`corpus/cases.json`](corpus/cases.json) — binds every
implementation. The Python hooks pass it. Any future port (TypeScript, Go, an MCP
server) must pass the *same file* or it doesn't ship. Rules drift; the corpus doesn't.

It's honest by construction, in four groups:

- `must_mask` — the guard must catch these
- `must_stay` — the guard must leave these alone
- `known_overmatch` — shapes we over-trigger on (warn, never block — documented, asserted)
- `known_gap` — what regex **cannot see** (free-text names, bare money amounts). Debt we
  publish, not a hole we hide. An opt-in classifier tier (`NAMBIKKAI_CLASSIFIER=1`,
  warn-only, fail-open) now covers these shapes — the corpus tags which cases are its
  contract, and a live calibration test holds it to them.

And one detail we're disproportionately proud of: every sensitive-shaped token in the
corpus carries a `~~` splitter, so the corpus file itself never contains a matchable
identifier at rest. The test suite arms them at runtime. **The corpus passes its own
gate.** (Our gate blocked our own test file during development. Working as intended.)

## What Nambikkai is not

- **Not an OS.** It's one cog, built to compose into a system of systems — yours.
- **Not a PII detection library.** [Presidio](https://github.com/microsoft/presidio)
  and [llm-guard](https://github.com/protectai/llm-guard) detect well as libraries an
  app must remember to call. Nambikkai's bet is *placement*: enforcement wired into the
  agent harness itself, where forgetting isn't possible.
- **Not finished.** v0.1 ships an SG/AU-flavored identifier pack (NRIC/FIN, AU mobile,
  passports, account numbers, DOBs, brokerage refs). Regional packs land as corpus PRs
  — a rule without cases doesn't merge.

## What's in the box

```
nambikkai/
├── plugin/            Claude Code plugin — hooks (gate + chat flag + opt-in classifier) + 2 skills
├── mcp/               trust-gate MCP server — check / redact / tag_fact / lint, any MCP client
├── corpus/            the golden corpus (synthetic, split at rest) — binds hooks AND server
├── conventions/       provenance receipts · trust doctrine · stage-only autonomy
├── tests/             self-tests: corpus drift-guard + gate + server-vs-corpus
└── docs/              the full documentation
```

Run the self-tests any time:

```
python3 tests/test_guard.py   # corpus + gate (+ classifier calibration when a key is present)
python3 tests/test_mcp.py     # the MCP server against the same corpus
```

## Escape hatch, on the record

Sometimes you *mean* to write a real value into your local secrets store:

```
NAMBIKKAI_ALLOW_RAW=1
```

downgrades the next block to a logged warning. Every block, warn, and override lands in
`.nambikkai/alerts.log` as a masked snippet — never the raw value. The perimeter has a
door; the door has a light over it.

## Roadmap

- **v0.1** — Claude Code plugin (hooks + skills), corpus, conventions, docs
- **v0.2** — `trust-gate` MCP server: `check` / `redact` / `tag_fact` / `lint` for any MCP client ← you are here
- **v0.3** — npm + PyPI packages; the corpus ships as fixtures
- **v0.x** — ~~classifier pass for the `known_gap` class~~ shipped as opt-in warn tier
  (`NAMBIKKAI_CLASSIFIER=1`); blocking mode after calibration · regional packs
- **v0.x** — **input perimeter** (the trifecta's other edge): untrusted-content
  checks on tool *results* before they steer the agent. Explicitly not built yet —
  design first, as a proposal

## License

[MIT](LICENSE) © The Nambikkai authors

---

*நம்பிக்கை (nambikkai) — Tamil: trust, faith, hope.*
