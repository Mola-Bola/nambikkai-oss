# Stage-only autonomy — the Gate pattern

Unattended agents should be **mechanically unable** to make permanent changes — not
promised, prevented. The pattern:

## The construction

1. **Headless runs get a reduced allowlist.** The permission set available to scheduled
   /unattended agent runs contains no `git commit`, no `git push`, no destructive
   verbs. In Claude Code this is the project allowlist; headless runs cannot prompt for
   more, so an unattended run *cannot* commit — by construction, not by instruction.
2. **Work is staged, not landed.** Unattended runs write to a staging area (an inbox
   directory, `git add` without commit, a proposals file) and describe what they did.
3. **The human gate is a ritual, not an interrupt.** The owner reviews staged work at a
   fixed moment (a morning review works well): approve → it lands; skip → it's archived.
   Approval is batched and cheap; nothing nags in real time.
4. **The run is metered.** Every unattended run appends one line to a run ledger
   (timestamp, job, exit code, duration). Watchdogs read the ledger: a missing or
   failing run is the *first line* of the next day's review, surfaced by a different
   job than the one that failed — the watchers watch each other.

## Why not just "human in the loop"?

Because a promise in a prompt degrades under model drift, prompt injection, and plain
bugs. An allowlist doesn't. The test of a real gate: *if the model turned hostile
tonight, what could it actually do before morning?* Under this pattern: stage some
files and write you a note.

## Composing with the perimeter

The gate bounds **what lands**; the Nambikkai perimeter bounds **what leaves**. An
unattended agent under both can read broadly, propose anything, leak nothing, and
change nothing — until a human says so.
