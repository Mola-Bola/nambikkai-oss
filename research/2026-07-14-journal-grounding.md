# Nambikkai journal — grounding notes (science · market · data · law)
_First research pass, 2026-07-14 (Cowork thinkpad). Feeds the reflection-loop voice, the
distress thresholds, and the data-sourcing stone. Web-sourced; links at each claim._

## 1 · The science the product stands on

**Affect labelling — capture IS the intervention.** Naming a feeling in words dampens amygdala
reactivity and recruits prefrontal regulation (visible on fMRI); journaling is one of the most
effective practice formats because writing forces precision. ([Torre & Lieberman 2018](https://journals.sagepub.com/doi/10.1177/1754073917742706);
[neural evidence](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3970015/)) → The schema
(what you feel · why · who/what · what you think of it) isn't just data collection — filling it
in is itself regulating. Design the capture prompt to invite a *specific* label, not "bad".

**Emotion granularity.** Finer-grained emotion vocabulary predicts better regulation (Feldman
Barrett's constructionist work). → The ledger should gently grow the user's vocabulary over time
("last month this was 'stressed'; today it reads closer to 'resentful' — different thing?").

**Expressive writing — real but modest effects, and the moderators matter.** Meta-analyses
(RCTs through mid-2025): small effects on depression (g≈0.31) and grief (g≈0.39) — but **more
sessions (g≈0.58) and feedback (g≈0.68) roughly double it**. ([PMC meta-analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC10415981/);
[depression meta-analysis](https://www.researchgate.net/publication/349908406_Effects_of_expressive_writing_on_depressive_symptoms-A_meta-analysis))
→ Two product implications: consistency beats intensity (the habit tracker and the journal are
one loop, not two features), and **the reflection loop is the "feedback" moderator** — the thing
that doubles the effect. That's the moat, scientifically.

**Rumination vs reflection — the danger to design against.** First-person, immersed "why did
this happen TO ME" re-triggers the feeling and predicts worsening (brooding); **self-distanced**
processing (third person, temporal distance) enables cool reflection without re-activation
([Kross, Ayduk & Mischel 2005](https://journals.sagepub.com/doi/abs/10.1111/j.1467-9280.2005.01600.x);
[processing-mode + self-distancing review](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.01943/full)) →
- Reflection voice nudges distance: "when [role] said that, you believed…" not "relive it".
- **Threshold heuristic v0 (owner-calibrated later):** same trigger recurring + negativity rising
  + no belief-revision across N entries = brooding loop → gentle intervention (suggest distance,
  a walk, a human), never a deeper probe.
- The already-logged "third-person narrative timeline (Uzzzz)" task IS a self-distancing tool —
  fold it into the product rather than a one-off.

**Appraisal theory — why bitemporal provenance fits feelings.** Emotions arise largely from
appraisals (what you *believed* about the event/person), and revising the appraisal revises the
feeling. The truth ledger is literally an appraisal ledger with valid-from/valid-to — "what I
believed then" vs "what I know now" is reappraisal with receipts. This is the theoretical spine
of the whole product; no competitor found builds on it.

**Habits.** Context-cue-anchored, tiny increments (Wood; Fogg's tiny-habits pattern); gamify
carefully — streaks motivate but streak-guilt punishes the struggling user the product exists
for. Reward *returning after a gap* at least as much as the streak.

## 2 · Market (2026 scan)
Leaders: **Rosebud** (chat-based "mentor in your pocket", $6M Bessemer, memory system,
therapist-designed workbooks), **Mindsera** (mental-models thinking partner — reviews call its
tone formal/clinical, "better for thinking about thoughts than feeling them"), Reflection.app,
Day One + a long tail. ([comparison](https://www.reflection.app/blog/ai-journaling-apps-compared);
[Rosebud](https://www.rosebud.app/); [Mindsera](https://mindsera.com/)) Both leaders are
cloud-hosted; both market encryption; neither offers belief-revision provenance or local-first.
**Nambikkai's open ground:** (1) the truth/appraisal ledger over time — nobody does "what you
believed then vs now"; (2) genuine privacy architecture (local-first spine, people-by-role,
identity non-retention) vs marketing-grade encryption claims; (3) warm + gentle where Mindsera
is clinical, structured where Rosebud is chatty.

## 3 · Law & positioning (matters even at MVP)
Illinois's **WOPR Act** (Aug 2025) and Nevada ban AI that claims to provide therapy/mental-health
treatment; wellness/journaling apps sit in a grey borderline the statutes don't resolve.
([Baker Donelson](https://www.bakerdonelson.com/illinois-passes-extensive-law-regulating-ai-in-behavioral-health);
[state-regulation overview](https://www.blueprint.ai/blog/breaking-down-current-legislation-regulating-ai-in-mental-health-care))
→ Rules for us: Nambikkai is a **journal, never therapy** — no diagnostic language, no treatment
claims, anywhere (copy, docs, replies). High-distress threshold behaviour = warm suggestion of
human support, never AI counselling. This aligns with, not against, the gentle-voice decision.

## 4 · Real-human data sources (owner note 2026-07-14: "more sources from actual humans")
Ethically usable research corpora, roughly in order of fit:
- **ISEAR** (~7.6k self-reported "situations in which I felt X" across 7 emotions) — closest
  shape to our schema: feeling + antecedent event.
- **Covid-ED** — crowdsourced *emotion diaries* labelled with emotion/empathy/personality; PII
  excluded by design. Closest to real journal entries.
- **GoEmotions** (58k Reddit comments, 27 fine-grained emotions) — trains granular labelling.
  ([paper](https://aclanthology.org/2020.acl-main.372/); [Google blog](https://research.google/blog/goemotions-a-dataset-for-fine-grained-emotion-classification/))
- **EmpatheticDialogues** (~25k emotion-grounded conversations) — grounds the *reflection voice*:
  what empathetic responding looks like turn-by-turn.
- **CLPsych / Reddit mental-health corpora** — powerful but access-restricted under data-use
  agreements; pursue only if/when a real calibration need justifies the paperwork.
- Published memoirs/essays/public journals (Pepys→modern) — voice and pattern grounding, not
  classifier training.

**Ethics gate (binding):** licensed research corpora and explicitly-published material only — no
scraping personal blogs/socials; data calibrates classifiers, thresholds, and voice, and is never
regurgitated into any user's reflections; user entries (including the owner's) never leave the
local spine for training. This resolves the previously-logged open question "how to source user
data ethically" for the journal context.

## Next stones this feeds
1. Reflection-voice spec (gentle-suggestive + self-distancing nudges + granularity growth).
2. Threshold design v0 (brooding-loop heuristic above), calibrated on the owner.
3. Capture-schema finalisation for the `journal:` prefix.
4. Corpus acquisition (ISEAR + GoEmotions + EmpatheticDialogues first) behind the ethics gate.
