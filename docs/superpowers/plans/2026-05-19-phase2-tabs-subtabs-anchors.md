# Phase 2: Tabs, Subtabs, and Anchors — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` (or `superpowers:subagent-driven-development` for parallelizable tasks) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Date:** 2026-05-19
**Branch:** `mjp/vocab_tier3`
**Source plan:** `docs/phase2-tabs-subtabs-anchors.md` (original Phase 2 design — read for full context, open questions, and projected anchor sizes)
**Workflow docs:** `docs/vocabulary-update-guide.md` (audit + validation pipeline used in this plan)

---

## Goal

Activate the full 8-tab layout, create the two missing meaning-room anchors (`cognition`, `more_scene`), assign all 195 unanchored Tier 3 symbols to anchors, add subtabs to large tabs, and surface multi-tab symbols correctly in the grid view.

## Prerequisites (DONE — verified state)

This plan starts from the clean state reached at the end of the 2026-05-19 vocabulary cleaning pass.

- ✅ All 436 symbols have validated category, POS, tab, and (where applicable) anchor data
- ✅ `data/canonical_vocabulary.csv` ↔ `vocabulary.json` ↔ `meaning_room.json` ↔ `data/vocabulary_union_table.csv` round-trip is clean
- ✅ `data/category_config.csv` reflects current rules (including `Regulation/Safety` → `calm_corner; time`)
- ✅ Tooling consolidated to: `vocab_sync` ↔ `build_union_table` ↔ `sanity_check_union` ↔ `generate_vocab_review` ↔ `apply_vocab_review` ↔ `backprop_union_table`
- ✅ Stale migration scripts archived to `scripts/_archive/`; stale data files renamed to `*.RETIRED.csv`
- ✅ 25 sanity-check flags remain, all on the `INTENTIONAL_OVERRIDES` list in `generate_vocab_review.py`

### Quick re-verification (run before starting)

```bash
python3 scripts/build_union_table.py        # expect: 11 collision flags (known)
python3 scripts/sanity_check_union.py       # expect: 25 symbols flagged (all known)
python3 scripts/generate_vocab_review.py    # expect: 0 rows (nothing needing decision)
python3 scripts/backprop_union_table.py     # expect: "Nothing to do"
python3 scripts/vocab_sync.py diff          # expect: 0 diffs
```

---

## Starting-state snapshot

### Tab counts (current, after cleaning pass)

| Tab | Symbols | Rendered in app? |
|-----|---------|------------------|
| more | 126 | Yes |
| actions | 85 | Yes |
| things | 74 | Yes |
| people | 49 | Yes |
| core | 36 | Yes |
| describe | **25** | **No — needs tab def** |
| feelings | 22 | Yes |
| food | **19** | **No — needs tab def** |

### Anchors (current)

12 active: `actions(42), toys(42), other_people(28), colors_descriptors(25), outside(22), self(20), feelings(20), food_drink(20), stop_refusal(14), calm_corner(12), clothing(8), time(1)`.

Missing / to create: `more_scene` (new), `cognition` (currently in `deferred_anchors`).
Still deferred after this phase: `body`, `relationships`.

### Unanchored: 195 symbols (all T3)

| Category | Count | Default anchor (from `data/category_config.csv`) |
|----------|------:|--------------------------------------------------|
| Actions | 56 | `actions; toys; outside` *(see Decision 1)* |
| Function/Core | 43 | `more_scene` *(blocked until created)* |
| Descriptors | 36 | `colors_descriptors` |
| Uncategorized | 29 | `more_scene` *(blocked until created)* |
| People/Pronouns/Possessives | 20 | `self; other_people` |
| Question Words | 9 | `cognition` *(blocked until created)* |
| Social | 2 | `other_people; actions` |

### Multi-tab symbols (current, 16)

Already set via `secondary_tabs`: most are core-tab phrases also surfacing in `actions`. Two `things;actions` (slide/swing), two `food;actions` (eat/drink), one `core;describe` (good). The app does NOT yet filter on `additional_tabs` — Task 1 fixes this.

---

## Decisions to confirm BEFORE starting

Each of these changes the size of the work. Do not start the plan until they are answered (the original plan document — `docs/phase2-tabs-subtabs-anchors.md` — has more context for each).

- [ ] **D1 — Verb duplication scope.** Auto-assign all `Actions` words to `actions + toys + outside` (full duplication per category_config), or *primary-only* with selective duplication for contextual verbs (`eat`/`drink`→food_drink, `play`/`jump`→toys)? Affects anchor sizes drastically (toys: 42→95 vs ~50; outside: 22→82 vs ~30).
- [ ] **D2 — Descriptors in `more` tab.** Move the 31 Descriptors currently in `ui_tab=more` to `ui_tab=describe`? Would bring `more` to ~95 and `describe` to ~56.
- [ ] **D3 — Multi-tab expansion.** Beyond the 16 already set, which words/phrases should also be multi-tab? Candidates listed in original plan §6.
- [ ] **D4 — Anchor-grid subtabs.** Same pill UI as tab subtabs, or simpler (section headers)?
- [ ] **D5 — Negation pill in `more`.** The 6 negation auxiliaries in `more` (`arent, cant, couldnt, havent, not, wont`) — get a "Negation" subtab pill, or stay unsorted?
- [ ] **D6 — Anchor labels.** Confirm `cognition` label ("Think" vs "Questions") and `more_scene` label ("More" vs "Toolbox" vs other). Confirm hotspot positions (current proposals are tunable estimates).

---

## Task 1: Activate `food` and `describe` tabs + enable multi-tab filter

**Goal:** Make the 19 `food`-tab and 25 `describe`-tab symbols visible in the app, and have the grid include `additional_tabs` membership.

**Files:**
- Modify: `vocabulary.json` (`tabs` array)
- Modify: `app.js` (`getGridSymbols`)
- Modify: `style.css` (tab pill styles if tab count change affects layout)

**Steps:**
- [ ] **1.1** Add the two new tab definitions to `vocabulary.json` `tabs` array:
  ```json
  { "id": "food",     "label": "Food",     "emoji": "🍎", "description": "Food and drinks",            "color": "#f97316" }
  { "id": "describe", "label": "Describe", "emoji": "🎨", "description": "Colors, sizes, descriptions", "color": "#8b5cf6" }
  ```
  Confirm emoji + color with the team if needed.
- [ ] **1.2** Update `getGridSymbols(activeTab)` in `app.js` to include symbols whose `additional_tabs` contains `activeTab`:
  ```js
  let syms = SYMBOLS.filter(s =>
    s.ui_tab === activeTab ||
    (s.additional_tabs && s.additional_tabs.includes(activeTab))
  );
  ```
- [ ] **1.3** Manually open the app and confirm the new tab pills render and each shows the expected count of symbols. Spot-check that `slide`/`swing` appear in both `things` and `actions`, and `drink`/`eat` in both `food` and `actions`.
- [ ] **1.4** No data changes here — `vocab_sync.py diff` should still report zero diffs.

---

## Task 2: Create `cognition` and `more_scene` anchors

**Goal:** Add the two missing anchors to `meaning_room.json` with hotspots, labels, icons, and (for `cognition`) initial membership.

**Files:**
- Modify: `meaning_room.json`

**Steps:**
- [ ] **2.1 — `cognition` anchor.** Add to the `anchors` array (final position/hotspot tunable):
  ```json
  {
    "id": "cognition",
    "label": "Think",
    "icon": "🧠",
    "hotspot": { "x": 0.28, "y": 0.02, "w": 0.10, "h": 0.12 },
    "symbol_ids": ["what", "whats", "when", "where", "wheres", "which", "who", "why", "how"],
    "stress_glow_curve": null
  }
  ```
  Verify those 9 `Question Words` ids exist in `vocabulary.json`.
- [ ] **2.2 — `more_scene` anchor.** Add (hotspot in unoccupied scene area):
  ```json
  {
    "id": "more_scene",
    "label": "More",
    "icon": "📦",
    "hotspot": { "x": 0.48, "y": 0.02, "w": 0.12, "h": 0.12 },
    "symbol_ids": [],
    "stress_glow_curve": null
  }
  ```
  Initial membership comes from Task 3.
- [ ] **2.3** Remove `"cognition"` from `deferred_anchors`. Leave `body` and `relationships` deferred.
- [ ] **2.4** Visually verify both hotspots render and don't overlap other anchors (open app in browser, switch to Meaning Room view).

---

## Task 3: Auto-assign 195 unanchored T3 symbols

**Goal:** Push all unanchored T3 symbols into their category's default anchor(s), per the answer to Decision **D1**.

**Two paths depending on D1:**

### Path A — full duplication (use `category_config.csv` defaults exactly)

- [ ] **3.A.1** Write `scripts/assign_t3_anchors.py` (new): reads `canonical_vocabulary.csv` + `meaning_room.json`, finds every T3 symbol with no anchor membership, and adds it to the `symbol_ids` array of every anchor listed in its category's `default_anchors`. Skips if the target anchor doesn't exist (sanity guard). Dry-run by default, `--apply` to write.
- [ ] **3.A.2** Dry-run and review the per-anchor delta. Expected sizes after: actions~100, toys~95, outside~82, more_scene~73, colors_descriptors~57, self~40, other_people~51, cognition~9.

### Path B — primary-only with selective duplication

- [ ] **3.B.1** Update `category_config.csv` `default_anchors` for `Actions` to only `actions` (drop `toys`, `outside`).
- [ ] **3.B.2** Decide explicit duplication list — e.g. `eat, drink → food_drink`; `play, jump, run, ride → toys`; `walk, run, jump, ride, go, come → outside`. Capture as `secondary_tabs` / additional anchor list inline in `canonical_vocabulary.csv` or in a separate mapping CSV.
- [ ] **3.B.3** Implement assignment script as in 3.A.1 but using primary anchor for default cases + the duplication list for specific verbs.
- [ ] **3.B.4** Dry-run and confirm anchor sizes are reasonable (target: no anchor > ~50 without justifying subtabs).

### Both paths

- [ ] **3.X.1** Apply, then run the full verification sweep:
  ```bash
  python3 scripts/build_union_table.py
  python3 scripts/sanity_check_union.py
  python3 scripts/backprop_union_table.py        # expect "Nothing to do"
  python3 scripts/vocab_sync.py diff             # expect 0 diffs
  ```
- [ ] **3.X.2** Confirm `unanchored` count drops to 0 (or only the deferred categories) using:
  ```bash
  python3 -c "import csv; n = sum(1 for r in csv.DictReader(open('data/vocabulary_union_table.csv')) if not r['meaning_room_anchors'].strip()); print(f'Unanchored: {n}')"
  ```

---

## Task 4: Subtabs — data layer

**Goal:** Encode the subtab structure in `data/category_config.csv` so both the tab grid and anchor grid can read consistent labels.

**Files:**
- Modify: `data/category_config.csv` (`subtab_label` column already exists)
- Modify: `vocabulary.json` (if subtab info needs to propagate to runtime)
- Modify: `scripts/vocab_sync.py` (only if new fields need syncing)

**Steps:**
- [ ] **4.1** Add `subtab_label` to categories that currently lack one:
  | Category | Tab | Subtab label |
  |---|---|---|
  | Function/Core | more | Grammar |
  | Uncategorized | more | Other |
  | Question Words | more | Questions |
  | Negation/Repair (in `more`) | more | Negation *(only if D5 = yes)* |
- [ ] **4.2** If D2 is yes (Descriptors → describe), update those rows in `canonical_vocabulary.csv` (`ui_tab=describe`), sync, and re-verify.
- [ ] **4.3** Round-trip: `vocab_sync.py import --apply`, `build_union_table.py`, `sanity_check_union.py`, `backprop_union_table.py` (dry).

---

## Task 5: Subtabs — UI layer (tab grid)

**Goal:** Render filter pills above the grid for any tab with subtab metadata.

**Files:**
- Modify: `app.js` (grid render)
- Modify: `style.css` (pill row styling)

**Steps:**
- [ ] **5.1** Read `subtab_label` from `category_config` (or pre-baked into `vocabulary.json` at load) when rendering a tab's grid. Compute subtab buckets by grouping symbols on `category_xls → subtab_label`. Render pills only when the active tab has ≥2 distinct subtab labels.
- [ ] **5.2** `actions` tab special case: split by `type` (`word` → "Verbs", `phrase` → "Phrases") instead of category.
- [ ] **5.3** Subtab interactions: "All" pill defaults active; tapping a pill filters in place. State is per-tab and persists in `localStorage`.
- [ ] **5.4** Style pills consistently with existing UI; ensure tap targets ≥44pt.
- [ ] **5.5** Manual QA: open each tab, confirm pill row appears only for tabs needing it, counts add up, and filter works.

---

## Task 6: Subtabs — anchor grid

**Goal:** Apply the same subtab pattern to anchor grids that have grown past ~40 symbols.

**Files:**
- Modify: `app.js` (anchor grid render)
- Modify: `style.css` (pill row already styled from Task 5)

**Steps:**
- [ ] **6.1** Per D4: if "same as tab subtabs", reuse Task 5's pill-row component in the anchor-grid view. If "simpler", render section headers within the grid for each subtab bucket.
- [ ] **6.2** Anchors needing subtabs after Task 3:
  - `actions` (~100): split by `type` (Verbs / Phrases) OR semantic group — confirm with team
  - `more_scene` (~73): Grammar (Function/Core) | Other (Uncategorized)
  - `toys`, `outside`: subtabs depend on D1 outcome
- [ ] **6.3** Manual QA on the meaning-room view.

---

## Task 7: Multi-tab expansion (optional, depends on D3)

**Goal:** Expand `secondary_tabs` membership for additional words/phrases beyond the 16 already set.

**Files:**
- Modify: `data/canonical_vocabulary.csv` (then sync)

**Steps:**
- [ ] **7.1** Update `secondary_tabs` in `canonical_vocabulary.csv` for the additional symbols decided in D3. Use the standard pipeline:
  ```bash
  python3 scripts/vocab_sync.py import --apply
  python3 scripts/build_union_table.py
  python3 scripts/sanity_check_union.py
  python3 scripts/backprop_union_table.py        # expect "Nothing to do"
  ```
- [ ] **7.2** Manual QA in the app: confirm each new multi-tab symbol appears in all expected tabs.

---

## Task 8: Final validation and docs

- [ ] **8.1** Full round-trip sanity:
  ```bash
  python3 scripts/build_union_table.py
  python3 scripts/sanity_check_union.py
  python3 scripts/generate_vocab_review.py        # expect 0 rows
  python3 scripts/backprop_union_table.py         # expect "Nothing to do"
  python3 scripts/vocab_sync.py diff              # expect 0 diffs
  ```
- [ ] **8.2** Confirm zero `orphan-tier-1-2` flags and zero `unassigned` symbols (modulo deferred categories).
- [ ] **8.3** Update `docs/vocabulary-update-guide.md` if any new column / convention was introduced (e.g. anchor subtab mapping).
- [ ] **8.4** Update `docs/AMIGA_AAC_MeaningRoom.md` with the two new anchors (purpose, hotspot, default symbols).
- [ ] **8.5** Update or retire `docs/phase2-tabs-subtabs-anchors.md` — mark the original plan superseded by this implementation and link the new sections of the user-facing docs.
- [ ] **8.6** Optional: write a brief `docs/release-notes-phase2.md` summarizing what changed for the team (Joannalyn, Gabby).

---

## Exit criteria

- [ ] All 8 tabs render in the app with non-empty grids (where data exists)
- [ ] `cognition` and `more_scene` anchors are clickable in the Meaning Room and show their grids
- [ ] Zero unanchored T1 or T2 symbols; zero unanchored T3 except in any explicitly deferred categories
- [ ] Subtab pills render on tabs with ≥2 subtab labels and filter the grid in place
- [ ] Multi-tab symbols (≥16 today, more after D3) surface in every tab they belong to
- [ ] Full round-trip remains clean (5 verification commands above all pass)
- [ ] Docs reflect the final state

---

## Out of scope (explicit non-goals)

- Generating new SVG icons for symbols (handled by `scripts/generate_symbols.py` independently)
- Creating the `body` or `relationships` anchors (still deferred)
- The SLP vocabulary update from `data/ValidationE-vocabupdate.csv` — handled as a separate workstream after Phase 2 settles
- Stress-glow tuning for the new anchors (use defaults initially; tune in a follow-up)

---

## Rollback

Every data change in this plan flows through the standard pipeline. To undo any task's data effects:

1. `git diff data/canonical_vocabulary.csv meaning_room.json vocabulary.json data/category_config.csv` — review
2. `git checkout -- <file>` to revert
3. Re-run `vocab_sync.py import --apply` and `build_union_table.py` to bring derived files back in sync

App-layer changes (Tasks 1, 5, 6) are pure code and revert via `git`.

---

## References

- `docs/phase2-tabs-subtabs-anchors.md` — original Phase 2 design notes (context, full open-question rationale)
- `docs/vocabulary-update-guide.md` — current canonical/JSON/union-table workflow
- `docs/AMIGA_AAC_MeaningRoom.md` — meaning room conceptual reference
- `docs/superpowers/plans/2026-05-14-meaning-room.md` — foundational meaning-room implementation (completed)
- `data/category_config.csv` — category → tab/anchor/subtab mappings (single source of truth for rules)
