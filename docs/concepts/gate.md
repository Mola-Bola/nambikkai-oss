# The Gate

**Unattended agents propose; humans approve; the mechanism enforces it.**

The fourth pillar is a pattern, not a hook: **stage-only autonomy**. Scheduled and
headless agent runs should be *mechanically unable* to make permanent changes — not
instructed, prevented.

## The construction

1. **Reduced allowlist for headless runs.** The permission set for unattended runs
   contains no `git commit`, no `git push`, no destructive verbs. Headless runs can't
   prompt for more — so they cannot land changes, by construction.
2. **Stage, don't land.** Unattended agents write to a staging area — an inbox
   directory, staged-but-uncommitted files, a proposals document — and describe what
   they did and why.
3. **The human gate is a ritual.** Review staged work at a fixed moment (a morning
   review works well): approve → it lands; skip → archived. Batched, cheap, calm.
4. **Meter every run.** One ledger line per run (timestamp, job, exit code, duration).
   Watchdogs read the ledger — and a *different* job surfaces the failure than the one
   that failed. The watchers watch each other.

## The test of a real gate

> If the model turned hostile tonight, what could it actually do before morning?

Under this pattern: stage some files and write you a note. That's the whole blast
radius — and that answer comes from an allowlist, not from trust in a prompt.

## Composing the four pillars

The **gate** bounds what *lands*. The [**perimeter**](perimeter.md) bounds what
*leaves*. [**Receipts**](receipts.md) bound what's *believed*.
[**Drills**](drills.md) bound how the whole thing *decays*. An unattended agent under
all four can read broadly, propose anything, leak nothing, change nothing, and get
more trustworthy every time it fails.

Full pattern: [`conventions/stage-only-autonomy.md`](https://github.com/YOUR-GITHUB-USER/nambikkai/blob/main/conventions/stage-only-autonomy.md)
