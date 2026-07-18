# ADR 002 · Identity policy: user's choice locally, roles enforced at egress

- **Status:** accepted (owner decision 2026-07-17, T1; recorded 2026-07-18)
- **Binds:** journal schema (M2+), persona model (M3), import (M4), every export path.

## Context

The engine's doctrine is people-by-role / identity non-retention — born from the
builder's own privacy bar for a dev-tool perimeter. A journal is different: it lives
on the user's own device, and forcing aliases on someone writing about their own
mother is paternalism, not privacy. The two positions collided as tension T1.

## Decision

**On the device, identity is the user's choice.** The UI suggests an alias first
(nickname, role, initial — their pick), but real names are allowed everywhere in the
journal tables. No warnings, no nagging.

**At egress, roles are enforced — always.** Anything leaving the device (exports,
shares, any future tier-2 surface per ADR 001) passes the redaction gate, and
name-bearing fields are swapped to the persona's alias/role before crossing.

Mechanically, the engine gains a **per-field policy** on journal tables:

| Policy | Meaning | Example fields |
|---|---|---|
| `local-free` | Any content, names included; never transmitted raw | entry body, truth text, persona display name |
| `egress-role` | On any export, value is replaced by alias/role mapping | persona references inside exported entries |

The old identity non-retention rule **still binds engine and dev surfaces**: no real
names in logs, fixtures, goldens, corpus data, or test output — those are not the
user's device-private space.

## Consequences

- Persona records carry both a display name (user's choice) and an alias/role used
  for egress; the mapping lives only on-device.
- Export is a pipeline stage, not a file copy — it must run the gate. A golden test
  (M7 battery) proves a named export comes out role-swapped.
- UI copy stays layman (VISION · Audience & voice): "Use their real name or a
  nickname — either way it never leaves this device." The word "egress" appears in
  docs like this one, never on a screen.
