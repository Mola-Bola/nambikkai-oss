# Install into PAI / LifeOS

Nambikkai is built to compose into folder-of-markdown agent OSes — PAI, LifeOS, or
your homegrown equivalent. It adds the trust layer; it changes nothing else.

## 1 · Install the plugin

```bash
claude plugin marketplace add YOUR-GITHUB-USER/nambikkai
claude plugin install nambikkai@nambikkai
```

The gate and flag hooks now cover every session in your OS's repo — including your
OS's own scheduled/headless runs, which is exactly where you want them.

## 2 · Point the receipts at your context files

Your OS keeps life context in markdown (PAI's `USER`/context scaffolds, LifeOS's
knowledge layer, your `domains/` folder). Adopt the receipt tag there:

```
- Passport renewal due next spring; scans in the vault.  [src: self | 2026-06 | firm | review:2027-01]
```

Then run the lint whenever you want a hygiene report:

> lint my vault

## 3 · Teach your OS's rituals the drill

If your OS has a daily/weekly review ritual, add one line to it: *read
`.nambikkai/alerts.log`; any real leak becomes a corpus case* (say "log this
incident" — the `incident-to-eval` skill scaffolds it).

## 4 · Optional: adopt the Gate pattern

If your OS runs scheduled headless agents, apply
[stage-only autonomy](../concepts/gate.md): strip commit/push verbs from the headless
allowlist, stage work to an inbox, review at a fixed ritual. This is a pattern to
apply in *your* settings, not something the plugin can impose.

## What you keep

Everything. Your OS's skills, structure, and rituals are untouched — Nambikkai sits at
the harness layer beneath them. If you uninstall it, nothing breaks; you're just
trusting prompts again.
