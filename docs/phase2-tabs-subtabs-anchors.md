# Phase 2: Tabs, Subtabs, and Anchors

> **STATUS: SUPERSEDED** — This design document has been implemented. See `docs/superpowers/plans/2026-05-19-phase2-tabs-subtabs-anchors.md` for the executed implementation plan.

**Date:** 2026-05-19
**Branch:** `mjp/vocab_tier3`
**Prereq:** Phase 1 is complete — all 436 symbols have validated categories, POS, tabs, and partial anchor assignments. Data is in sync across canonical_vocabulary.csv, vocabulary.json, and meaning_room.json.

---

## Current State

### Tabs (8 target, 6 rendered)

Symbols already have the correct 8-tab `ui_tab` values, but `vocabulary.json` only defines 6 tabs. Symbols with `ui_tab=food` (19) and `ui_tab=describe` (22) are invisible in the app.

| Tab | Symbols | Exists in app? |
|-----|---------|----------------|
| more | 129 | Yes |
| actions | 85 | Yes |
| things | 74 | Yes |
| people | 49 | Yes |
| core | 36 | Yes |
| feelings | 22 | Yes |
| **describe** | **22** | **No — needs tab definition** |
| **food** | **19** | **No — needs tab definition** |

### Anchors (12 active, 2 to add)

| Anchor | Current symbols | Status |
|--------|----------------|--------|
| actions | 43 | Active |
| toys | 41 | Active |
| other_people | 28 | Active |
| outside | 23 | Active |
| self | 20 | Active |
| feelings | 20 | Active |
| food_drink | 20 | Active |
| colors_descriptors | 20 | Active |
| stop_refusal | 14 | Active |
| calm_corner | 12 | Active |
| clothing | 8 | Active |
| time | 1 | Active |
| **cognition** | **0** | **Deferred — needs creation** |
| **more_scene** | **0** | **Does not exist — needs creation** |

**Deferred anchors:** `body`, `cognition`, `relationships`

### Unanchored symbols: 199 (all T3)

| Category | Count | Target anchor(s) from category_config |
|----------|-------|---------------------------------------|
| Actions | 54 | `actions; toys; outside` (verb duplication pattern) |
| Function/Core | 38 | `more_scene` (blocked — anchor doesn't exist) |
| Descriptors | 35 | `colors_descriptors` |
| Uncategorized | 35 | `more_scene` (blocked — anchor doesn't exist) |
| People/Pronouns/Possessives | 20 | `self; other_people` |
| Question Words | 9 | `cognition` (blocked — anchor deferred) |
| Places | 5 | `outside` |
| Social | 3 | `other_people; actions` |

### Multi-tab symbols (current)

Only 2 symbols currently use `additional_tabs`:
- `slide`: primary=things, additional=[actions]
- `swing`: primary=things, additional=[actions]

The app does NOT yet filter on `additional_tabs` — `getGridSymbols()` only matches `ui_tab === activeTab`.

---

## Step 1: Add food and describe tab definitions

Add to `vocabulary.json` `tabs` array:

```json
{ "id": "food", "label": "Food", "emoji": "🍎", "description": "Food and drinks", "color": "#f97316" }
{ "id": "describe", "label": "Describe", "emoji": "🎨", "description": "Colors, sizes, and descriptions", "color": "#8b5cf6" }
```

Update `getGridSymbols()` in `app.js` to include secondary tab symbols:

```javascript
let syms = SYMBOLS.filter(s =>
  s.ui_tab === activeTab ||
  (s.additional_tabs && s.additional_tabs.includes(activeTab))
);
```

This activates the 8-tab layout and multi-tab support in one step.

---

## Step 2: Create cognition and more_scene anchors

### cognition
- **Purpose:** Spatial home for question words and thinking-related words
- **Label:** "Think" (or "Questions" — SLP decision)
- **Icon:** 🧠
- **Hotspot:** Near child's head area (approx `{ x: 0.28, y: 0.02, w: 0.10, h: 0.12 }` — tunable)
- **Initial symbol_ids:** 9 Question Words from T3: `what`, `whats`, `when`, `where`, `wheres`, `which`, `who`, `why`, `how`
- **Duplication candidates:** `know` (currently in actions), `confused` (currently in feelings) — duplicate into cognition per the verb duplication pattern
- **Remove from** `deferred_anchors`

### more_scene
- **Purpose:** Toolbox/drawer for grammar words, function words, and uncategorized overflow
- **Label:** "More"
- **Icon:** 📦
- **Hotspot:** Unoccupied scene area (approx `{ x: 0.48, y: 0.02, w: 0.12, h: 0.12 }` — tunable)
- **Initial symbol_ids:** 73 T3 words (38 Function/Core + 35 Uncategorized)
- **Note:** This is a new anchor, not currently in `deferred_anchors` — just add it

---

## Step 3: Auto-assign T3 words to anchors

Use `category_config.csv` `default_anchors` to assign all 199 unanchored T3 symbols to their anchors. Write to `meaning_room.json` and update the union table.

**Projected anchor sizes after assignment:**

| Anchor | Current | + New | = Total | Needs subtabs? |
|--------|---------|-------|---------|----------------|
| actions | 43 | +57 | **100** | **Yes** |
| toys | 41 | +54 | **95** | **Yes — but see note** |
| outside | 23 | +59 | **82** | **Yes — but see note** |
| more_scene | 0 | +73 | **73** | **Yes** |
| colors_descriptors | 20 | +35 | **55** | Maybe |
| other_people | 28 | +23 | **51** | Maybe |
| self | 20 | +20 | **40** | No |
| feelings | 20 | +0 | 20 | No |
| food_drink | 20 | +0 | 20 | No |
| stop_refusal | 14 | +0 | 14 | No |
| calm_corner | 12 | +0 | 12 | No |
| cognition | 0 | +9 | **9** | No |
| clothing | 8 | +0 | 8 | No |
| time | 1 | +0 | 1 | No |

**Note on verb duplication:** Actions verbs get duplicated into `actions` + `toys` + `outside` per the config. This means `toys` and `outside` balloon because they inherit ALL action verbs. This may be too aggressive — we may want the primary anchor only (`actions`) for most verbs, with contextual duplication only for specific verbs (e.g., `eat`/`drink` → `food_drink`, `play`/`jump` → `toys`). **Decision needed: auto-assign all Actions to all 3 anchors, or primary-only with selective duplication?**

---

## Step 4: Subtabs for grid view tabs

Tabs over ~40 symbols benefit from subtab filter pills. Based on current counts:

### things (74 symbols) — subtabs by category

| Subtab | Category | Count |
|--------|----------|-------|
| Toys | Preferred Items + Vehicles | 39 |
| Body | Body Parts | 15 |
| Places | Places | 9 |
| Clothes | Clothing | 7 |

Already defined via `subtab_label` in `category_config.csv`.

### more (129 symbols) — subtabs by category

| Subtab | Category | Count |
|--------|----------|-------|
| Grammar | Function/Core | 36 |
| Other | Uncategorized | 35 |
| Describe | Descriptors | 31 |
| Questions | Question Words | 9 |
| Negation | Negation/Repair | 6 |
| (remaining) | Actions (6), Places (5), Social (1) | 12 |

Needs `subtab_label` added to `category_config.csv` for: Function/Core → "Grammar", Uncategorized → "Other", Question Words → "Questions". Negation/Repair currently maps to `core` tab default, but the 6 words in `more` (arent, cant, etc.) need a "Negation" subtab label when they're in the `more` tab.

**Open question:** Should Descriptors (31) in the `more` tab migrate to `describe` tab? They have `ui_tab=more` currently. If moved, `more` drops to 98 and `describe` goes to 53.

### actions (85 symbols) — subtabs by type (word vs phrase)

| Subtab | Filter | Count |
|--------|--------|-------|
| Verbs | type=word | 76 |
| Phrases | type=phrase | 9 |

This is the one exception to category-driven subtabs — it splits by the `type` field.

### Tabs that do NOT need subtabs

- **people** (49): One dominant category. Borderline, but manageable.
- **core** (36): Small enough.
- **feelings** (22): Small.
- **describe** (22): Small (53 if descriptors migrate from `more`).
- **food** (19): Small.

---

## Step 5: Subtabs for anchor grids

The anchor grid view (clicking a hotspot in the meaning room) also needs subtabs for large anchors:

### actions anchor (100 projected) — subtabs by type or semantic group

Options:
- **By type:** Verbs (word) vs Phrases (phrase) — same as tab subtabs
- **By semantic group:** Movement, Communication, Creation, etc.

### more_scene anchor (73 projected) — subtabs by category

- Grammar (Function/Core) | Other (Uncategorized)

### toys anchor (95 projected) — review needed

95 is inflated by verb duplication. If we limit to primary-anchor-only for most verbs, `toys` stays closer to ~41. Otherwise needs subtabs.

### outside anchor (82 projected) — review needed

Same verb duplication concern. Without the duplicated verbs, `outside` stays around ~28.

---

## Step 6: Multi-tab support

### Current mechanism

- `ui_tab`: primary tab (single value)
- `additional_tabs` (JSON) / `secondary_tabs` (CSV): array of extra tabs

### Candidates for multi-tab

Currently only `slide` and `swing` use this. Other candidates:

| Symbol | Primary tab | Also belongs in | Rationale |
|--------|------------|-----------------|-----------|
| eat, drink | food | actions | Action verbs about food |
| break, sleep | core | actions | Action verbs used for regulation |
| help, want | core | actions | Core accessibility words that are verbs |
| i want water, i want food | core or food | actions | Request phrases |

**Decision needed:** Which phrases/words should appear in multiple tabs? The `secondary_tabs` mechanism already exists in the data pipeline — just needs values set and the app filter updated.

---

## Step 7: Validation and cleanup

1. Rebuild union table: `python3 scripts/build_union_table.py`
2. Verify zero collision flags: all tabs should match anchor expectations
3. Run sanity check: `python3 scripts/sanity_check_union.py`
4. Sync check: `python3 scripts/vocab_sync.py diff`
5. Update docs: `vocabulary-tiers.md`, `vocabulary-update-guide.md`

---

## Implementation order

```
Step 1: Add food/describe tab definitions + multi-tab filter  (app.js, vocabulary.json)
Step 2: Create cognition + more_scene anchors                 (meaning_room.json)
Step 3: Auto-assign T3 to anchors                             (meaning_room.json, union table)
Step 4: Add subtab config to category_config.csv              (data layer)
Step 5: Build subtab UI in app.js + style.css                 (app layer)
Step 6: Set additional_tabs for multi-tab words               (data layer)
Step 7: Validate and clean up                                 (scripts)
```

## Open decisions

1. **Verb duplication scope:** Auto-assign all Actions to 3 anchors (actions + toys + outside), or primary-only with selective duplication for contextual verbs?
2. **Descriptors in more tab:** Move the 31 Descriptors from `more` to `describe`, or keep them?
3. **Multi-tab candidates:** Which words/phrases should appear in multiple tabs?
4. **Anchor grid subtabs:** Same mechanism as tab subtabs, or simpler (e.g., just section headers)?
5. **Negation in more:** The 6 negation words (arent, cant, etc.) in `more` — do they get their own subtab pill or stay unsorted?
