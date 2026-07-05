# The trust doctrine

How Nambikkai thinks about building trustworthy agent systems. Distilled from running
one in production; every rule below was paid for by a real incident or audit finding.

## The axiom

Models generate cheaply; **verification is the scarce resource.** Every capability an
agent system adds must name its verifier before it ships: a gate, a lint, an approval,
or an eval. Unverified capability is debt.

## Rules

### 1 · Verification over generation
Every loop ends in a check, not in output. A new agent loop without a named verifier
doesn't ship.

### 2 · Test the guard the day you build it
Safety-critical code gets a golden corpus **the same session it's written** — never
"later". Every incident becomes a permanent corpus case the day it's resolved. A guard
without a corpus is a hope, not a guard.

### 3 · Threat-model surfaces once, not per-incident
When a new data surface opens (a table, a channel, an agent return path), enumerate
**all** leak paths up front — chat transcript · tracked files · cloud rows · LLM
payloads · sub-agent returns · logs — and apply the redaction posture to each before
first use. Reactive hardening costs one incident per surface; enumeration costs an hour.

### 4 · Exposure loses, and so does loss
Security has two failure modes: leak **and** loss. If your secrets store is excluded
from sync (correct), it lives on one disk — so backup is a first-class security
control, and cloud copies travel encrypted only.

### 5 · No fixture rendered as live
A dashboard showing demo data as if real teaches false confidence. Meter first,
visualize second; label samples as samples; fold them away when real data exists.

### 6 · Verify before destroying
Before any delete/overwrite/purge, read the target and confirm the premise that
justified the action. If evidence contradicts the label, stop and surface.

### 7 · Defaults over discipline
When a fault is found, encode the fix where nobody has to remember it — a hook, a
config default, an allowlist — never a rule someone must recall under load.
Per-decision vigilance is not a control.

### 8 · Propose-then-run, and actually let it run
Autonomy is granted through gates, never assumed — but the gate exists **so agents can
act**. A propose-then-run system where nothing ever runs unattended pays the cost of
the gate and throws away the benefit.

### 9 · Honest limits, published
Every guard documents what it cannot see (`known_gap`) and where it over-triggers
(`known_overmatch`), and the test suite asserts both. A blind spot you publish is debt;
a blind spot you hide is a betrayal.
