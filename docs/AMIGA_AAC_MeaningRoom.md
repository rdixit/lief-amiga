# 🏛️ The Meaning Room — Spatial Semantic Scene Navigation for AMIGA-AAC

*Synthesized from AMIGA-AAC meeting · 2026-05-11 · Rohan Dixit + Michael Pesavento + Joannalyn Delacruz + Gabby DeFazio*

---

## 🧭 Why We're Here — The Problem

**Validation D is complete.** AMIGA now fully covers all three AAC communication categories from the matrix — requests, emotional expression, and refusal/repair dialogue — and reached baseline functional performance on structured scenarios. But two structural tensions surfaced immediately:

1. **Literacy dependency.** The Quick Bar and tab labels rely on reading. Many users can't. Gabby was direct: *"Most of the clients who will utilize this can't read. So I think that's going to be fairly meaningless."*
2. **Scale collapse.** The full vocabulary sits at ~400 words, with ~170 live in the demo. Of those 400, ~144 have questionable category assignments or parts-of-speech classifications. The jump to 1,000 words will make the current tab structure unmanageable. As Rohan put it: *"This is kind of the fundamental problem with a lot of the AACs that exist now — insane nested menus that are so hard to use."*

LAMP's 84-cell field is overwhelming on first look. AMIGA is quicker to learn initially, but as vocabulary grows, it risks becoming the same problem in a different shape. The tab model doesn't scale. We need a different navigation paradigm entirely.

The metric that matters: **number of clicks to build a sentence.** Fewer is better. Every layer of nesting adds friction. The goal is a **wide, shallow graph** — many categories, minimal depth — but navigated spatially rather than textually.

---

## 🏷️ Naming It Correctly

In the meeting, Rohan introduced this as a **"memory palace"** approach. That framing is directionally right — it invokes spatial encoding, sensory anchoring, and intuitive retrieval — but it undersells the actual design.

Classical memory palaces are mnemonic devices for recall: you walk through a memorized space and each location holds a piece of information. What Rohan is proposing is different: the user doesn't *walk through* anything. They look at a **single persistent scene** and tap into it. The spatial layout is the *index*, not the journey.

A more precise name: **Spatial Semantic Scene Navigation.**

The shorthand we'll use internally: **The Meaning Room.**

> You're not building a better keyboard. You're building a **visual-semantic operating system for human expression.**

---

## 🖼️ The Core Concept — A World Model UI

Instead of categories arranged as tabs or folders, the user is placed **inside a simple intuitive environment** — one scene that persists across sessions. Each anchor object in that scene represents a semantic domain. Tapping an object opens its vocabulary cluster.

There is no menu to learn. There is no reading required. **Spatial memory builds fluency over time**, the same way LAMP users develop muscle memory for word locations — except the cues are visual-environmental rather than grid-positional.

This is what Gabby was already doing by hand for her Rett syndrome client using eye gaze: visual scenes with contextually clustered vocabulary. She built it on a PRC device with limited tools. What we're designing is the generalized, generative version of that insight.

---

## 🗺️ Base Scene Layout — The Meaning Room

```
           🕒
        (Time)


   🙂            👤
 (Emotion)    (Other)


        🧍
       (Self)


 ❤️            🧠
(Body)      (Mind)


   🌍            🎯
(Environment)  (Intent)
```

The **Self** is always at center. Everything radiates from it. This is not arbitrary — it mirrors the structure of embodied communication: *I feel, I want, I see, I relate.*

---

## ⚓ The Nine Anchor Objects

### 🧍 1. Self → Person in Center
The anchor of all meaning. The user's own figure.
- Tap self → *I / me*
- Drag from self → creates subject-based expressions

---

### 🙂 2. Emotion → Face / Aura Around Self
Facial expression or colored glow, optionally animated (subtle breathing/pulsing).
- 🔵 Blue = sad · 🔴 Red = angry · 🟡 Yellow = anxious · 🟢 Green = calm
- Tap emotion → attaches feeling to self
- Drag emotion → applies to other (*"they are angry"*)

---

### ❤️ 3. Body → Heart / Chest Icon
Near or inside the self figure. Pulsing = arousal.
- Tap → pain, heart, breath, tension
- Expands into body-specific primitives

---

### 🕒 4. Time → Clock on Wall
Literally a clock in the environment. Extremely intuitive — no learning required.
- Tap → now / later / before / again
- Rotate gesture → timeline selection

---

### 👤 5. Other People → Silhouette Figure
Another human outline opposite the user.
- Tap → *you / they*
- Drag toward self → relational interaction

---

### ↔️ 6. Relationships → Arrow Between People
A bidirectional arrow that appears when both self and other are selected. **This replaces a large surface area of verbs.**
- Arrow + "help" → *"help me"*
- Arrow + "hurt" → *"you hurt me"*
- Arrow + "love" → *"I love you"*

This is where Rohan's concept goes beyond tab navigation into something genuinely novel. The *relational gesture* encodes grammar spatially.

---

### 🌍 7. Environment → Background / Room Elements
Objects embedded in the scene itself.
- 💡 Light → brightness
- 🔊 Speaker → noise
- 🚪 Door → outside
- 🛏️ Bed → rest
- Tap object → context
- Adjust intensity (e.g., noise slider)

---

### 🎯 8. Intent → Tool / Action Icon (Hand or Target)
Represents *what I want to do.*
- Tap → want / need / stop / help / ask
- Drag onto objects:
  - want + water
  - stop + noise

---

### 🧠 9. Cognition → Thought Bubble / Brain
Floating near the head.
- Tap → think / know / confused / explain
- Combine with others:
  - *"I don't understand"*
  - *"I want to explain"*

---

## 💬 Example Interaction Flows

### 😰 Panic
User taps: **heart** (body) → **fast** → **emotion: afraid** → **intent: help**
→ *"My heart is racing and I feel scared. I need help."*

### 🚫 Boundary
User taps: **self** → **other person** → **arrow** → **"not"** → **"touch"** → **"now"**
→ *"I don't want you to touch me right now."*

### 🔊 Sensory Overload
User taps: **environment → noise** → **modifier: too much** → **emotion: overwhelmed** → **intent: stop**
→ *"The noise is too much. I need it to stop."*

### 🤔 Misunderstanding
User taps: **cognition: confused** → **intent: explain** → **modifier: different**
→ *"I'm confused. Let me explain differently."*

---

## 🧠 Why This Works — The Design Rationale

### 1. Embodied Cognition
People think in **space, relationships, bodies, and scenes** — not menus. The Meaning Room maps to how cognition actually works.

### 2. Zero Memorization
You don't learn: *"medical → symptoms → respiratory"*
You just: tap your chest → tap "breath" → tap "hard."

### 3. Natural Relational Grammar
Instead of selecting verbs from a list, you visually construct:
- self ↔ other
- intent → object
- emotion → self

This is **pre-linguistic meaning formation.** It removes the requirement to understand grammatical categories at all.

### 4. Shallow Graph Structure
The engineering frame (from Mike): vocabulary organized as a **balanced, wide, shallow tree**. Many categories with minimal nesting depth. Every additional click to reach a word is friction lost. The Meaning Room keeps everything one or two taps from the surface — no folder diving.

---

## ⚠️ Critical Design Constraints and Open Risks

### 1. Motor Accessibility
Gestural paths (drag-to-combine, relational arrows) require fine motor control and sustained attention that many low-verbal ASD users may not have, especially during dysregulation. **Every gestural interaction must have a tap-only fallback that produces identical output.** If a gestural composition cannot degrade gracefully to taps, the model fails for the core population.

### 2. Mundane Requests Must Be Fast
The expressive examples above (panic, sensory overload, boundaries) are high-expressivity, low-frequency events. The daily communication load is "more popcorn," "my turn," "bathroom," "I want iPad." The spatial model must handle these at least as efficiently as a grid. The **symbol-based quick phrase bar** (no text — symbols only, since these users are non-literate) remains flat and always-accessible alongside the spatial scene for high-frequency concrete requests.

### 3. Cognitive Load During Dysregulation
Spatial reasoning and relational construction are executive functions — among the first to degrade under stress. The very moment AAC is most needed is the moment this model is least usable. The system provides a **simplified state** that collapses the scene to 5–8 context-relevant one-tap options. This can trigger automatically via high arousal detection from the Lief HRV patch, or be activated manually via a **mode switch** that allows clinicians/users to toggle between spatial and simplified modes at any time. The manual toggle also enables A/B testing of both navigation paradigms.

### 4. SLP Adoption
A spatial model with gesture grammar is harder to configure, harder to teach to caregivers, and harder to document in treatment plans than a grid with word buttons. Clinical adoption is a real constraint — the system must be learnable in a single session and configurable by SLPs without engineering support.

---

## 🔬 Clinical Validation

Gabby described already doing a version of this for a client with Rett syndrome using eye gaze: a picture of the client in a pool, with all pool-related vocabulary embedded in the scene. It worked — not for building generative language analytically, but for **connection and conversational communication**, which was the appropriate goal for that client's trajectory.

Her key insight on the tradeoff: visual scenes make it harder to teach **descriptive modification** at scale (e.g., *red balloon vs. blue balloon* requires explicit representation of each variant). The Meaning Room addresses this through the **modifier + drag** interaction grammar — layering descriptors onto anchored objects rather than requiring separate scenes for each concept.

---

## 🔤 Interaction Grammar — Formal Definition

The interaction grammar must be **deterministic** — spatial combinations produce predictable structured output without LLM involvement. The LLM handles surface-form polishing only (grammatical rendering of the structured intent), not structural interpretation.

### Primitive Grammar

```
EXPRESSION := SUBJECT [MODIFIER] PREDICATE [OBJECT] [QUALIFIER]

SUBJECT    := self | other | we
PREDICATE  := intent | emotion | body-state | environment-state
OBJECT     := environment-element | body-part | person | abstract
MODIFIER   := negation | intensity | time
QUALIFIER  := now | again | more | stop
```

### Combination Rules (Deterministic)

| Combination | Output |
|---|---|
| self + intent(want) + environment(food) | "I want food" |
| self + emotion(afraid) + body(heart) + fast | "My heart is racing. I feel scared." |
| self + intent(stop) + environment(noise) | "I need the noise to stop." |
| other + arrow + self + intent(touch) + negation | "I don't want to be touched." |
| self + emotion(overwhelmed) + environment(noise) + intent(stop) | "It's too loud. I need it to stop." |
| self + time(now) + environment(bathroom) | "I need the bathroom now." |
| self + other + arrow + social(turn) | "My turn." |

### Coverage Requirement

This table must reach **~50–100 combinations** before the spatial UI can be used clinically. Gaps in the table become gaps in communication — which is clinically unacceptable. Defining the interaction grammar is a whiteboard/document task and the recommended next step before building the full spatial interaction layer.

---

## 🛠️ Implementation Pathway — Three Tiers

### Core Interaction Loop

The spatial scene is the **primary navigation surface**. The interaction loop is:

1. User sees the persistent Meaning Room scene
2. User taps an anchor object (e.g., Body, Emotion, Environment)
3. The associated **symbol grid** opens for that semantic domain
4. User selects symbols rapidly from the grid
5. System constructs utterance from selected symbols via the interaction grammar + LLM surface form

A **symbol-only quick phrase bar** (no text — these users are non-literate) is always visible for high-frequency concrete requests ("bathroom," "more," "my turn," "help"). The quick bar uses the same symbol set as the grids.

A **manual mode switch** allows toggling between spatial mode and simplified mode at any time, enabling clinician-controlled A/B testing of navigation paradigms.

### Tier 1 — MVP (This Week)
> *"The quickest thing: create the scene and add invisible buttons around objects. Tap the invisible button, it opens just the standard rectangular card grid."* — Rohan

- AI-generated scene image
- Invisible tap hotspots mapped to existing card categories
- Opens existing symbol grid for that semantic domain
- Symbol-only quick phrase bar alongside the scene
- Manual toggle to simplified (flat grid) mode
- **Tests the core navigation hypothesis with zero new infrastructure**

### Tier 2 — Spatial Consistency
- Same scene, but within each sub-view, cards maintain **consistent spatial positions** across sessions
- Builds muscle memory the way LAMP does — but anchored to scene objects rather than a grid
- Validates whether spatial persistence improves fluency

### Tier 3 — Full Interaction Grammar
- Drag + combine gestures (self → other → arrow = relational verb)
- Modifier attachment (emotion → body = "my heart hurts")
- Tap-only fallback path for every gestural interaction
- Deterministic grammar layer interpreting spatial input **before** LLM invocation
- This is the layer that makes the system feel **precise, not fuzzy**

---

## 🔮 Advanced Extensions

### 🫀 Physiology Integration
*(Lief Therapeutics — Rohan's edge)*

Lief's ECG chest patch records real-time HRV continuously. This is the intended data hook — clinical-grade, not consumer wearable. The physiological signal enters the system at two levels:

**Visual cues in the scene.** If HRV signals high arousal, the UI subtly:
- Highlights the heart anchor
- Pulses the emotion zone
- Suggests: anxious / overwhelmed

User confirms with one tap. The device is *already listening* to the body before the user speaks — and unlike a wrist wearable, the ECG patch captures this with clinical fidelity during the moments that matter most.

**Affect as a categorical prior over intent.** Beyond visual hints, the HRV signal functions as a Bayesian prior p(c | X) over communicative-intent categories. High arousal with negative valence shifts probability mass toward request, protest, and comfort-seeking; calm states shift toward description, social initiation, and labeling. This is a different (and clinically stronger) role than "sound calmer when stressed" — it's evidence about *what the child is trying to say*, not instructions about *how to say it*.

**Design constraints on the physiological layer:**
- **Baseline-relative normalization** is a clinical-safety requirement, not a refinement. Autistic populations show substantially higher inter-individual variability in autonomic baselines; population-level HRV thresholds will produce biased inferences for a meaningful fraction of users.
- **Cold-start handling:** reduced confidence for the first ~5–7 days until per-user baseline stabilizes. Affect breaks ties; it never overrides symbols.
- **Phase I validation strategy:** the affect-as-prior mechanism is validated first on the existing symbol grid, so the spatial model inherits a proven data layer rather than building on speculation.

### 👶 Adaptive Scene
- For a child → playful visuals, larger tap targets
- For medical setting → cleaner, minimal
- For advanced user → faster gestures, fewer labels

### 🔀 Simplified State and Mode Switching

The **dysregulation paradox**: the moment AAC is most needed (high arousal, distress, escalation) is the moment spatial reasoning and relational construction are least available — these are executive functions that degrade under stress.

**Arousal-triggered collapse.** When Lief HRV signals high arousal crossing a configurable threshold, the spatial scene auto-collapses to **5–8 context-relevant one-tap options** drawn from the highest-posterior communicative-intent categories (request, protest, comfort-seeking). Affect functions here as a Bayesian prior over intent categories — high arousal shifts probability mass toward urgent communicative acts, and the simplified surface reflects that shift.

**Manual mode toggle.** A persistent switch allows clinicians or users to manually toggle between spatial mode and simplified mode at any time, regardless of arousal state. This serves two purposes:
1. **Safety fallback** — if the spatial scene is overwhelming, switch to simplified immediately
2. **A/B testing** — enables direct comparison of navigation paradigms during evaluation

---

## 🔭 Phase II Direction

- Spatial scene renderer (SVG/canvas with persistent region anchors, responsive to screen size)
- Gesture recognizer with tap-only fallback for every interaction
- Deterministic combination engine (grammar table lookup producing structured intent objects)
- Arousal-responsive layer with auto-trigger for simplified state
- SLP configuration panel for scene customization (add/rearrange anchors, personalize per user)
- Key research question: does spatial navigation actually transfer to faster expression for this population, or is it faster only for neurotypical users?

---

## 🗂️ Design Constraints (Non-Negotiable)

- **Flat** — no deep menus
- **Persistent** — same scene layout always (spatial memory requires consistency)
- **Predictable** — location *is* meaning; shuffling breaks fluency

---

## ✅ Next Steps

### Full Team
- [ ] Joannalyn → ARPA meeting debrief + TDD feedback loop
- [ ] Joannalyn → design lightweight **Validation E** vocab expansion process with Gabby/Emily (week-by-week word collection + categorization)
- [ ] Joannalyn → send simplified tab/category proposal to Gabby/Emily for async review this week
- [ ] Gabby/Emily → comment on tab structure; dream freely on SLP administrative burden pain points

### Engineering (Rohan + Mike)
- [ ] **Today:** sync call to divide weekly tasks
- [ ] Rohan → sketch a simple scene using AI tools; prototype invisible tap target layout
- [ ] Mike → share vocabulary classification spreadsheet (~144 questionable classifications across ~400 total words) with full team
- [ ] Resolve: continue Tier 3 tab expansion in parallel, or pause for scene prototype first?
- [ ] Near-term: define **interaction grammar** — how spatial combinations translate deterministically (the recommended next step before full LLM layer)
- [ ] Exploratory: identify 1-2 game design references for the vocabulary learning loop (grab-the-red-balloon core loop); possible mini book club

### Research Thread (Kaleen / USC)
- [ ] Kaleen → continue literature review on unsupervised techniques for children's audio (ages 3–7)
- [ ] Explore alternative conference submission venues following Resna non-acceptance

---

*Next milestone: simple Meaning Room prototype ready for SLP feedback before next AMIGA-AAC sync.*
