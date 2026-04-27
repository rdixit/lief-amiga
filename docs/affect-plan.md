# Lief Affect Integration — AMIGA-AAC Phase I Implementation Plan

> **Status:** v2 — 2026-04-26
> **Relation to v1:** v1 (`lief-affect-integration.md`, week of 2026-04-24) was a forward-looking design draft. None of its mechanism is in `app.js` yet. This v2 document fully absorbs v1's content, extends it into a phased plan, and supersedes it. v1 can be archived.
> **Scope:** Phase I implementation horizon (next ~8 weeks, through end of June 2026)
> **Owner:** Mike Pesavento (PezTek consulting)
> **Companion documents:** *State of Knowledge & Direction*; *Phase I Architecture* (reference); `monday-demo-update.md` (concrete build spec for the Sub-Phase 0 work)

---

## What this document is

This is the **core implementation plan** for integrating Lief affect signals into the AMIGA-AAC prediction pipeline over the remaining Phase I window. It supersedes the v1 design draft and is fully self-contained:

- absorbs v1's content (schemas, code, design intent) directly so v1 can be archived
- stages the work into five sub-phases tied to specific outcomes, including a Sunday-Monday build that is the v1 mechanism's first implementation
- adds parallel infrastructure (retrieval scorer with affect-categorical-prior) that will let the team evaluate alternatives to prompt-modulation with empirical comparison data
- adds baseline-normalization, confidence-weighting, and measurement plans that apply regardless of which integration mechanism is used
- adds an SLM (small-CPU-model) evaluation track that addresses closed-API/latency/IRB concerns at the model layer
- makes explicit what is Phase I scope vs. Phase II readiness

The Monday-2026-04-28 placeholder milestone is captured in detail in the companion `monday-demo-update.md` document, which is the concrete build spec for the Sunday work.

---

## Relation to v1 (full absorption)

The v1 doc was a forward-looking design draft authored by a previous Claude (Sonnet 4.6) acting in a similar engineering-advisor role. Reviewing `app.js` v6 against v1: **none of v1's affect mechanism is in the codebase yet.** No `liefState`, no widget, no `buildAffectSystemPrompt`, no `getAffectTemperature`, no BLE scaffold, no slider, no "Connect Lief" button. The current `predictWithAPI` uses a static prompt and `temperature: 0.3` hardcoded.

This means v1 is a **plan that has not been executed**, not a shipped mechanism that needs evolving. Reframing v1 this way changes how this v2 plan reads: Sub-Phase 0 (the Monday demo) is the work of *implementing v1 for the first time*, not extending an existing implementation. The companion `monday-demo-update.md` is a concrete build spec for that Sunday work.

This v2 plan absorbs v1's content directly. Specifically:

- **v1's `liefState` schema** — extended in v2 with confidence, baseline-relative HRV, and an `inferred_category_prior` slot for Sub-Phase D, but core fields (hrv, valence, source, lastUpdated) preserved
- **v1's quintile-to-valence mapping** — preserved as the Sub-Phase 0 placeholder; baseline normalization in Sub-Phase C replaces the population-relative `rmssd / 80` approximation
- **v1's emoji widget design** — preserved; `(simulated)` badge approach is the right call
- **v1's `buildAffectSystemPrompt(liefState)` and `getAffectTemperature(liefState)`** — these are the active Phase I prediction-coupling mechanism, implemented in Sub-Phase 0 and refined as baseline normalization (Sub-C) lands
- **v1's BLE scaffold (`connectLief`, `handleHRVData`)** — superseded by the cloned Lief mobile app shell approach (see Sub-Phase B) per Rohan's 2026-04-26 update. The v1 BLE code becomes unnecessary because the cloned shell handles BLE/byte parsing/reconnection. The v1 design effort there isn't wasted; it informed the integration shape, just at a different level of the stack.
- **v1's open-questions list** — preserved and updated in this v2 doc

What this v2 plan *adds* on top of v1:

- A phased structure: five sub-phases over 8 weeks, each tied to specific outcomes
- A parallel retrieval scorer (Sub-Phase A onward) that lets the team evaluate alternatives to prompt-modulation with empirical comparison data
- A baseline-normalization sub-phase (Sub-Phase C) that fixes v1's `rmssd / 80` placeholder
- An SLM exploration sub-phase (Sub-Phase E) addressing closed-API/latency/IRB concerns at the model-backend layer
- An explicit measurement plan tied to the team's layered evaluation framework
- The cloned-mobile-app-shell integration approach for BLE (Sub-Phase B), simpler than v1's raw Web Bluetooth path

### A direction this plan flags but does not commit to

The State of Knowledge document argues for moving the affect integration point from LLM-prompt modulation (v1's mechanism) to retrieval reranking. The reasoning, briefly:

1. *Affect-as-tone is hard to clinically validate.* Stressed minimally-verbal children are often trying to communicate a need or protest, not receive a calmer-sounding response. Modulating tone may not match what the user is trying to do.
2. *Affect-as-categorical-prior is more theoretically grounded.* The §2 formalism in the Phase I Architecture document treats affect as a Bayesian prior over communicative-act categories, which has a cleaner evaluation story.
3. *LLM-prompt coupling ties affect to the project's most fragile component* (closed API, latency, IRB exposure).

These are real concerns, but they are **not actionable in the next two months without more time spent in the literature and with the team's existing implementation**. This v2 document explicitly defers the decision: prompt-modulation is the active mechanism through Phase I (Sub-Phase 0 implements it; Sub-Phase C improves it with baseline normalization), the retrieval scorer is built as parallel infrastructure (Sub-Phase A) that can be evaluated against it (Sub-Phase D), and the question of whether to migrate the affect-coupling point gets revisited later — likely as part of Phase II planning, after Mike has had real time with the literature and the team has data from the layered evaluation framework to inform the choice.

> **Note on intellectual lineage.** v1 was authored by a previous Claude (Sonnet 4.6) acting in this same role; v2 is a Claude iteration revising another Claude's draft, with Mike as continuity. The architectural reframing argued above (retrieval-rerank vs. prompt-modulate) is a real disagreement between the two iterations; it is being held open deliberately rather than resolved by fiat in either direction.

---

## Architecture (Phase I)

```
┌─────────────────────┐     BLE Notifications (handled by cloned Lief mobile app)
│   Lief Device       │ ──────────────────────────────────►  Lief mobile shell
│  (HRV / stress)     │                                         │
└─────────────────────┘                                         ▼
                                                        affectState = {
                                                          hrv_raw, hrv_baseline_z,
                                                          valence, arousal,
                                                          confidence, source,
                                                          available_modalities,
                                                          inferred_category_prior  // for Sub-D
                                                        }
                                                                │
                          ┌─────────────────────────────────────┤
                          ▼                                     ▼
                   Emoji Widget                      Prediction Pipeline
                   (valence + confidence            ┌────────────────────────┐
                    visible, "(simulated)" or      │ PRIMARY: LLM call with │
                    "(low confidence)" badge)      │ affect-modulated       │
                                                   │ system prompt + temp   │
                                                   │ (v1 mechanism, kept)   │
                                                   │                        │
                                                   │ Backend: GPT-4o-mini   │
                                                   │ now; SLM in Sub-E      │
                                                   └────────────────────────┘
                                                                │
                                                                ├── parallel evaluation ──┐
                                                                │                         │
                                                                ▼                         ▼
                                                        Top-k candidates         Retrieval scorer
                                                                │                  (Sub-A onward,
                                                                │                  affect prior
                                                                │                  in Sub-D)
                                                                │                         │
                                                                └─────► User sees ◄───────┘
                                                                        primary path
                                                                        results

(Eventual direction, not Phase I commitment: retrieval becomes primary, LLM becomes
fallback, affect couples to retrieval ranking only. Decision deferred — see "What changed
from v1.")
```

Key facts about this Phase I architecture:

- **The active prediction path is unchanged from the current demo + v1 plan**: GPT call with anti-hallucination prompt, modulated by affect via system-prompt and temperature
- **The retrieval scorer (built in Sub-A onward) runs in parallel for evaluation**, not as a replacement
- **`affectState` is a typed contract with confidence and baseline-relative HRV** — this is new in v2 and is independent of which integration mechanism wins
- **The widget displays valence and confidence both** — testers and clinicians need to see when affect is unreliable
- **BLE handling lives in the cloned Lief mobile app shell** (Rohan) — we do not handle raw BLE bytes ourselves

---

## The affect contract (absorbed from v1)

The `liefState` object is the central state object passed through the prediction pipeline. Initialized as mock; `source` flips to `'lief-shell'` when the cloned mobile app shell provides real data (Sub-Phase B).

```javascript
let liefState = {
  hrv: null,                  // Raw RMSSD value (ms), null if no connection
  hrv_baseline_z: null,       // Baseline-relative z-score (Sub-Phase C)
  quintile: null,             // 0-4, mapped from Lief quintile scores (Sub-Phase B/C)
  valence: 0.5,               // 0.0 (distressed) -> 1.0 (calm/positive)
  arousal: 0.5,               // 0.0 (low energy) -> 1.0 (high energy), secondary axis
  confidence: 0.0,            // 0.0-1.0, how much we trust this reading
  source: 'mock',             // 'mock' | 'lief-shell'
  available_modalities: ['hrv'],   // Phase II adds: 'eda', 'motion', 'temp', 'caregiver_flag'
  inferred_category_prior: null,   // p(c | X) categorical (Sub-Phase D)
  lastUpdated: null,          // Timestamp of last reading
};
```

**Quintile-to-valence mapping (placeholder for Sub-Phase 0; replaced by baseline-relative computation in Sub-Phase C).** Lief uses quintile scoring relative to the user's own HRV baseline. Higher quintile = higher HRV = calmer state.

```javascript
const QUINTILE_TO_VALENCE = {
  0: 0.1,  // Most stressed -- 😫
  1: 0.3,  // Stressed      -- 😟
  2: 0.5,  // Neutral       -- 😐
  3: 0.7,  // Calm          -- 🙂
  4: 0.9,  // Most calm     -- 😊
};
```

**Valence emoji mapping:**

```javascript
const VALENCE_EMOJIS = [
  { threshold: 0.2, emoji: '😫', label: 'High stress' },
  { threshold: 0.4, emoji: '😟', label: 'Stressed' },
  { threshold: 0.6, emoji: '😐', label: 'Neutral' },
  { threshold: 0.8, emoji: '🙂', label: 'Calm' },
  { threshold: 1.1, emoji: '😊', label: 'Very calm' },
];
```

**Affect-modulated system prompt (the v1 mechanism, active in Sub-Phase 0 onward):**

```javascript
function buildAffectSystemPrompt(liefState) {
  let affectContext = '';

  if (liefState.valence < 0.35) {
    affectContext = `The user appears anxious or highly stressed (HRV signal low).
Prioritize short, simple, calming phrases. Avoid complex constructions.
Prefer: needs, requests for comfort, simple statements.`;
  } else if (liefState.valence < 0.55) {
    affectContext = `The user shows mild stress. Prefer clear, direct sentences.`;
  } else if (liefState.valence < 0.75) {
    affectContext = `The user appears calm and regulated. Suggest natural, expressive sentences.`;
  } else {
    affectContext = `The user is very calm and engaged. Support rich, expressive communication.`;
  }

  // Affect context is prepended to the existing anti-hallucination grammar-engine
  // prompt that's already in app.js predictWithAPI(). The voice-authenticity rules
  // ("never add content words the child did not tap") are unchanged.
  return affectContext;
}
```

**Affect-modulated temperature:**

```javascript
function getAffectTemperature(liefState) {
  // High stress -> lower temp -> more conservative/predictable
  // Calm        -> higher temp -> more expressive/varied
  // Range: 0.25 -> 0.90 (compared to current static 0.3)
  return 0.25 + (liefState.valence * 0.65);
}
```

**Confidence weighting (added in v2; not in v1).** When `liefState.confidence < 0.3`, the affect context is suppressed (use neutral/default prompt) and temperature reverts to the static 0.3. This is the Phase I way of saying "we have a typed contract for low-confidence affect"; the implementation is straightforward.

```javascript
function applyAffectToRequest(liefState) {
  if (liefState.confidence < 0.3) {
    return { systemPrompt: '', temperature: 0.3 };  // fallback to current behavior
  }
  return {
    systemPrompt: buildAffectSystemPrompt(liefState),
    temperature: getAffectTemperature(liefState),
  };
}
```

These four functions plus the `liefState` object are the entire Sub-Phase 0 mechanism. Concrete file-level patches against `app.js`/`index.html`/`style.css` are spelled out in `monday-demo-update.md`.

---

## The score function (parallel evaluation track)

The retrieval scorer ranks candidate phrases u_j against the symbol selection s and (when available) affect state X. This runs **alongside** the primary LLM path, producing rankings that can be compared but do not (yet) drive the user-facing output:

```
score(u_j | s, X, θ_i) =
    α · cos(E(symbol_phrase(s)), E(u_j))     ← Phase I.A: retrieval similarity
  + β · log p(c_j | X, θ_i)                  ← Phase I.D: affect-conditional prior
  + γ · log π_i(c_j)                         ← Phase I.C: per-user category base rate
  + δ · recency_bonus(u_j, user_history)     ← Phase I.C: recency
```

The point of running this in parallel during Phase I is to collect comparison data:

- **Top-k overlap with the LLM path**: how often do the two methods agree on the top candidate?
- **Where they disagree, which is right?** Adjudicated by SLP review on representative scenarios (post-IRB) or by structured expert review (pre-IRB).
- **Latency comparison**: retrieval is much faster; if quality is comparable, that's a strong argument for the eventual migration.
- **Affect-on vs. affect-off behavior**: does β > 0 produce sensibly different rankings for high-arousal scenarios, in the direction clinicians expect?

In Phase I, the retrieval scorer's output is logged but not displayed to users. The user-facing prediction comes from the LLM path with v1's prompt-modulation mechanism.

The categorical prior `p(c | X, θ_i)` operates over a small set of communicative-act categories (request, protest, comfort-seeking, description, social, affirmation). This taxonomy is Phase I.D work and requires SLP ratification before it goes live in any path.

---

## Phased plan over the Phase I window

The 8-week implementation horizon decomposes into four sub-phases, each with specific deliverables and success criteria. These are sequenced so that earlier sub-phases produce demonstrable artifacts that don't depend on Lief device access, baseline data, or IRB approval.

### Sub-Phase 0 — Visible placeholder, built Sunday 2026-04-26 for Monday 2026-04-28 demo

**Goal.** Implement v1's mechanism end-to-end with mock affect input. None of this is in `app.js` v6 currently; all of it is greenfield work for tomorrow. Detailed file-level build spec is in `monday-demo-update.md`; this section is the planning-level summary.

**Deliverables (all new code Sunday):**
- `liefState` object with sensible mock defaults (schema in "The affect contract" above)
- Emoji widget rendered above the symbol grid showing valence + `(simulated)` indicator
- "Connect Lief" button (placeholder UX — real connection comes in Sub-Phase B via the cloned mobile app shell)
- Mock valence slider in dev controls so the demo can show affect changing
- `buildAffectSystemPrompt(liefState)`, `getAffectTemperature(liefState)`, and `applyAffectToRequest(liefState)` implemented per "The affect contract" section
- Modify the existing `predictWithAPI` in `app.js` to call `applyAffectToRequest()` and use the returned system prompt + temperature
- HTML changes to `index.html` for the widget container, slider, and button
- CSS changes to `style.css` for widget styling

**What is explicitly in Sub-Phase 0:**
- Affect-driven changes to the GPT system prompt and temperature (the v1 mechanism, implemented for the first time)

**What is explicitly NOT in Sub-Phase 0:**
- Real device connection (cloned mobile app not yet available)
- Baseline normalization (raw RMSSD-to-valence mapping is a placeholder per v1)
- Any retrieval-scorer infrastructure (Sub-A)
- Any categorical prior or β term (Sub-D)
- Any SLM evaluation (Sub-E)

**Success criteria.**
- Widget visible and updates when slider moves
- GPT system prompt visibly changes when slider moves (verifiable by inspecting network requests in browser dev tools)
- Sampling temperature visibly changes (same mechanism)
- "Connect Lief" button visible, behaves as a placeholder when clicked
- Demo runs end-to-end on Chrome
- Team can see "the v1 mechanism is implemented and runs on mocked input" without confusion about what's real

**Risk.** Stakeholders may interpret the visible widget + active prompt-modulation as a clinically-validated affect-aware system. Mitigation: the `(simulated)` badge is non-removable in this sub-phase, the Monday talking-points doc is explicit that the affect signal is mocked, and the affect-to-prediction coupling is described as "the first-pass mechanism we're evaluating."

---

### Sub-Phase A — Retrieval substrate (parallel evaluation track) (weeks of 2026-04-29 → 2026-05-12, ~2 weeks)

**Goal.** Build embedding-based retrieval over the existing `SENTENCE_TEMPLATES` library as a **parallel scorer** alongside the live LLM path. This is infrastructure for evaluating the eventual retrieval-first migration, not a replacement of the current path.

**Deliverables.**
- Embed the existing `SENTENCE_TEMPLATES` library (~50 entries) using a multilingual sentence encoder (candidates: `multilingual-MiniLM-L12-v2` for size, `multilingual-e5-small` for quality — choice is empirical)
- Cosine-similarity retrieval function returning top-k candidates ranked by `α · cos(...)`
- Score function exposed as a pure function so β/γ/δ terms can be added later without restructuring
- **Logging hooks**: every prediction request logs both the LLM-path top-3 and the retrieval-path top-3, plus their respective latencies, for offline comparison
- **Decision logged**: encoder client-side (smaller, slower, simpler IRB story) vs. server-side (faster, requires infrastructure)?

**Success criteria.**
- Retrieval returns same top-1 as current dictionary on >90% of dictionary entries
- Retrieval returns sensible top-3 on 10 hand-picked symbol combinations not in the dictionary (subjective, evaluated by Mike + Rohan)
- p50 retrieval latency under 100ms (target), p95 under 250ms
- Side-by-side log shows clear comparison data: LLM top-3 vs. retrieval top-3 vs. user-selected (when applicable)

**What this enables.** Sub-Phases C and D add personalization terms (γ, δ) and the affect prior (β) to the same scorer. Once Sub-D lands, the retrieval scorer becomes the place where affect-as-categorical-prior can be evaluated against affect-as-prompt-modulation in the live LLM path. That comparison is the data we'd want before deciding to migrate the user-facing path off the LLM mechanism.

**What this sub-phase does NOT do.** Switch the user-facing prediction off the LLM path. That decision is deliberately deferred — see "What changed from v1."

---

### Sub-Phase B — Real Lief integration via cloned mobile app shell (weeks of 2026-05-06 → 2026-05-12, ~1 week)

**Goal.** Replace the mock affect state with real HRV from a Lief device. The affect signal is captured and feeds the existing v1 prompt-modulation mechanism (and the parallel retrieval scorer's logging).

**Major scope change from v2 draft.** Rohan's update on 2026-04-26: **we are not writing raw BLE handlers ourselves.** The Lief mobile app already handles BLE, byte parsing, device pairing, and reconnection robustly. Rohan will clone parts of the Lief mobile app and re-skin it as the AMIGA-AAC shell, exposing HRV/quintile/quality-flag signals to the AAC layer through the app's existing internal APIs. This eliminates roughly 60% of the original Sub-Phase B scope.

**What this means concretely:**
- We do not need GATT service UUIDs, characteristic UUIDs, or HRV byte-format documentation — the cloned app has all of this working
- We do not need to write `connectLief()`, `handleHRVData()`, or the disconnection state machine — the cloned app has these
- We do not need Web Bluetooth (browser-side BLE) at all — the AAC tool runs inside the cloned mobile app shell
- The "Connect Lief" button becomes a much smaller piece of UX: surface the connection state from the app shell, not initiate the connection from JS

**Deliverables.**
- AMIGA-AAC tool integrated into the cloned Lief mobile app shell
- Affect data subscribed from the app shell's internal API into `affectState`
- Affect data flow: app shell → AAC layer → `affectState` → v1 prompt-modulation (and parallel retrieval logging)
- Connection-state UI mirrors the cloned app's connection state (connected / disconnected / poor signal)
- Confidence estimation: at minimum, surface the cloned app's existing sensor-quality flags into `affectState.confidence`

**Success criteria.**
- AAC tool runs inside the cloned shell on the target mobile platform (iOS/Android — Joannalyn to confirm)
- Real HRV from a worn Lief device shows up in `affectState` and updates the widget
- "(simulated)" badge automatically clears when source becomes `'lief-shell'`
- Disconnection during a session is handled gracefully — affectState keeps its last reading but flips `confidence` to a low value, the widget shows "(stale)" or similar

**Risk reduction from this approach:**
- No dependency on Lief team for UUID/byte-format documentation (was 2 of the 4 critical-path open questions in v1)
- Reconnection robustness inherited from production Lief code rather than written from scratch
- Known-good BLE path means we don't lose a week to BLE debugging

**Tradeoffs of this approach:**
- AAC tool is now distributed as a mobile app, not as a web app. Web Bluetooth path goes away. This affects how we share builds with Faison testers and how IRB describes the technology.
- Cross-platform (iOS + Android) is a bigger lift than cross-browser. If the cloned app is iOS-only, the demo and pilot are iOS-only too.
- Tighter coupling to Lief's mobile codebase. If their app changes structure, we may need to re-clone. Long-term answer per Rohan is to extract a cross-platform library, but that's a bigger effort and is out of Phase I scope.

**Open question (one remaining, much narrower than v1's BLE list):**
- Target mobile platform for Phase I demo and Faison pilots: iOS, Android, or both? (Joannalyn / Rohan)

**Sub-Phase B does NOT require:** baseline access, intent-category schema, or IRB approval. It is gated on Rohan delivering the cloned app shell, expected within the next week per his 2026-04-26 update.

---

### Sub-Phase C — Baseline normalization & per-user state (weeks of 2026-05-13 → 2026-05-26, ~2 weeks)

**Goal.** Make the affect signal personally meaningful rather than absolute. This is the single most important Phase I commitment for ASD-population safety, and it applies regardless of which integration mechanism wins (prompt modulation or retrieval reranking).

**Deliverables.**
- Per-user baseline storage: rolling-window HRV statistics (μ_i, σ_i) accumulated over device wear time
- Baseline-relative z-score computation: `hrv_baseline_z = (hrv - μ_i) / σ_i`
- `affectState.valence` is derived from the z-score, not from raw HRV (replaces v1's `rmssd / 80` placeholder)
- Cold-start handling: when baseline is sparse (< N samples or < D days), valence defaults toward neutral and confidence is reduced
- Per-user persistence model decided and implemented: device-local? server-side? both?
- `recency_bonus` (δ term in retrieval scorer) implemented from accepted-phrase history, also per-user

**Active in v1's prompt-modulation path too.** Once this lands, `buildAffectSystemPrompt(affectState)` receives a baseline-normalized valence, not a population-relative one. The prompt thresholds (< 0.35 → "anxious", < 0.55 → "mild stress" etc. in v1's implementation) become baseline-relative thresholds. This is a meaningful improvement to the v1 mechanism, not a replacement of it.

**Success criteria.**
- For a user with stable HRV at their personal mean, valence reads as neutral regardless of absolute HRV
- For a user with HRV one σ_i below mean, valence reads as moderately stressed
- Confidence reads low for first ~5–7 days of new-user data, increases as baseline stabilizes
- Per-user state persists across sessions
- The recency bonus is observable in the parallel retrieval scorer's output

**Decision required during this sub-phase (joint with Joannalyn, Rohan, USC):**
- Where does per-user state live? Local-only is IRB-simplest; server-side enables federation; both is most flexible. This decision affects USC's IRB amendment for Phase II.
- Does the cloned Lief mobile app shell already maintain per-user baseline statistics? If so, we may be able to subscribe to its baseline rather than computing our own.

**Why this matters.** The §3.5 ASD-physiology literature (Lydon et al. 2016, Goodwin et al. on autism HRV variability) is unambiguous: population-level HRV thresholds are unsafe in autistic populations because of high inter-individual variability and atypical reactivity patterns. Without baseline normalization, the affect signal will be systematically wrong for a substantial fraction of users — and that is true whether the affect drives a prompt modulation or a retrieval reranking. The v1 fallback (`rmssd / 80`) is a placeholder, not a deployment path.

---

### Sub-Phase D — Categorical prior on intent, evaluated against v1 prompt path (weeks of 2026-05-27 → 2026-06-23, ~4 weeks)

**Goal.** Turn baseline-normalized affect into a usable categorical prior over communicative-act categories in the parallel retrieval scorer, and **collect comparison data** between this approach and v1's prompt-modulation approach.

**Deliverables.**
- A small intent-category taxonomy ratified with Casey Okoniewski and the Faison SLPs (Gabrielle DeFazio, Emily Johnson)
- Each candidate phrase in the retrieval library tagged with its intent category (one-time clinician annotation)
- Tagging mechanism for SLPs (e.g., shared spreadsheet with category dropdown, or lightweight web form) and reverse-import into the retrieval library
- A zero-shot affect→category prior function: `p(c | valence, arousal)` — initially hand-specified by clinicians, later learned from logs
- The β term enabled in the **parallel retrieval scorer** (the user-facing LLM path is not affected)
- Confidence-gated coupling: when affect confidence is low, β is automatically reduced; when sufficient, β is at full weight
- Per-user category base rates `π_i(c)` initialized with population priors, updated as the user accumulates accepted predictions
- **Comparison logging**: for each prediction, both the LLM-prompt-modulated top-3 and the retrieval-with-affect-prior top-3 are logged for offline review
- Phase I evaluation report (draft) summarizing the affect-on/affect-off comparison data and the LLM-path/retrieval-path divergence analysis, suitable for inclusion in the Phase II grant application

**Success criteria.**
- Affect-on vs. affect-off A/B comparison on the parallel retrieval scorer shows non-trivial difference in top-3 candidate ordering for high-arousal scenarios
- The difference is in the right direction (clinician judgment): high-arousal states surface request/protest/comfort categories more prominently than description/social
- Category base rates evolve sensibly over a simulated user session
- No regression in low-arousal or unknown-affect scenarios (β contribution stays small when affect is uncertain)
- **Side-by-side comparison data**: log shows where the LLM-prompt path and the retrieval-prior path agree, where they diverge, and what the user/SLP picked

**What this enables for Phase II decision-making.** At end of Phase I, the team has empirical data to decide between:
1. Keeping affect-as-prompt-modulation (current path), with baseline normalization as the key Phase I improvement
2. Migrating affect-as-categorical-prior to the user-facing path
3. A hybrid where retrieval is the primary path and the LLM is the fallback for novel symbol combinations

The Phase I comparison data, plus the SLP review of where the two paths disagree, is the input to that decision. We are not making it now.

**Why this is the latest sub-phase.** It requires (i) the retrieval substrate from A, (ii) reliable affect signal from B, (iii) baseline normalization from C, and (iv) clinical input on the taxonomy. It is the most clinically sensitive piece — getting the categories wrong propagates to every prediction — and the most engineering-light once the substrate exists.

**What this sub-phase does NOT commit to.** Training a Stage-1 intent classifier from logged data (Approach B in the Phase I Architecture document). That's Phase II, contingent on labeled data accumulating during the IRB-approved deployment window. Also, this sub-phase does **not** flip the user-facing prediction off the LLM-prompt path. The retrieval scorer with the β term runs in parallel and produces comparison data; the production prediction continues to come from v1's mechanism.

---

### Sub-Phase E — Small-LM (SLM) exploration (weeks of 2026-05-20 → 2026-06-16, ~4 weeks, runs parallel with C and D)

**Goal.** Evaluate whether a small CPU-runnable language model (1B–4B parameters) can replace the GPT-4o-mini API call. The AAC grammar-engine workload is light — top-3 candidate sentences over a 50-word vocabulary, no heavy reasoning — and is plausibly within reach of edge-deployable models.

**Why this matters.** A successful local SLM addresses several open project concerns at once:

- **Closed-API IRB exposure.** Sending child interaction data to a third-party API requires explicit IRB and parental consent disclosure. Local inference removes this entire concern.
- **Latency variance.** GPT-4o-mini round-trips run 400–800ms typical and unbounded under network jitter. Local SLM inference on consumer hardware is bounded and consistent.
- **HIPAA / data-flow simplicity.** Local inference simplifies the data-flow story USC IRB reviews.
- **Hardcoded API key.** Sidesteps the operational concern in the current `app.js`.
- **Affect-coupling flexibility.** Local models permit logit biasing, grammar-guided decoding (Outlines, llama.cpp grammars), and other constrained-decoding techniques that closed APIs do not. This becomes relevant if the team eventually moves affect into decoding rather than prompting.

**The 2026 SLM landscape (verified via web search 2026-04-26).** Edge-deployable models in the 1B–4B range have matured substantially: Llama 3.2 (1B, 3B), Phi-4-mini (3.8B), Qwen 2.5 (0.5B, 1.5B, 3B), Gemma 3 (down to 270M), SmolLM2 (135M–1.7B), SmolLM3 (3B), Liquid AI LFM 2.5, and MobileLLM-R1. Llama 3.2 3B is the canonical example — it runs on a $35 Raspberry Pi at usable token-rates and exceeds GPT-3.5 on common benchmarks. For a workload as light as ours, even the 1B-class models are likely sufficient.

**Deliverables.**
- A short comparative evaluation: 3–4 candidate SLMs benchmarked on the existing AAC grammar-engine task using the current prompt
- Comparison metrics: top-1 agreement with GPT-4o-mini, voice-authenticity violation rate (out-of-vocabulary content words), latency p50/p95 on a target device class, model size on disk, memory footprint at inference
- A recommendation document: which SLM (or none, sticking with the API), under what deployment configuration (mobile-side, server-side, hybrid)
- A working integration of the chosen SLM in the cloned mobile app shell, gated behind a feature flag so the team can A/B against the API path

**Candidate models for first-pass evaluation:**
- **Llama 3.2 3B** — strong baseline, well-supported, runs on iOS/Android via mlc-llm or executorch
- **Phi-4-mini (3.8B)** — Microsoft, strong on reasoning and structured output
- **Qwen 2.5 1.5B or 3B** — strong multilingual support (relevant for Milestone 2a)
- **SmolLM3 3B** — fully open, designed for efficiency

The decision between mobile-side (runs on the user's phone, fully local) and server-side (runs on a Lief-controlled server) is a tradeoff between latency, model-size flexibility, and IRB simplicity. Both are tractable; the choice depends on what mobile platforms we target and what server infrastructure Lief has.

**Success criteria.**
- At least one SLM achieves top-1 agreement with GPT-4o-mini on >80% of held-out test scenarios
- Voice-authenticity violation rate (out-of-vocabulary content words in output) is no worse than GPT-4o-mini's
- Latency p95 under 500ms on the target device class (target: same or better than the API)
- Memory footprint fits within the cloned mobile app shell's budget

**What this sub-phase does NOT do.** Replace GPT-4o-mini in the user-facing path during Phase I. Like Sub-Phases A and D, this is evaluation infrastructure that produces a recommendation. The team decides, with data in hand, whether to flip the user-facing path. The SLM may end up as a fallback (used when network is unavailable) rather than the primary, which is also a fine outcome.

**Open questions:**
- Target device class for mobile-side inference: minimum specs? (Joannalyn / Rohan)
- Lief server infrastructure for server-side inference: available, or would need to be stood up? (Rohan)
- Multilingual evaluation scope: Phase I requires >2000 words and implies multilingual; the SLM choice should be evaluable on at least one non-English locale

---


```
Week of:   04-26   05-04   05-11   05-18   05-25   06-01   06-08   06-15   06-22
─────────────────────────────────────────────────────────────────────────────────
Sub-0 ─►   ▓▓
A           ░░░░░░░░░░░░
B                ░░░░░░          (1 wk — gated on cloned shell from Rohan)
C                     ░░░░░░░░░░░░
D                                ░░░░░░░░░░░░░░░░░░░░░░░░░░
E                                ░░░░░░░░░░░░░░░░░░░░░░
─────────────────────────────────────────────────────────────────────────────────
                    │       │       │       │       │       │       │
                    │       │       │       │       │       │       └─ End Phase I (Milestone 2a)
                    │       │       │       │       │       └─ IRB approval target
                    │       │       │       │       └─ Sub-C closeout
                    │       │       │       └─ SLM pick (Sub-E mid-point)
                    │       │       └─ Sub-A & B closeouts
                    │       └─ Mid-month review with Faison
                    └─ Monday demo (Sub-0)
```

Slip risk concentrates on three dependencies: the cloned mobile app shell from Rohan (gates Sub-Phase B), SLP availability for the intent-taxonomy conversation (gates Sub-Phase D), and target-device decisions from Joannalyn (gates both B and E). The plan is robust to any one of B, D, or E slipping by 1–2 weeks because A and C produce useful artifacts on their own. The active prediction path (v1 prompt-modulation through GPT-4o-mini, or whatever model Sub-E selects) keeps working throughout.

---

## Cross-cutting work and overhead

Beyond the per-sub-phase deliverables, ongoing work across Phase I includes the following recurring categories. This work is real, distributed across the 8-week window, and not allocated to any single sub-phase. It is what makes the per-sub-phase deliverables ship cleanly rather than land as code with no documentation, no team awareness, and no review.

- **Weekly project sync** with the team (~1 hour/week, 8 weeks). Status, blockers, decisions surfaced for joint resolution.
- **Async communication and code review** with Rohan (~1.5 hours/week). PR review, design-question Slack threads, debugging-pair sessions outside scheduled meetings.
- **Architecture documentation maintenance** (~1 hour/week). As decisions are made and scope evolves, the planning documents (this one, the State of Knowledge doc, the Architecture doc) are kept current. This is what makes the documents useful as references at the end of Phase I rather than stale snapshots from week 2.
- **Onboarding** to the AAC literature, the existing codebase, and the Lief anxiety-LLM stack. Front-loaded across weeks 1–3, totaling ~12 hours. Mike has been on this project less than a week as of 2026-04-26; meaningful technical onboarding is required to operate at the architecture-advisor level the role expects.
- **Meeting prep, demo prep, retrospectives** (~30 minutes/week). The Monday demo this week is one example; expect 2–4 hours of polish on top of the engineering work for each significant team-facing demo across Phase I.

Total cross-cutting work over Phase I is approximately 44 hours (likely-case) to 60 hours (pessimistic). It accounts for ~21% of the likely-case Phase I total. The estimates document allocates this proportionally across sub-phases when computing per-unit project pricing, so it is not a separate line item in fixed-price quotes — it is baked into the unit prices.

---

## What success looks like at end of Phase I

**In a Monday-meeting form:** by end of June, when a user wearing a Lief device taps symbols, the system runs the affect-aware GPT call (v1 mechanism, with baseline-normalized HRV) and returns a top-1 prediction; in parallel, a retrieval scorer with an affect-categorical-prior produces its own top-3 ranking; both are logged. The user sees the LLM-path output. The team sees comparison data across thousands of interactions, plus SLP review of where the two approaches disagree. The SLM evaluation has produced a recommendation about whether to migrate off GPT-4o-mini. The affect signal is per-user-baseline-normalized, gracefully degrades when the device is missing or noisy, and is visibly displayed so caregivers can interpret what the system is using.

**In a Phase II grant-prep form:** this delivers the closed-loop architecture from the Q1 Kickoff slide page 43 in production form (v1's affect-aware prompt mechanism) while also producing the empirical foundation for two key Phase II decisions: (i) whether to migrate to retrieval-with-affect-prior as the primary mechanism, and (ii) whether to migrate from closed API to local SLM. The decision in either case is made with data, not in advance. The work is instrumented for the layered evaluation framework (telemetry layer captures comparison deltas; SLP layer can adjudicate divergent cases), and structurally ready for the multimodal extensions (EDA, motion, facial, caregiver flags) that Phase II will add.

**In a what-we-can-publish form:** the comparison itself — affect-as-prompt-modulation versus affect-as-categorical-prior, on a real AAC use case with paired symbol-affect-acceptance triples — is plausibly novel enough to be a paper, regardless of which mechanism wins. The Phase I dataset (assuming IRB approval lands on schedule) is a separable contribution. The personalization protocol (baseline-relative + cold-start subtype prior) is another separable contribution. None of these are Phase I deliverables; all are Phase I byproducts of running both paths in parallel.

---

## Measurement & evaluation

The team's layered evaluation framework (telemetry / SUS / NASA-TLX / CETI / optional Vineland-3 + FCP-R) is the primary evaluation. The engineering-internal metrics below feed into it but don't replace it.

**Engineering-internal metrics tracked from Sub-Phase 0 onward (in logs only — no human-subjects data without IRB):**

| Metric | Sub-Phase first measurable | Why it matters |
|---|---|---|
| GPT path latency p50 / p95 | 0 | Real-time usability constraint |
| Retrieval path latency p50 / p95 | A | Baseline for SLM and migration decision |
| Retrieval coverage (% of symbol combos with cos > 0.7) | A | Tells us if library needs expansion |
| LLM path vs. retrieval path top-1 agreement % | A | Whether retrieval is "good enough" yet |
| Lief BLE connection uptime % during demo sessions | B | Operational reliability (inherited from cloned shell) |
| HRV-vs-Lief-app cross-validation | B | Signal correctness |
| Baseline stability (σ of σ_i over weekly windows) | C | Calibration quality |
| Affect confidence distribution | B–C | Tells us how often we trust the signal |
| Top-3 candidate Kendall-τ change with β=0 vs β>0 in retrieval scorer | D | Whether affect is doing anything in the retrieval path |
| Per-user category base rate divergence from population | C–D | Whether personalization is working |
| SLM vs. GPT-4o-mini top-1 agreement % | E | SLM viability gate |
| SLM voice-authenticity violation rate | E | Compares to GPT-4o-mini's rate |
| SLM latency p95 on target device | E | Edge feasibility |
| Cases where LLM-prompt path and retrieval-prior path disagree | A→D | The substrate for the Phase II mechanism decision |

**Metrics deliberately NOT tracked in Phase I (require IRB):** anything involving real children's interactions, intent-label ground-truth from session annotations, caregiver acceptance ratings, clinician-adjudicated communication success.

---

## Open questions (updated 2026-04-26)

Significantly shorter than v1's list, primarily because the cloned-mobile-app-shell approach removes the BLE-engineering uncertainties.

| Question | Owner | Sub-Phase blocked | Status |
|---|---|---|---|
| Cloned Lief mobile app shell delivery | Rohan | B | Open — expected within next week per 2026-04-26 update |
| Target mobile platform (iOS/Android/both) | Joannalyn / Rohan | B + E | Open |
| Per-user state location (local / server / both) | Joannalyn / Rohan / USC | C | Decision needed by mid-May |
| Lief baseline statistics: does the cloned app already maintain these? | Rohan | C | Open — could simplify Sub-C significantly |
| Intent taxonomy — does it match SLP framing? | Casey, DeFazio, Johnson | D | Conversation needed early May |
| SLM target deployment: mobile-side, server-side, or both? | Joannalyn / Rohan | E | Open |
| SLM minimum device specs for mobile-side inference | Joannalyn / Rohan | E | Tied to target mobile platform decision |
| Closed-API GPT call vs. local model migration timing | Joannalyn / USC IRB | E | Sub-E produces the data USC IRB review needs |
| API key handling (currently hardcoded in client) | Rohan | All | Should be resolved before any external demos |

**Resolved or de-scoped from v1's open questions list:**
- ~~Lief GATT service + characteristic UUIDs~~ — handled by cloned mobile app
- ~~HRV characteristic byte format~~ — handled by cloned mobile app
- ~~Quintile over BLE or only RMSSD~~ — exposed by cloned app's internal API
- ~~Lief SDK / JS library availability~~ — superseded by cloned-app approach
- ~~Lief DB access for per-user baselines~~ — likely available via cloned app shell, pending Rohan confirmation

---

## What this plan deliberately does NOT include

A few things from the broader project conversation that I am consciously deferring:

- **Replacing v1's prompt-modulation mechanism in the user-facing path.** Kept active throughout Phase I. The retrieval scorer with affect prior is built as a parallel evaluation track. The Phase II decision about which mechanism to use as primary is informed by Phase I's comparison data, not made in advance.
- **Stimming detection from accelerometer.** Phase II.
- **EDA, skin temperature, facial expression, caregiver flags.** Phase II — but the affectState contract has named slots for them with `available_modalities` flags so adding them is additive.
- **Federated personalization.** Phase II/III.
- **Stage-1 intent classifier training.** Phase II, contingent on labels.
- **Multilingual support as a separate track.** Comes for free with the multilingual encoder choice in Sub-A and the multilingual-capable SLM evaluation in Sub-E.
- **Phase II IRB amendment scope.** Engineering identifies what data flows are involved; USC drafts the amendment. Not a Phase I implementation deliverable.

---

## How this plan interacts with the SOW

| SOW Milestone | What this plan delivers |
|---|---|
| 1a (Adapt Lief LLM for autism) | Sub-Phase 0 + the constrained-prompt LLM that already exists, with v1's affect-modulation active |
| 1b (Train AMIGA-AAC LLM with CI/CD) | Sub-Phases A + B + C — "training" interpreted as building the retrieval substrate, the personalization layer, and (Sub-E) evaluating the SLM alternatives. CI/CD covers the offline evaluation harness running both prediction paths in parallel |
| 2a (Multilingual, vocab >2000, affect-aware) | Sub-Phase D delivers affect-aware in the parallel retrieval scorer; v1's mechanism delivers affect-aware in the live path; Sub-A's multilingual encoder + Sub-E's multilingual SLM evaluation deliver multilingual; vocabulary expansion is a curation task that runs parallel to D |

---

## v1 archival

The v1 doc (`lief-affect-integration.md`) is **archived** on adoption of this v2 plan. All of v1's substantive content — the `liefState` schema, the quintile-to-valence mapping, the emoji set, `buildAffectSystemPrompt`, `getAffectTemperature`, the BLE design intent — is absorbed directly into this v2 doc and into `monday-demo-update.md`. The v2 doc plus the Monday spec is fully self-contained; nothing else needs to be read in v1 to execute the plan.

The v1 BLE engineering effort (`connectLief()`, `handleHRVData()`, GATT setup, byte parsing, Web Bluetooth integration) is **not built**. Rohan's 2026-04-26 update established that BLE handling lives in the cloned Lief mobile app shell; we do not write raw BLE in this codebase. The v1 BLE design effort was good engineering at the wrong level of the stack — it informed the integration shape but is superseded by working with the cloned app's internal API (Sub-Phase B).

The five v1 open questions about BLE specifics resolve themselves: GATT UUIDs, HRV byte format, quintile-vs-RMSSD-over-BLE, Lief SDK availability, and Lief DB access for baselines all become "handled by the cloned app shell" or "expose-from-cloned-app's-internal-API."

---

## Closing notes

The substantive question this plan defers — affect-as-prompt-modulation versus affect-as-categorical-prior on retrieval — is real and worth deciding properly. The argument for the deferral is twofold: (i) v1's mechanism is already implemented and works as a placeholder, so there is no Phase I urgency; (ii) Mike has been onboarding to this space for less than a week and should not unilaterally argue for an architectural pivot before reading the AAC and affective-computing literature carefully. The right path is to build both mechanisms in parallel during Phase I, collect comparison data, and revisit the decision with empirical input plus team alignment.

The other substantive bet is that an intent-category taxonomy is a worthwhile clinical-engineering investment. This depends entirely on whether SLPs already think in those categories. If the conversation in early May with Casey and the Faison SLPs reveals that "communicative-act category" is not how clinicians describe communication success, Sub-Phase D collapses to "per-user category base rates without categorical structure" — which is still a useful personalization layer, just less clean mathematically.

The SLM exploration (Sub-Phase E) is the bet most likely to pay off in obvious ways: it potentially resolves the closed-API IRB exposure, the latency variance, and the hardcoded-API-key concerns simultaneously. The 2026 SLM landscape (Llama 3.2 3B, Phi-4-mini, Qwen 2.5, SmolLM3) is mature enough that this is a near-term feasibility question, not a research project.

All three bets are revisable mid-plan. Sub-Phases 0, A, B, and C are robust to any of them being wrong.
