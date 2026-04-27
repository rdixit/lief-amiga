# Session notes — 2026-04-26 Sunday build

> **Session:** Sub-Phase 0 implementation + scope review
> **Author:** Mike Pesavento (PezTek)
> **Status:** Sub-Phase 0 complete. Three scope additions identified and deferred.

---

## What was built (Sub-Phase 0, complete)

All eight tasks from `monday-demo-update.md` are done:

- `liefState` global object, `QUINTILE_TO_VALENCE`, `VALENCE_EMOJIS`, `getValenceEmoji()` added to `app.js`
- `buildAffectSystemPrompt()`, `getAffectTemperature()`, `applyAffectToRequest()` added above `predictWithAPI()`
- `predictWithAPI()` now calls `applyAffectToRequest(liefState)` — system message injected when confidence ≥ 0.3, temperature used from the function
- Affect widget bar (`😐 Neutral (simulated)` + Connect Lief button) added above iPad frame in `index.html`
- Mock valence slider added to controls panel
- `renderAffectWidget()` wired to slider input and called from `init()`
- CSS for widget, bar, connect button, and responsive overrides added to `style.css`
- Cache-bust versions bumped: `style.css?v=3`, `app.js?v=7`
- Phase references removed from visible UI copy

---

## Design decisions made during build

### Prompt architecture: system message for affect, user message for grammar engine

The existing grammar engine prompt lives in the `user` message. When affect is active (`liefState.confidence ≥ 0.3`), a `system` message is prepended with style guidance (e.g. "The user appears anxious — prioritize short, simple phrases"). This is the current wiring.

**What's deferred:** The grammar engine prompt itself was written for a neutral baseline and has not been tuned for affect. The system prompt can nudge style, but the user-message rules ("most natural, grammatically correct English sentence") can pull against it. Properly separating concerns — grammar engine rules in the system message, affect guidance in a second system message or injected into the user message — is a future tuning pass, not done today. The current approach is enough for demo verification.

**What needs tuning:** The affect system prompt brackets (valence < 0.35 → "anxious", etc.) were spec'd before testing. Whether those thresholds and phrasings produce the right behavior on real symbol combos needs empirical testing once the smoke test baseline is established.

### Temperature: fixed at 0.3, system prompt does all style work

**Original spec:** temperature scales linearly with valence, range 0.25–0.90 (`0.25 + valence * 0.65`).

**Problem:** The task is a constrained JSON-output grammar completion over 3–5 symbols. At high valence (calm), temperature 0.84 increases JSON parse failures and grammatical noise rather than producing meaningfully "richer" sentences. Style guidance belongs in the prompt, not in sampling randomness.

**Decision:** Temperature fixed at 0.3 in `applyAffectToRequest()`. `getAffectTemperature()` is preserved in the codebase for rollback if we want to re-enable valence-scaled temperature.

### Grammar engine bug fix: "You" → request, not statement

**Bug:** `You, Give, Water` was producing "You want to give water." The model was following the `He/She, Eat, Food → "He wants to eat food."` pattern and treating "You" as the actor.

**Fix:** Added an explicit rule and three examples to the grammar engine prompt:
- Rule: when "You" is the first symbol, interpret it as a request directed AT another person, not a statement about them
- Examples added: `You, Give, Water → "Can you give me water?"`, `You, Help → "Can you help me?"`, `You, Stop → "Please stop."`

**Note for future:** The `SENTENCE_TEMPLATES` local fallback also has `you_give`, `you_help`, `you_look`, `you_stop`, `you_play` entries that already produce the correct request form. The API path was the gap.

### Demo test combinations

Two-symbol combos with no noun (e.g. `You, Help`) get the 0.55 dampening multiplier and land below the 70% confidence threshold. Best demo sequences for showing affect differences AND crossing the threshold:

| Symbols | Stressed 😫 expected | Calm 😊 expected |
|---|---|---|
| `You, Give, Water` | "Give me water." | "Can you give me some water, please?" |
| `You, Give, Food` | "Give me food." | "Can you give me some food?" |
| `I, Want, More, Food` | "I want more food." | "I would like more food, please." |
| `I, Need, Help` | "I need help." | "I need some help, please." |

The `You, Give, [noun]` sequence is the best demo anchor — pronoun + verb + noun hits the 1.0 dampening multiplier, and the imperative vs. polite-request fork is the widest contrast available in the current symbol set.

---

## Scope additions identified — deferred

These came out of the session review. None are in the codebase yet.

### 1. Slider zone labels

**Requirement:** Slider maps to 5 discrete stress zones (No / Low / Medium / High / Extreme), matching the distress thermometer 0–10 and Lief quintile scores 1–5.

**Decision:** Keep the continuous slider, add a zone label that updates as you drag (e.g. "Zone 3 — Medium"). This gives the continuous feel while making the discrete states visible.

**Not yet built.**

### 2. Preset self-regulation phrases

**Requirement:** Always-visible quick-tap bar above the symbol grid with four preset phrases:
- "I need a break"
- "I'm all done"
- "I need space"
- "I need to take a breath"

These map to the self-regulation / co-regulation vocabulary that SLPs and caregivers use. Tapping one sends it directly to the sentence output (bypassing the grammar engine).

**Decision:** Always visible — not triggered by stress level. Placement: above the symbol grid, inside the iPad screen.

**Not yet built.**

### 3. Biofeedback placeholder (Zone 5 / Extreme only)

**Requirement:** When stress is at Extreme (Zone 5, valence < 0.2), surface a pathway to a biofeedback exercise.

**Decision for now:** User-triggered only — no automatic interrupt. A button or indicator appears when Zone 5 is active; tapping it shows a placeholder card ("Breathing exercise — coming soon" or similar). The actual exercise UI (breathing animation, timer) is out of scope until the feature is specified.

**Not yet built.**

---

## Smoke test checklist (Task 7)

Run in Chrome with DevTools Network tab open, filtered to `api.openai.com`:

- [ ] Page loads, widget shows `😐 Neutral (simulated)` above the iPad frame
- [ ] Tap `I, Want, Food` before touching slider — ONE message in request body (no system prompt), temperature 0.3
- [ ] Drag slider to 0.10 — widget updates to `😫 High stress`
- [ ] Tap `You, Give, Water` — TWO messages: system says "anxious or highly stressed...", temperature 0.3
- [ ] Drag slider to 0.90 — widget updates to `😊 Very calm`
- [ ] Tap same symbols — system message says "very calm and engaged..."
- [ ] Console: `liefState.confidence = 0.0` — tap symbols — back to ONE message (fallback)
- [ ] Move slider to restore confidence
- [ ] Click `🫀 Connect Lief` — placeholder alert appears
