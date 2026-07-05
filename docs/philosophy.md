# Philosophy

## The axiom

Models generate cheaply; **verification is the scarce resource.** Every capability an
agent system adds must name its verifier before it ships — a gate, a lint, an
approval, or an eval. Unverified capability is debt.

Everything in Nambikkai is that axiom applied four ways: receipts verify *beliefs*,
the perimeter verifies *outputs*, drills verify *the guards themselves*, and the gate
verifies *actions*. Nine working rules fall out of it — the full doctrine lives in
[`conventions/doctrine.md`](https://github.com/YOUR-GITHUB-USER/nambikkai/blob/main/conventions/doctrine.md).
Three deserve expansion:

## Defaults over discipline

When a fault is found, encode the fix where nobody has to remember it — a hook, a
config default, an allowlist. Per-decision vigilance is not a control; it's a
countdown. This is why Nambikkai is a *hook*, not a checklist, and why the override
is an environment variable that announces itself rather than a rule you're trusted
to follow.

## Honest limits, published

Every guard documents what it cannot see and where it over-triggers — and the test
suite **asserts both**, so the documentation cannot drift from reality without a test
failing. A blind spot you publish is debt; a blind spot you hide is a betrayal. We'd
rather ship a smaller guard that's honest than a bigger one that's marketing.

## A cog, not a kingdom

Systems thinking distinguishes a **system of systems** — independent, task-oriented
systems pooling capability — from a monolith. The agent-OS ecosystem is becoming the
former: your OS, your connectors, your models, your rituals. Nambikkai chooses to be
one excellent component in that composition rather than another kingdom. The trust
layer is the piece that *most* needs to be shared infrastructure — trust rules that
differ per-OS are trust rules nobody audits.

## Provenance, all the way down

This project was extracted from a production personal life-OS where every one of these
mechanisms runs daily — the incidents in the corpus shaped the rules, the gate blocked
this project's own files during development, and the doctrine was paid for, rule by
rule, before it was written down.

*நம்பிக்கை — trust, faith, hope. A word that has to be earned.*
