# Monday Demo: Sunday Build Spec + Meeting Plan

> **For:** Mike's Sunday 2026-04-26 build session and the Monday 2026-04-28 team meeting
> **Author:** Mike Pesavento (PezTek)
> **Demo target:** rdixit.github.io/lief-amiga (current deployment, app.js v6)
> **Companion plan:** `affect-plan.md` v2 — full Phase I context

---

## Executive summary

Tomorrow (Sunday) is the build day. The current `app.js` v6 has zero affect-related code — no `liefState`, no widget, no slider, no prompt modulation. The v1 design doc described what to build but was never executed. **Sub-Phase 0 of the Phase I plan is "implement v1 for the first time"**, not "extend an existing implementation."

This document is the concrete build spec for Sunday, plus the talking points for Monday.

---

## What's currently in `app.js` v6 (the starting point)

Confirmed by re-reading the file:

**Present:**
- 34 SYMBOLS array with inline SVG icons across 5 grammatical categories
- `SENTENCE_TEMPLATES` exact-match dictionary (~50 entries)
- `NEXT_WORD_MAP` for grid suggestion reordering
- `selectedSymbols` state array, symbol-tap handler, selected-strip rendering
- `updatePrediction()` orchestrator, `predictWithAPI()` with **static** prompt and **hardcoded `temperature: 0.3`**, `predictLocal()` template fallback, `buildSimpleSentence()`
- `dampenConfidence()` — empirically tuned confidence multiplier
- Web Speech API for output, Web Bluetooth not used anywhere
- Hardcoded base64-obfuscated OpenAI API key (with a self-aware comment)
- Toggles for auto-speak, suggestion highlighting, grid reordering, confidence threshold

**Absent (all greenfield Sunday work):**
- `liefState` object
- Affect emoji widget (DOM, CSS, render function)
- Mock valence slider
- "Connect Lief" placeholder button
- `buildAffectSystemPrompt()`, `getAffectTemperature()`, `applyAffectToRequest()`
- Any modification to `predictWithAPI()` to use those functions

---

## Sunday build plan

Eight discrete tasks, ordered for incremental verification. Each builds on the previous; pause to test after each.

### Task 1 — Add `liefState` global and the constant tables

**File:** `app.js`. **Insert location:** near top, after the `SYMBOLS` / `SENTENCE_TEMPLATES` / `NEXT_WORD_MAP` blocks, before `let selectedSymbols = []`.

```javascript
// ============================================================
// Lief affect state (Sub-Phase 0 — mock-only)
// ============================================================

let liefState = {
  hrv: null,                  // Raw RMSSD value (ms), null if no connection
  hrv_baseline_z: null,       // Baseline-relative z-score (Sub-Phase C, Phase I)
  quintile: null,             // 0-4, mapped from Lief quintile scores
  valence: 0.5,               // 0.0 (distressed) -> 1.0 (calm/positive)
  arousal: 0.5,               // 0.0 (low energy) -> 1.0 (high energy)
  confidence: 0.0,            // 0.0-1.0 — Sub-Phase 0 starts at 0; mock slider sets to 0.6
  source: 'mock',             // 'mock' | 'lief-shell' (Sub-Phase B)
  available_modalities: ['hrv'],
  inferred_category_prior: null,  // p(c | X) categorical (Sub-Phase D)
  lastUpdated: null,
};

const QUINTILE_TO_VALENCE = { 0: 0.1, 1: 0.3, 2: 0.5, 3: 0.7, 4: 0.9 };

const VALENCE_EMOJIS = [
  { threshold: 0.2, emoji: '😫', label: 'High stress' },
  { threshold: 0.4, emoji: '😟', label: 'Stressed' },
  { threshold: 0.6, emoji: '😐', label: 'Neutral' },
  { threshold: 0.8, emoji: '🙂', label: 'Calm' },
  { threshold: 1.1, emoji: '😊', label: 'Very calm' },
];

function getValenceEmoji(valence) {
  return VALENCE_EMOJIS.find(v => valence < v.threshold) ?? VALENCE_EMOJIS[4];
}
```

**Verify:** No visible change in browser. Open DevTools console, type `liefState`, confirm the object exists with mock defaults.

---

### Task 2 — Add the affect prompt + temperature functions

**File:** `app.js`. **Insert location:** above `predictWithAPI()`.

```javascript
// ============================================================
// Affect → prediction modulation (v1 mechanism, first implementation)
// ============================================================

function buildAffectSystemPrompt(liefState) {
  if (liefState.valence < 0.35) {
    return `The user appears anxious or highly stressed (HRV signal low). Prioritize short, simple, calming phrases. Avoid complex constructions. Prefer: needs, requests for comfort, simple statements.`;
  } else if (liefState.valence < 0.55) {
    return `The user shows mild stress. Prefer clear, direct sentences.`;
  } else if (liefState.valence < 0.75) {
    return `The user appears calm and regulated. Suggest natural, expressive sentences.`;
  } else {
    return `The user is very calm and engaged. Support rich, expressive communication.`;
  }
}

function getAffectTemperature(liefState) {
  // High stress -> lower temp (more conservative); calm -> higher temp (more expressive)
  // Range: 0.25 -> 0.90 (current static value is 0.3)
  return 0.25 + (liefState.valence * 0.65);
}

function applyAffectToRequest(liefState) {
  // Confidence gate: when affect signal is unreliable, fall back to current static behavior
  if (liefState.confidence < 0.3) {
    return { systemPrompt: '', temperature: 0.3 };
  }
  return {
    systemPrompt: buildAffectSystemPrompt(liefState),
    temperature: getAffectTemperature(liefState),
  };
}
```

**Verify:** Console: `applyAffectToRequest(liefState)` returns the fallback `{ systemPrompt: '', temperature: 0.3 }` because mock confidence is 0. We'll set confidence to 0.6 when the slider is moved (Task 6).

---

### Task 3 — Modify `predictWithAPI` to use affect

**File:** `app.js`. **Surgical edit** to `predictWithAPI()` only — the existing prompt stays intact (its anti-hallucination rules are separate from affect modulation).

The change converts a single `messages: [{ role: 'user', content: prompt }]` into a `system` + `user` pair, and uses `applyAffectToRequest()` for the temperature.

Before:
```javascript
body: JSON.stringify({
  model: 'gpt-4o-mini',
  messages: [{ role: 'user', content: prompt }],
  max_tokens: 80,
  temperature: 0.3
}),
```

After:
```javascript
const affect = applyAffectToRequest(liefState);
const messages = [];
if (affect.systemPrompt) {
  messages.push({ role: 'system', content: affect.systemPrompt });
}
messages.push({ role: 'user', content: prompt });

const response = await fetch('https://api.openai.com/v1/chat/completions', {
  method: 'POST',
  headers: { /* unchanged */ },
  body: JSON.stringify({
    model: 'gpt-4o-mini',
    messages: messages,
    max_tokens: 80,
    temperature: affect.temperature
  }),
  signal: controller.signal
});
```

**Verify:** With confidence still at 0 (mock default), behavior is identical to current — empty system message is omitted, temperature stays 0.3. We've made the path affect-capable without changing default behavior. Tap a few symbols, get the same prediction as before. Open DevTools network panel, check the request body.

---

### Task 4 — HTML: widget container, slider, button

**File:** `index.html`. **Insert location:** between the `<header class="page-header">` block and the `<div class="ipad-frame">` block.

```html
<!-- Sub-Phase 0 affect controls. Above the iPad frame so it's visible during demo. -->
<div class="lief-affect-bar">
  <div id="lief-affect-widget" class="lief-affect-widget">
    <span class="affect-emoji" id="affectEmoji">😐</span>
    <span class="affect-label" id="affectLabel">Neutral</span>
    <span class="affect-source" id="affectSource">(simulated)</span>
  </div>
  <button id="liefConnectBtn" class="lief-connect-btn" type="button">
    🫀 Connect Lief
  </button>
</div>

<!-- Mock dev controls. Inside the controls panel below the iPad. -->
<!-- Add this as a new control-group inside <div class="controls-panel"> -->
```

Inside `<div class="controls-panel">`, add a new `control-group` block (after the existing toggles, before the confidence slider group):

```html
<div class="control-group">
  <label class="slider-label">
    <span>Mock affect (dev): <span id="mockValenceLabel">0.50 — 😐</span></span>
    <input type="range" id="mockValenceSlider" min="0" max="100" value="50" step="5" class="confidence-slider">
    <span class="slider-hint">Sub-Phase 0 mock — replaced by Lief device data in Sub-Phase B.</span>
  </label>
</div>
```

**Verify:** Refresh the page. The affect widget shows `😐 Neutral (simulated)` above the iPad frame. The mock slider appears in the controls panel. Slider doesn't do anything yet (Task 6).

---

### Task 5 — CSS for the widget and slider

**File:** `style.css`. **Append to end of file.**

```css
/* ============================================================
   Lief affect widget (Sub-Phase 0)
   ============================================================ */

.lief-affect-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  width: 100%;
  max-width: 860px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(10px);
  border-radius: 12px;
}

.lief-affect-widget {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  color: white;
}

.lief-affect-widget .affect-emoji {
  font-size: 28px;
  line-height: 1;
}

.lief-affect-widget .affect-label {
  font-size: 14px;
  font-weight: 600;
}

.lief-affect-widget .affect-source {
  font-size: 12px;
  opacity: 0.7;
  font-style: italic;
}

.lief-affect-widget .affect-source.live {
  color: #86efac;
  opacity: 0.9;
  font-style: normal;
}

.lief-connect-btn {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.lief-connect-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

.lief-connect-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

**Verify:** Refresh. Widget is now styled — emoji visible, label readable, "(simulated)" italicized. Connect button is styled and clickable.

---

### Task 6 — Wire the mock slider and the widget render

**File:** `app.js`. **Two pieces:** add DOM refs to the existing list near the top, and add a render function + slider handler.

In the DOM refs block (around line 267):
```javascript
const liefAffectWidget = document.getElementById('lief-affect-widget');
const affectEmojiEl = document.getElementById('affectEmoji');
const affectLabelEl = document.getElementById('affectLabel');
const affectSourceEl = document.getElementById('affectSource');
const liefConnectBtn = document.getElementById('liefConnectBtn');
const mockValenceSlider = document.getElementById('mockValenceSlider');
const mockValenceLabel = document.getElementById('mockValenceLabel');
```

Add a render function (anywhere in the file — near the other render functions is natural):
```javascript
function renderAffectWidget() {
  const { emoji, label } = getValenceEmoji(liefState.valence);
  affectEmojiEl.textContent = emoji;
  affectLabelEl.textContent = label;

  if (liefState.source === 'mock') {
    affectSourceEl.textContent = '(simulated)';
    affectSourceEl.classList.remove('live');
  } else {
    affectSourceEl.textContent = '(Lief — live)';
    affectSourceEl.classList.add('live');
  }
}
```

Wire the mock slider in `setupEventListeners()`:
```javascript
mockValenceSlider.addEventListener('input', () => {
  const valence = parseInt(mockValenceSlider.value, 10) / 100;
  liefState.valence = valence;
  liefState.confidence = 0.6;       // mock has "decent" confidence so affect actually applies
  liefState.lastUpdated = Date.now();

  const { emoji } = getValenceEmoji(valence);
  mockValenceLabel.textContent = `${valence.toFixed(2)} — ${emoji}`;

  renderAffectWidget();
});
```

Wire the placeholder Connect button (it does nothing real for Sub-Phase 0, just gives feedback):
```javascript
liefConnectBtn.addEventListener('click', () => {
  alert('Lief device connection lands in Sub-Phase B via the cloned Lief mobile app shell. Until then, use the mock slider.');
});
```

Add a render call to `init()` so the widget shows correctly on first load:
```javascript
function init() {
  renderGrid();
  setupEventListeners();
  renderAffectWidget();   // <-- new
  updateSuggestions();
}
```

**Verify:** Refresh. Move the slider — emoji and label change in real time. Slider label shows current valence + emoji.

---

### Task 7 — End-to-end smoke test

This is the demo-readiness check. Run through the demo script (in the next section) and confirm everything works.

Specifically, with the network panel open in DevTools:

1. Slider at 0.10 (high stress). Tap `I, Want, Food`. Inspect the request to `api.openai.com`. Confirm:
   - `messages` array has TWO entries: a `system` message starting with "The user appears anxious or highly stressed..." and a `user` message with the existing grammar-engine prompt.
   - `temperature` is approximately `0.25 + 0.10 * 0.65 = 0.3175`.
2. Slider at 0.90 (very calm). Tap the same symbols. Confirm:
   - `system` message starts with "The user is very calm and engaged..."
   - `temperature` is approximately `0.25 + 0.90 * 0.65 = 0.835`.
3. Slider at 0.50 (default). Confidence on the slider-handler is 0.6, so affect is applied (system message present).
4. Manually set `liefState.confidence = 0.0` in console, tap symbols. Confirm system message is absent and temperature is 0.3 (fallback). Restore by moving slider.

**If any of these don't match, the wiring is wrong.** This is the easiest place for a bug. Walk through Tasks 1–6 to find which step.

---

### Task 8 — Cleanup and commit

- Make sure the API key is still working (we haven't touched it but verify the demo still runs)
- Remove any console.log debug noise added during build
- Commit with a descriptive message: `Sub-Phase 0: liefState + affect-modulated prompt + mock widget (v1 mechanism, first implementation)`

---

## Estimated time

- Tasks 1–2 (state + functions): 30 min
- Task 3 (predictWithAPI edit): 15 min, including testing that nothing broke
- Task 4 (HTML): 20 min
- Task 5 (CSS): 30 min, mostly tweaking until it looks right
- Task 6 (slider + render wiring): 30 min
- Task 7 (smoke test): 30 min
- Task 8 (cleanup): 15 min

Total: ~3 hours of focused work. Add buffer for the inevitable CSS tweaking and one or two surprises. Plan for 4–5 hours.

---

## Pre-meeting checklist (Monday morning before the meeting)

- [ ] Demo URL loads without errors in Chrome
- [ ] Slider visibly changes the widget emoji and label
- [ ] Network panel confirms the system message and temperature change appropriately at 0.10, 0.50, 0.90 valence
- [ ] Mock confidence behavior works (set `liefState.confidence = 0` in console, verify fallback)
- [ ] "Connect Lief" button shows the placeholder alert when clicked
- [ ] At least one clean end-to-end demo run rehearsed

---

## Demo script for the meeting (~3 minutes)

1. Open the AAC tool with DevTools network panel visible. Tap a few symbols — `I`, `Want`, `Food`. Show the existing prediction.
2. Point out the new affect widget showing 😐 Neutral with `(simulated)` badge above the iPad frame.
3. Move the dev-mode mock slider toward "stressed." Widget changes to 😟, then 😫. Open the network panel — show that the GPT request now includes a `system` message saying "The user appears anxious or highly stressed..." and that `temperature` has dropped from 0.83 (calm) to 0.32 (stressed).
4. Re-tap the same symbols. The prediction may differ slightly because the GPT path is now affect-aware. Note that prediction quality is not the point of the demo today — the point is that the closed loop now runs.
5. Click "Connect Lief." Show the placeholder alert. Note that real connection lands in Sub-Phase B when Rohan's cloned Lief mobile app shell arrives.
6. Move the slider back to neutral. Close out.

The point of the demo is to show **a working end-to-end loop with mocked input**, plus where the real device will plug in.

---

## What to say (and not say) about it

**Frame it as:** the v1 design now implemented end-to-end with mocked HRV input. The widget is a visible indicator; the GPT prompt actually changes; the mock slider is the demo affordance until the real device lands. Real Lief integration comes through the cloned mobile app shell within a week.

**Concrete language that's accurate:**

- "We've implemented the affect mechanism end-to-end. The signal is mocked this week; real device data flows through the cloned Lief mobile app shell once Rohan has it."
- "The widget shows valence as an emoji and a `(simulated)` indicator; both go live once the app shell is connected and a per-user baseline is established."
- "Right now, the affect signal modulates the GPT system prompt and the sampling temperature — that's the v1 design, now active. In parallel we're building a retrieval-based scorer that will let us compare approaches with empirical data over the next two months."
- "Phase II decisions about the affect coupling mechanism (prompt vs. retrieval-prior) and the model backend (GPT-4o-mini vs. local SLM) will be made with the comparison data we collect during Phase I, not in advance."

**Things to avoid claiming:**

- That the affect signal is real (it's a slider — mock until the cloned app arrives)
- That the affect-aware behavior is clinically validated (it's a first-pass mechanism we're evaluating)
- That HRV is being read from a real device (not yet)
- That we're committed to the v1 mechanism long-term (we're evaluating alternatives in parallel during Sub-Phases A and D)
- That this implements the full Q1 Kickoff slide closed loop (it implements the v1 mechanism with mocked input; the real-device closed loop closes in May)

**If asked about the integration mechanism:** "Affect modulates the GPT system prompt and the sampling temperature — that's the v1 design, kept active because it works as a placeholder. In parallel we're building a retrieval-based scorer with an affect-categorical-prior that we'll evaluate against the v1 mechanism over the next two months. The Phase II decision about which to use as primary is informed by that comparison."

**If asked about model backend:** "Currently GPT-4o-mini through the API. We're starting an evaluation of small CPU models — Llama 3.2 3B, Phi-4-mini, Qwen 2.5, SmolLM3 — that could plausibly run locally inside the Lief mobile app shell. That would address closed-API IRB exposure and latency variance. The evaluation timeline is mid-May through mid-June."

---

## Open items for the meeting

These are the questions worth surfacing while the team is together. Each blocks specific downstream work:

- **Cloned Lief mobile app shell** — Rohan, expected within next week. Big simplification: we don't write raw BLE handlers, the cloned shell handles BLE/byte parsing/reconnection. Gates Sub-Phase B (real device connection, target weeks of 05-06).
- **Target mobile platform** — iOS / Android / both? — Joannalyn and Rohan. Affects what we can show at Faison pilots and what SLM deployment looks like.
- **Per-user state location** (device-local / server-side / both) — joint decision Joannalyn / Rohan / USC. Blocks Sub-Phase C (baseline normalization, target weeks of 05-13 → 05-26).
- **Intent-category taxonomy conversation** with Casey and Faison SLPs — needs ~30 minutes early May. Blocks Sub-Phase D (parallel retrieval scorer with affect prior, June work).
- **SLM target deployment** — mobile-side, server-side, or both? — Joannalyn / Rohan. Gates Sub-Phase E (small-model evaluation, mid-May onward).
- **Hardcoded API key in app.js** — Rohan. Operational item, not architectural. Should be resolved before any external demos or USC IRB review reaches the data-flow questions.

---

## What this fits into

Eight-week implementation plan from now to end of June, six sub-phases (some run in parallel):

- **Sub-0** — this Sunday's build: v1 mechanism implemented for the first time (Monday demo)
- **Sub-A** — embedding-based retrieval scorer running in parallel for evaluation (~2 weeks, starts next week)
- **Sub-B** — real Lief integration via cloned mobile app shell (~1 week, gated on Rohan's delivery)
- **Sub-C** — per-user baseline normalization (~2 weeks, applies to v1's mechanism too)
- **Sub-D** — categorical intent prior with SLP-ratified taxonomy in the parallel retrieval scorer (~4 weeks, lands by end of Phase I)
- **Sub-E** — SLM evaluation as a GPT-4o-mini alternative (~4 weeks, runs parallel with C and D)

Detailed plan in `affect-plan.md` v2. End of Phase I produces (i) v1's mechanism running on real Lief data with baseline normalization, (ii) parallel comparison data between affect-as-prompt and affect-as-categorical-prior, and (iii) an SLM recommendation. Phase II decisions about which mechanism and which model backend become data-driven rather than premature.

---

## Code review note for Rohan (separate conversation, not the meeting)

A few items I'd want to walk through with you when there's time, in priority order:

1. The hardcoded API key — what's the right move? Server proxy? Local model (which the Sub-E SLM evaluation could feed into)? Both? This needs resolving before USC IRB starts asking about data flows.
2. The cloned Lief mobile app shell — what does the affect-data API surface look like, and where do you want the AAC layer to plug in?
3. Where the affect widget JS should live in the file structure — does `app.js` stay monolithic, or do we start splitting (now that we're adding ~150 lines)?
4. The `confidenceDampening` function — I want to understand the empirical work that produced those multipliers so I don't break it accidentally when Sub-Phase A introduces the retrieval scorer alongside.
5. Whether the existing `SENTENCE_TEMPLATES` / `NEXT_WORD_MAP` dictionaries can stay as-is and have an embedding layer wrap them, or whether we want to refactor while we're in there.
6. What's the deployment story for SLMs in your shell — is there a model loader you've already built for the Lief Anxiety LLM that we can repurpose, or would Sub-E start from scratch?

These are paired-coding-friendly. Half a day to a day, ideally before Sub-A starts in earnest.
