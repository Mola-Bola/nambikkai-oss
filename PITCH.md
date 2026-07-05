# Nambikkai — the pitch
_One page. For maintainers, adopters, and the skeptical._

## The observation

Personal agent systems won. Folder-of-markdown OSes (PAI, LifeOS, and kin) give an AI
durable memory of a human life: money, health, family, plans. The category is racing on
capability — more skills, more agents, more autonomy.

Nobody is racing on trust. The systems that read your mail and hold your medical
history mostly protect it with a paragraph in a system prompt.

## The thesis

**Trust is a component, not a feature.** Like auth, it should be something you install,
not something you write. In systems-of-systems terms: everyone is building airports —
ticketing, baggage, control towers. Nambikkai is the security checkpoint, built once,
composable into any airport.

## The mechanism (why it's defensible)

1. **Perimeter placement.** Detection libraries (Presidio, llm-guard) work only where
   an app remembers to call them. Nambikkai wires enforcement into the agent harness's
   hook layer — every file write, shell command, and MCP payload passes the gate, and
   forgetting is not possible. The block is an exit code, not a suggestion.

2. **The corpus moat.** One golden test corpus binds every implementation across
   languages and runtimes. It asserts its own false positives (`known_overmatch`) and
   publishes its own blind spots (`known_gap`). Competitors ship code; we ship code
   chained to an honest, growing test bed.

3. **The contribution flywheel.** The `incident-to-eval` ritual turns every user's
   real-world failure into a synthetic corpus case. Community incidents grow the
   corpus; the corpus hardens every port; PRs are cases, not opinions. No guardrails
   project works this way.

4. **Receipts as a convention.** The `[src | date | tier | ttl]` provenance tag makes a
   markdown knowledge base auditable — which facts are firm, which are hunches, which
   have expired. Formalized in research (bi-temporal memory); absent in practice.
   Nambikkai ships it as a spec plus a lint.

## Proof it's real

Extracted from a production personal life-OS where it runs daily: the gate has blocked
live leaks (including, memorably, this project's own test file), the corpus replays
every past incident on every run, and nightly headless agents operate under
stage-only autonomy — mechanically unable to commit without the owner's morning gate.

## The ask

- **Adopters:** install the plugin into your PAI/LifeOS/homegrown system. It takes 90
  seconds and refuses your national ID by lunch.
- **Maintainers:** one integration conversation. Nambikkai is deliberately a cog —
  it makes your OS more shippable to people who hesitate at the trust question.
- **Contributors:** bring incidents. A failure with a shape is a corpus case; a corpus
  case is a permanent fix for everyone.

## The team

The Nambikkai authors — currently one human (systems background in observability and security platforms) and
their agents, building in the open from a system they actually live in.

*நம்பிக்கை — trust, faith, hope. We picked a word that has to be earned.*
