# AMIGA-AAC: Spatial Semantic UI — Concept Evaluation & Execution Path

**Concept origin:** Rohan  
**Date:** May 2026  
**Status:** Research direction — Phase II/III  
**Current build priority:** Tab navigation (Phase I)

---

## The Core Idea

Replace categorical tab navigation with a persistent spatial scene that the user navigates through embodied, topographic memory rather than menu logic. Each region of the scene is a semantic anchor (self, emotion, body, environment, intent, other people, time). Meaning is constructed by combining anchors — spatially and relationally — rather than by selecting words from lists.

The deepest insight: **pre-linguistic meaning formation maps onto space, not menus.** People think in bodies, scenes, and relationships. This architecture mirrors how meaning exists before language.

---

## What Makes This Genuinely Interesting

### 1. Spatial memory is more durable than categorical memory
Once a region of the scene is learned, it stays learned. There is no menu to remember, no tab to find. The layout is always the same. This is closer to motor planning than navigation — which is why LAMP works, and why this could work.

### 2. Relational grammar without verbs
The arrow-between-self-and-other construction replaces a large class of verbs:
- Self → arrow → other + "help" = "Help me"
- Other → arrow → self + "touch" + "not" = "I don't want you to touch me"

This is a genuine compression. It's also how some AAC researchers think about semantic primitives — meaning before syntax.

### 3. Physiology integration is the unique leverage point
This is where AMIGA diverges from every existing AAC system. If HRV or Lief biometrics indicate elevated arousal, the scene can:
- Subtly highlight the emotion or body region
- Offer a one-tap confirmation rather than a search
- Reduce the interaction to a single decision

The user doesn't have to know they're dysregulated. The system already knows and surfaces the right language.

### 4. Adaptive rendering by user profile
The same spatial model renders differently for:
- A young child: large, colorful, playful objects
- A medical setting: clean, minimal, labeled
- An advanced user: smaller targets, gesture shortcuts, fewer labels

The semantic structure is constant; the visual skin changes.

---

## What Needs to Be Resolved Before Building

### Critical concerns

**Motor accessibility.** Drag-to-combine and relational arrows require fine motor control and sustained attention that many low-verbal ASD users may not have, especially during dysregulation. Any implementation must offer a tap-only fallback path that produces the same output as the gestural path. If the gestural composition can't degrade gracefully to taps, the model fails for the core population.

**Fluency with mundane requests.** The Rohan examples (panic, sensory overload, boundaries) are high-expressivity, low-frequency events. The daily communication load is "more popcorn," "my turn," "bathroom," "I want iPad." The spatial model needs to handle these at least as efficiently as a grid. Right now it doesn't obviously do that — constructing "I want popcorn" spatially is slower than tapping a quick phrase.

**Resolution:** The quick phrase bar and high-frequency core words should remain as a flat, always-accessible layer. The spatial model sits above it as an expressive layer for emotional, relational, and contextual communication. These are not competing systems.

**Cognitive load during dysregulation.** Spatial reasoning and relational construction are executive functions — among the first to degrade under stress. The very moment AAC is most needed is the moment this model is least usable. Any spatial implementation must have a "simplified state" triggered by high arousal that collapses the scene to the 5–8 most context-relevant one-tap options.

**Learning curve and SLP adoption.** SLPs program and configure AAC devices. A spatial model with gesture grammar is harder to configure, harder to teach to caregivers, and harder to document in treatment plans than a grid with word buttons. Clinical adoption is a real constraint.

**Validation against Phase I goals.** The IRB-gated pilot at Faison is the immediate milestone. Any UI that deviates significantly from familiar AAC paradigms will face additional scrutiny and approval delays. Phase I should validate the LLM-constrained prediction layer on a familiar UI substrate. The spatial model is a Phase II research question.

---

## Interaction Grammar (What Needs to Be Defined Before Coding)

Rohan's recommendation to define the interaction grammar before touching LLM integration is correct. The grammar must be deterministic — combinations should produce predictable output without LLM involvement, with LLM used only for polishing or edge cases.

### Proposed primitive grammar

```
EXPRESSION := SUBJECT [MODIFIER] PREDICATE [OBJECT] [QUALIFIER]

SUBJECT    := self | other | we
PREDICATE  := intent | emotion | body-state | environment-state
OBJECT     := environment-element | body-part | person | abstract
MODIFIER   := negation | intensity | time
QUALIFIER  := now | again | more | stop
```

### Combination rules (deterministic)

| Combination | Output |
|---|---|
| self + intent(want) + environment(food) | "I want food" |
| self + emotion(afraid) + body(heart) + fast | "My heart is racing. I feel scared." |
| self + intent(stop) + environment(noise) | "I need the noise to stop." |
| other + arrow + self + intent(touch) + negation | "I don't want to be touched." |
| self + emotion(overwhelmed) + environment(noise) + intent(stop) | "It's too loud. I need it to stop." |
| self + time(now) + environment(bathroom) | "I need the bathroom now." |
| self + other + arrow + social(turn) | "My turn." |

This table needs to reach ~50–100 combinations before the UI can be built reliably. Gaps in the table become gaps in communication — which is clinically unacceptable.

---

## Relationship to Current Tab Architecture

The tab architecture and the spatial model are not mutually exclusive. They operate at different abstraction levels:

| Layer | Current approach | Spatial model |
|---|---|---|
| Fast access | Quick phrase bar | Quick phrase bar (keep) |
| Navigation | Tab categories | Spatial scene regions |
| Composition | Sequential symbol taps | Relational combination |
| LLM role | Sentence prediction | Grammar resolution |

A plausible evolution path:

1. **Phase I (now):** Tab navigation + quick phrase bar + LLM prediction. Standard grid interaction.
2. **Phase II:** Introduce spatial scene as an *optional* alternative view within the existing app. Users can switch between grid and scene. Gather data on which users prefer which and for what communication types.
3. **Phase III:** Spatial scene becomes the default for emotional/relational expression. Grid remains for high-frequency concrete requests. Both layers coexist.

This path preserves clinical familiarity in Phase I, allows parallel testing in Phase II, and avoids rebuilding from scratch.

---

## What Would Need to Be Built (Phase II Scope)

### New components required
- **Scene renderer:** SVG or canvas scene with persistent region anchors, responsive to screen size
- **Gesture recognizer:** tap, drag, combine — with tap-only fallback for each
- **Combination engine:** deterministic grammar table lookup, producing structured intent objects
- **Arousal-responsive layer:** biometric input → scene highlight + suggestion surface
- **Simplified state:** collapses to 5-tap mode when arousal threshold crossed
- **SLP configuration panel:** lets clinicians customize scene objects, add personalized anchors

### Data requirements
- Interaction grammar table (~100 combinations minimum before clinical use)
- User profiles: which scene configuration, which fallback triggers, which personalized anchors
- Session logs: which combinations were used, which produced correct output, which were abandoned

### Research questions to answer in Phase II
1. What is the minimum motor complexity that remains accessible during mild dysregulation?
2. Does spatial navigation actually transfer to faster expression for this population, or is it faster only for neurotypical users?
3. How do caregivers and SLPs learn to configure and extend the scene?
4. Does biometric-triggered highlighting reduce time-to-communication during escalation events?

---

## Recommendation

**Do not build this for Phase I.** The tab navigation is the right substrate for the Faison pilot — familiar, configurable, auditable by SLPs, and fast to implement.

**Do preserve the idea.** The spatial model addresses a real limitation of grid-based AAC (categorical navigation, verb lookup, relational meaning) in a way that no current commercial system does. It is a legitimate research direction and a potential differentiator in Phase II.

**Immediate next step for this concept:** Define the interaction grammar table to ~50 combinations. This is a whiteboard/document task, not a coding task. If the grammar can be made complete and deterministic, the case for building the scene renderer becomes much stronger.

**Physiology integration is the angle to protect.** Whatever the UI layer, the biometric-triggered suggestion surface is the unique AMIGA contribution. That should be implemented in Phase I on the grid, so the data and the paradigm are validated before the UI is changed underneath it.
