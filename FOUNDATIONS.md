# Foundations audit — what's in, what's missing, what to skip (2026-07-18)

_Research pass: two web-research agents over the mid-2026 local-first / solo-builder landscape,
checked against this repo's actual state (M2 committed, M3 in flight). Sources linked._

## Already incorporated (and validated as correct by the research)
- **FastAPI + React/Vite localhost MVP** — still the mainstream 2026 shape for this exact case;
  highest AI-codegen fluency; upgrades cleanly to packaging (below). No change needed.
- **Append-only chained JSONL ledger + derived views** — textbook event-sourcing pattern; also
  the easiest E2E-sync primitive for the future (encrypted blob sync of an append-only log).
- **Golden-corpus test culture + GitHub Actions CI** — ahead of most solo repos; keep.
- **ADRs** (001 tiered architecture, 002 identity policy) + living VISION/CLAUDE/charter docs.
- **data/ gitignored** — user words never enter git. Verified.

## Add NOW (ordered by leverage)
1. **Session state + handoffs (the gap you asked about):** STATUS.md (short, overwrite-in-place)
   + docs/handoffs/ per-session notes + a session-close rule in CLAUDE.md ("commit or write a
   handoff before ending — never leave silent dirty state"). Scaffolded alongside this doc.
   Heavier option if this ever feels thin: Beads (git-backed agent task ledger,
   github.com/steveyegge/beads).
2. **Localhost hardening — privacy brand demands it:** bind 127.0.0.1 only + a per-session token
   on every API call. Any local process or malicious webpage can poke open localhost ports
   (DNS-rebinding/CSRF class). Small change, do it before more features.
3. **Python toolchain consolidation:** uv (pyproject.toml + uv.lock, drop requirements.txt) +
   ruff (lint+format, rules E/F/I/UP/B/SIM) + pre-commit (whitespace, ruff). uv is the 2026
   consensus default. One `uv run pytest` command that runs everything incl. the corpus.
4. **Backup + restore for data/:** nightly copy of the JSONL dir (+ `VACUUM INTO` once SQLite
   views exist); test restore ONCE and write the procedure down. Currently journal entries have
   no backup story at all in this repo (life-os's vault no longer covers this path automatically —
   verify or add it to backup_vault.sh's include set).
5. **Engine spec + golden vectors freeze:** write the ledger/hash-chain/redaction spec as a doc
   with test vectors. This is cheap insurance: mobile packaging will eventually force a
   Rust/TS engine port (see below), and a frozen spec makes it mechanical, not archaeology.
6. **Typed API client:** generate the TS client from FastAPI's OpenAPI schema instead of
   hand-writing api.ts — kills a whole drift class between backend and frontend.

## Add at the RIGHT moment (not now)
- **UI pass (M7):** Tailwind v4 (CSS-first config, no tailwind.config.js) + shadcn/ui — NOTE:
  since July 2026 fresh shadcn scaffolds default to Base UI primitives, not Radix; ignore
  pre-2026 tutorials. Vitest units + 3–5 Playwright smoke flows added to the existing CI job.
- **Packaging (post-MVP):** PyInstaller single binary ("download, double-click") → Tauri v2
  desktop with FastAPI as a sidecar — proven pattern, NO rewrite for desktop. Mobile is what
  forces the engine port (Tauri sidecars don't run on iOS/Android) — hence item 5 above.
- **CHANGELOG automation:** conventional commits (already ~in use) + git-cliff when releases start.
- **Local AI features (reflection loop era):** sqlite-vec + local embeddings for
  "chat with your journal" fully offline; steal patterns from Reor and Khoj (both local-first
  PKM, both validate that this category settled on self-host/local).
- **Multi-device sync (later):** DIY encrypted-blob sync of the ledger over dumb storage;
  re-evaluate Evolu (E2E-first, 2025 rewrite, shipping) and Automerge 3 then.
- **Social tier (much later):** separate server-readable stack — Zero 1.0 (stable June 2026) or
  ElectricSQL + TanStack DB — deliberately firewalled from the private core per ADR 001.

## Do NOT add (solo local MVP — research-confirmed dead weight)
Docker/k8s · CI matrices (one job, one OS) · telemetry/Sentry · i18n · state-management libs
(React Query + local state suffices) · monorepo tooling · auth/user accounts · Storybook ·
GraphQL · release-please/Renovate. Revisit only at second user or second contributor.

## Key sources
uv/ruff/pytest consensus: pydevtools.com/handbook · Vite 8 (Rolldown): vite.dev/blog/announcing-vite8 ·
shadcn Base-UI default: ui.shadcn.com/docs/changelog/2026-07-base-ui-default · Tauri sidecar:
v2.tauri.app/develop/sidecar (mobile gap: tauri#9774) · SQLite ops: jvns.ca 2026-07-17 ·
localhost attack class + single-origin serving: davidmuraya.com/blog, arlaf.com/en/blog/ui-web-local ·
Evolu: evolu.dev · Automerge 3: automerge.org/blog/automerge-3 · Zero 1.0: infoq.com/news/2026/06/zero-version-1 ·
Beads: steve-yegge.medium.com/introducing-beads
