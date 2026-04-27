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

**Decision:** Discrete 5-stop slider with zone label that updates as you drag (e.g. "Zone 3 — Medium stress").

**Built.** See "What was built (session 2)" above.

### 2. Preset self-regulation phrases

**Requirement:** Always-visible quick-tap bar with preset phrases ("I need a break", "I'm all done", "I need space", "I need to take a breath").

**Partial:** Break button is always visible in bottom-right of iPad screen and triggers TTS "I need a break." plus a calming modal. Additional preset phrases are documented as a future extension in the code but not built.

### 3. Biofeedback placeholder (Zone 5 / Extreme only)

**Requirement:** When stress is at Extreme (Zone 5, valence < 0.2), surface a pathway to a biofeedback exercise.

**Decision for now:** User-triggered only via Break button — no automatic trigger on Zone 5. Break modal is a child-friendly placeholder. Actual breathing exercise UI is out of scope until specified.

**Break button + modal built.** Automatic Zone 5 trigger not yet built.

---

## What was built (session 2, same day)

### Stress zones 1-5 (replaces raw valence slider)

Slider reframed from continuous valence (0-1) to discrete Lief stress zones (1-5):

| Zone | Label | Emoji | Internal valence |
|------|-------|-------|------------------|
| 1 | No stress | calm | 0.9 |
| 2 | Low stress | slightly worried | 0.7 |
| 3 | Medium stress | neutral | 0.5 |
| 4 | High stress | worried | 0.3 |
| 5 | Extreme stress | distressed | 0.1 |

Direction: left = calm (Zone 1), right = extreme (Zone 5). Matches Lief quintile numbering. Default is Zone 1 (no stress). Internal `liefState.valence` mapping is preserved so `buildAffectSystemPrompt()` works unchanged.

### Break button + break modal

- **Break button**: always visible in the bottom-right of the iPad screen. Floating, teal-ish color, labeled "Break".
- **Break modal**: child-friendly fullscreen overlay inside the iPad screen. Shows cloud icon, "Taking a break!", "It's okay to pause.", and a green "I'm ready!" button to dismiss.
- Tapping Break stops any in-progress speech and says "I need a break." via TTS (the child's voice).
- "I'm ready!" dismisses the modal and returns to the AAC grid.

### Future extension points (documented in code)

- Additional preset phrases ("I'm all done", "I need space", "I need to take a breath") can be added as buttons inside the break modal or as a quick-tap bar.
- Automatic break trigger on Zone 5 (Extreme stress) is not implemented yet — currently user-triggered only.

---

## Smoke test checklist (updated)

Run in Chrome with DevTools Network tab open, filtered to `api.openai.com`:

- [ ] Page loads, widget shows `😊 No stress (simulated)` above the iPad frame
- [ ] Slider shows 5 discrete stops (Zone 1 through Zone 5)
- [ ] Drag slider to Zone 5 — widget updates to `😫 Extreme stress`, label shows `Zone 5 — Extreme stress 😫`
- [ ] Tap `You, Give, Water` — TWO messages: system says "anxious or highly stressed...", temperature 0.3
- [ ] Drag slider to Zone 1 — widget updates to `😊 No stress`
- [ ] Tap same symbols — system message says "very calm and engaged..."
- [ ] Console: `liefState.confidence = 0.0` — tap symbols — back to ONE message (fallback)
- [ ] Move slider to restore confidence
- [ ] Click `🫀 Connect Lief` — placeholder alert appears
- [ ] Click Break button — modal appears, TTS says "I need a break."
- [ ] Click "I'm ready!" — modal dismisses, AAC grid is visible again
