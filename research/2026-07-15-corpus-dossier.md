# Corpus dossier — timestamped real-human journals, feelings & findings
_Deep-research pass, 2026-07-15 (Cowork, Fable). Charter: `(internal note, not published)`.
Extends (does not redo) `2026-07-14-journal-grounding.md`. Ethics gate binding throughout:
licensed corpora / public domain / formal access programmes only; no scraping personal blogs or socials._

Ranking criteria (charter order): timestamped → longitudinal per-person → revision structure → ethically usable → schema fit (feeling · trigger · person/context · belief).

---

## A · Experience-sampling / daily-diary science — the "wider surface"

### 1. openESM ⭐ (biggest find of this pass)
- **What:** harmonised database of openly available experience-sampling datasets, launched late 2025. Search metadata at openesmdata.org; download via R (`openesm`, on CRAN) or Python packages; data stored in a Zenodo community with DOIs. ([preprint](https://osf.io/preprints/psyarxiv/qfdtb_v1) · [announcement](https://jonashaslbeck.com/OpenESM/) · [CRAN](https://cran.r-project.org/web/packages/openesm/index.html)) [src: web 2026-07-15]
- **N:** 60 datasets · >16,000 participants · >740,000 observations (growing).
- **Timestamp/revision:** fully timestamped, multiple pings/day or daily, per-person time series — exactly the longitudinal-per-person shape. No revision structure.
- **Licence/access:** open; per-dataset licences surfaced by the package ("ensures proper citation and license compliance"). Verify each dataset's licence at pull time.
- **Ethics gate:** ✅ PASS — purpose-built open research data.
- **Schema fit:** feeling (Likert affect items, not free text) + timestamp always; trigger/context in some datasets (event-contingent designs); person-role rarely; belief no.
- **Acquisition:** `install.packages("openesm")` → browse metadata → pull matching datasets. Hours, not weeks.
- **Size:** hundreds of MB total at most; individual datasets small.

### 2. NSDE (National Study of Daily Experiences, MIDUS)
- **What:** largest, longest-running public daily-diary study in the US — 8 consecutive days of phone-interview diaries (stressors via DISE inventory, emotions, physical symptoms), repeated in 3 bursts ~9 years apart across 20+ years. ([protocol](https://www.researchprotocols.org/2025/1/e76453) · [20-year paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9993073/) · [NSDE lab](https://sites.psu.edu/nsde/)) [src: web 2026-07-15]
- **N:** 3,510 adults (24–97) · >42,000 diary days.
- **Timestamp/revision:** daily timestamps; per-person 8-day runs; *same people re-measured a decade later* — the closest a big-N dataset gets to long-horizon revision (of affect patterns, not of stated beliefs).
- **Licence/access:** public access programme via MIDUS Colectica portal and ICPSR/NACDA (e.g. [MIDUS 3 Daily Diary, ICPSR 38529](https://www.icpsr.umich.edu/web/NACDA/studies/38529)). Registration + terms of use; standard, real paperwork — fine to do, per gate.
- **Ethics gate:** ✅ PASS (formal access programme).
- **Schema fit:** feeling (structured scales) + trigger (stressor type, who was involved — so person/context partially!) + time. Belief: appraisal items only (severity, control). No free text.
- **Acquisition:** ICPSR/Colectica account → download public-use files. Days.
- **Size:** tens of MB per wave (tabular).

### 3. EMOTE database
- **What:** open-access, searchable, cumulative repository of experience-sampling data on daily emotional functioning (FEEL Lab, University of Melbourne). ([about](https://emotedatabase.com/about/) · [FEEL Lab](https://psychologicalsciences.unimelb.edu.au/research/research-initiatives/our-work/feel-research-lab)) [src: web 2026-07-15]
- **N:** cumulative, varies by contributed study — enumerate on site at acquisition time.
- **Timestamp/revision:** timestamped ESM pings per person; no revision structure.
- **Licence/access:** open access; check per-study terms. Overlaps with openESM — dedupe.
- **Ethics gate:** ✅ PASS. **Schema fit:** as openESM.
- **Acquisition/size:** browse + download; small.

Also noted, minor: [Qwantify app dataset (OSF)](https://osf.io/sxfrx/) — desire/emotion/well-being ESM, open; [DAPPER](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8239004/) — ESM + physiology. Both pass the gate; pull via openESM/OSF if the harmonised sets leave gaps.

---

## B · Shortlisted corpora — verified

### 4. ISEAR
- **What:** International Survey on Emotion Antecedents and Reactions (Scherer & Wallbott, 1990s) — self-reported "a situation in which I felt X" + appraisal questions, ~3,000 respondents across 37 countries. ([UNIGE research material](https://www.unige.ch/cisa/research/materials-and-online-research/research-material) · [JULIELab mirror](https://github.com/JULIELab/ISEAR/blob/master/README.md)) [src: web 2026-07-15]
- **N:** 7,665 statements · 7 emotions (~1,095 each) · ~3,000 people.
- **Timestamp/revision:** ❌ none — one snapshot per memory; not longitudinal.
- **Licence/access:** distributed free by the Swiss Center for Affective Sciences (UNIGE); explicit research licence text not surfaced — confirm terms on the UNIGE page at download.
- **Ethics gate:** ✅ PASS (consented research corpus).
- **Schema fit:** ⭐ best free-text fit — feeling + trigger + appraisal (a belief-adjacent field). Person/context often embedded in the text.
- **Acquisition:** direct download from UNIGE. Minutes. **Size:** ~2 MB.

### 5. Covid-ED — important correction to yesterday's note
- **What:** COVID-19 Emotion Diary with empathy/Theory-of-Mind ground truths — crowdsourced pandemic diaries, expert-reviewed annotations. **It is a Korean-language corpus** (Seoul National University), which yesterday's shortlist didn't flag. ([GitHub](https://github.com/humanfactorspsych/covid19-tom-empathy-diary) · [paper](https://escholarship.org/uc/item/950900w7)) [src: web 2026-07-15]
- **N:** 19,025 diary documents · 3,805 Korean residents · Oct–Dec 2020 (≈5 entries/person — genuinely longitudinal per-person).
- **Timestamp/revision:** dated entries over ~3 months; no revision structure.
- **Licence/access:** CC-BY-NC-SA 4.0, **but train split restricted to researchers at verified institutions** (privacy) — access by email request to the dataset maintainers (address in the upstream README). As an individual builder, expect friction or refusal.
- **Ethics gate:** ✅ PASS in principle (consented, PII-excluded), but the verified-institution DUA is the CLPsych problem in miniature — park unless translated Korean data is worth the paperwork.
- **Schema fit:** feeling + free-text trigger/context + empathy/ToM labels; language mismatch for an English-voice product.
- **Acquisition:** email request → likely partial (test/val) access. Weeks, uncertain. **Size:** ~40k sentences.

### 6. GoEmotions
- **What/N:** 58k Reddit comments, 27 fine-grained emotions + neutral. ([HuggingFace](https://huggingface.co/datasets/google-research-datasets/go_emotions)) Repo under Apache 2.0. [src: web 2026-07-15]
- **Timestamp/revision:** ❌ none usable; single comments, no per-person series.
- **Ethics gate:** ⚠️ CONDITIONAL PASS — a published research release (not our scraping), but it *is* Reddit text; use for granular-label classifier training only, never as "journal" exemplars, never regurgitated.
- **Schema fit:** feeling label + text; no trigger/person/belief structure.
- **Acquisition:** `load_dataset("google-research-datasets/go_emotions")`. Minutes. **Size:** ~50 MB.

### 7. EmpatheticDialogues
- **What/N:** ~25k emotion-grounded conversations (Facebook AI); CC-BY-NC 4.0; on HuggingFace. [src: 2026-07-14 grounding note; availability re-confirmed via HF 2026-07-15]
- **Timestamp/revision:** ❌. **Ethics gate:** ✅ PASS (crowd-worker consented).
- **Schema fit:** none of the four fields as data — its value is the *reflection voice* (empathetic turn-taking), as yesterday's note said.
- **Acquisition:** HuggingFace. Minutes.

### 8. Vent dataset
- **What:** largest emotion-annotated social dataset — posts from the Vent app, each self-tagged from a 705-emotion / 63-category taxonomy. ([paper](https://arxiv.org/abs/1901.04856) · [Zenodo](https://doi.org/10.5281/zenodo.2537838)) [src: web 2026-07-15]
- **N:** 33M posts · ~1M users — with per-user timelines: timestamped AND longitudinal per-person at scale, which nothing else on this list matches for free text.
- **Timestamp/revision:** ✅ timestamps + per-person series; no revision structure.
- **Licence/access:** metadata (everything except text) public on Zenodo; **text file is restricted-access, upon request** to the authors.
- **Ethics gate:** ⚠️ CONDITIONAL — the restricted-access request route is a formal programme (fine to pursue); but this is social-app venting by users who never wrote for research. If granted: calibrate label taxonomies and emotion-dynamics statistics only; never train the voice on it, never quote it. Decide deliberately before requesting.
- **Acquisition:** pull metadata now (dynamics stats need no text!); optionally email authors for text. **Size:** metadata ~GBs.

### 9. LiveJournal mood-annotated corpora (Mishne et al.)
- **What/N:** ~815k–8M blog posts with self-selected mood tags, scraped mid-2000s for the MoodViews work. ([MoodViews](https://www.icwsm.org/papers/5--Mishne-Balog-de-Rijke-Ernsting.pdf)) [src: web 2026-07-15]
- **Licence/access:** no maintained distribution found; would require re-scraping or grey-market copies.
- **Ethics gate:** ❌ FAIL — scraped personal blogs, no consent, no formal access route. **Drop from the shortlist.**

### 10. CLPsych shared-task corpora
- **Status per charter:** noted, not chased. Access is per-task DUA (e.g. [CLPsych 2022 longitudinal "moments of change"](https://aclanthology.org/2022.clpsych-1.16/) — Reddit timelines with change-point annotations, conceptually the closest public thing to *within-person turning points*). DUA generally requires institutional affiliation. Revisit only with a concrete calibration need. [src: web 2026-07-15]

---

## C · Public-domain diaries & letters — deep time

### 11. Pepys diary
- **What:** 9.5 years (1660–1669) of near-daily entries, one person; Project Gutenberg plain text (1893 Wheatley edition), copyright-free. ([Gutenberg #4200](https://www.gutenberg.org/ebooks/4200) · [pepysdiary.com text notes](https://www.pepysdiary.com/about/text/)) [src: web 2026-07-15]
- **N:** 1 person · ~3,100 dated entries — the densest single-person timestamped series available at zero cost.
- **Ethics gate:** ✅ PASS (public domain). **Schema fit:** feeling/trigger/person all in prose (extraction needed); belief occasionally explicit. 17th-century register limits voice use; excellent for *pattern* extraction tests (recurring triggers, named-person co-occurrence with mood).
- **Acquisition:** download; pepysdiary.com's per-entry structure makes date-parsing trivial. Minutes. **Size:** ~10 MB.

### 12. Orwell diaries, Gutenberg diaries/correspondence, WWI/WWII archives
- Orwell: public domain in UK/EU since 2021 (life+70); US status varies by publication — check per-text before use. Gutenberg hosts many lesser-known dated diaries and letter collections (search "diary" in the catalogue) — same PASS profile as Pepys, more voices, variable density. WWI/WWII diary digital archives are numerous but access terms vary per archive; treat each as its own gate check. [src: web 2026-07-15, partial — per-text verification at acquisition]

### 13. Mass Observation Archive (incl. COVID-19 collection)
- **What:** UK everyday-life writing since 1937; COVID collection = directive responses, personal diaries, 12th May day-diaries, Mar 2020–Autumn 2021; Wellcome-funded database gives researchers search access to ~10,000 documents. ([COVID collection](https://massobs.org.uk/research/covid19/) · [researcher access note](https://massobs.org.uk/2025/03/24/mass-observation-covid-19-collection-what-does-it-mean-for-researchers/)) [src: web 2026-07-15]
- **Timestamp/revision:** dated; some writers respond for *decades* (long-horizon per-person). Directive design = same prompt to many people (great width).
- **Licence/access:** formal programme; trustees' permission needed to use/publish extracts; copyright cleared per-contributor. Not bulk-downloadable.
- **Ethics gate:** ✅ PASS via the programme — but access model suits scholarship, not corpus ingestion. Use as *reading/grounding*, not training data.
- **Acquisition:** apply to MOA (University of Sussex). Weeks–months; probably not worth it for MVP.

---

## D · Revision structure — the honest answer

**Nearly nothing exists as a usable dataset.** The closest things found:

1. **Anne Frank, The Critical Edition (1987/2003)** — the single best-documented case of a diarist revising her own diary: Anne's original entries (version A) printed alongside her own in-hiding rewrite (version B), differences documented passage-by-passage. ([Anne Frank House on the two versions](https://www.annefrank.org/en/anne-frank/diary/two-versions-annes-diary/) · [Wikipedia](https://en.wikipedia.org/wiki/The_Diary_of_a_Young_Girl)) In copyright — a **design reference** for what revision structure looks like, not a corpus. [src: web 2026-07-15]
2. **Diary-interview method studies** — the qualitative-health-research design where follow-up interviews have participants revisit their own diary entries is established methodology ([overview](https://academic.oup.com/fampra/article/39/5/996/6574305)), so the *structure* exists in science — but the underlying transcripts are almost never shared (privacy). Findings papers are citable; data is not acquirable. [src: web 2026-07-15]
3. **CLPsych 2022 "moments of change"** (§10) — change-points annotated by third parties, not self-revision; nearest labelled proxy.
4. Republished annotated diaries (e.g. Emilie Davis's Civil War diaries) are annotated by *editors*, not the author-later — fails the definition. Politician/artist diaries with retrospective footnotes (Benn, Palin genre) exist but are in copyright and anecdotal in structure.

**Conclusion:** the bitemporal, self-revised feelings ledger effectively **does not exist in public data**. Nobody else has this — which cuts both ways: it's the moat, and there is no external corpus to calibrate revision-detection against. The owner's own re-reads are, and will remain, the only ground truth for v0.

---

## E · Findings literature — numbers for thresholds (extends §1 of the 2026-07-14 note)

- **Emotion-dynamics meta-analysis** ([Houben et al. 2015](https://ppw.kuleuven.be/okp/_pdf/Houben2015TRBST.pdf)): higher variability (within-person SD), instability (MSSD), and inertia (autocorrelation) all correlate with lower well-being / more depressive+anxious symptoms. These are the three statistics a threshold engine should compute per user.
- **Caution:** newer EMA work is mixed on inertia — some studies find no prospective association with depressive symptoms once mean affect is controlled ([mood-reactivity review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12837089/) · [NA-instability study](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1371115/full)). Instability of negative affect looks more robust than inertia. [src: web 2026-07-15]
- Practical read: thresholds should key on **within-person change from own baseline** (rising NA instability + recurring trigger + no belief-revision), not population cutoffs — consistent with the brooding-loop heuristic v0 already drafted.

---

## Top-5 recommended acquisitions (effort-ranked, cheapest first)

1. **openESM** — one R/Python call away; 60 datasets, 16k people, timestamped per-person series; licence handling built in. *This is the "wider surface" in a box.*
2. **ISEAR** — instant download; the best feeling+trigger+appraisal free-text fit; small enough to hand-inspect fully.
3. **Pepys (+ 2–3 more Gutenberg diaries)** — free, public domain, dense per-person timelines for pattern-extraction prototyping.
4. **GoEmotions + EmpatheticDialogues** (bundle, both on HuggingFace) — granular-label training and voice grounding respectively; conditional-use rules from the ethics gate apply to GoEmotions.
5. **NSDE/MIDUS public-use files** — registration paperwork, then the gold-standard N for stressor→affect dynamics; feeds thresholds, not voice.

Deliberate non-acquisitions: Vent *text* (decide-later; pull free metadata for dynamics stats if wanted), Covid-ED (Korean + institution-gated), Mass Observation (scholar-access model), CLPsych (DUA, no current need), LiveJournal (ethics FAIL — dropped).

## Three design implications for the reflection loop / thresholds

1. **Thresholds must be within-person, and humble.** The literature's strongest signals (variability/instability/inertia) are within-person statistics, and even inertia's evidence is mixed. Population data (openESM, NSDE) sets *priors and plausible ranges* only; the trigger condition stays "change against own baseline," owner-calibrated, and v0 should fire conservatively.
2. **No corpus covers the full schema — so compose, don't train end-to-end.** Feeling+trigger lives in ISEAR; feeling+time+person-series lives in ESM data; empathetic responding lives in EmpatheticDialogues; **belief is nowhere**. Belief extraction will have to be LLM/few-shot with owner-graded examples, not corpus-trained — plan the calibration set accordingly.
3. **Revision structure must be captured natively from day one, because it can't be bought.** Since no external data exists to calibrate revision-detection, the ledger schema (valid-from/valid-to, "what I believed then") must make every owner re-read/correction a clean labelled event — the product manufactures the dataset that D shows the world doesn't have. Anne Frank's A/B versions are the design north star for what a self-revision diff should record: what changed, when, and in what direction.

---
_⚠ Per charter: nambikkai repo git may be locked (stale index.lock) — file written, commit deferred. Nothing else touched._
