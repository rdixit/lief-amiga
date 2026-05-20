# LiefAAC

A browser-based AAC (Augmentative and Alternative Communication) prototype for the AMIGA project. Designed for non-speaking individuals, with a focus on LAMP (Language Acquisition through Motor Planning) compatibility — consistent symbol positions, stress-aware highlighting, and Fitzgerald Key color coding.

---

## Running the app

ES modules require a local HTTP server (direct `file://` open won't work):

```bash
python3 -m http.server 8001
```

Then open [http://localhost:8001](http://localhost:8001) in your browser.

**URL parameters for development:**

| Parameter | Effect |
|---|---|
| `?view=meaning_room` | Force the Meaning Room view on load |
| `?view=grid_tabs` | Force the tab grid view on load |
| `?debug` | Show hotspot bounding boxes as red overlays |

---

## Key files

| File | Purpose |
|---|---|
| `vocabulary.json` | Source of truth — all symbols, tabs, tiers, POS, Meaning Room config |
| `meaning_room.json` | Meaning Room scene config — image, anchor hotspots, symbol mappings, glow curves |
| `symbols.js` | ES module mapping `symbol_id` → SVG string |
| `app.js` | Application logic — view state machine, glow engine, sentence builder |
| `style.css` | All styles including iPad frame, hotspot glow, and pulse animation |
| `scripts/generate_symbols.py` | Regenerate `symbols.js` from `vocabulary.json` |
| `scripts/vocab_sync.py` | Bidirectional sync between `vocabulary.json` and the canonical CSV |
| `scripts/build_union_table.py` | Cross-system collision audit joining vocab, tabs, and Meaning Room |
| `scripts/sanity_check_union.py` | Validate the union table against `data/category_config.csv` rules |
| `scripts/generate_vocab_review.py` | Curated, decision-oriented subset of sanity findings |
| `scripts/apply_vocab_review.py` | Apply marked rows from `vocab_review.csv` to canonical + meaning_room |
| `scripts/backprop_union_table.py` | Alternate writeback: union table → canonical + meaning_room |

---

## UI overview

The app has three views, controlled by a toggle button (bottom-left) and persisted in `localStorage`:

### Meaning Room (default)
A spatial scene showing a child's room. Each object is a tappable anchor leading to a focused symbol grid for that category. Anchors glow softly at all times; stress-sensitive anchors (Feelings, Stop, Calm) escalate and pulse at high stress zones.

- **Stress glow** — driven by the Lief HRV device (or the simulated slider); only anchors with a `stress_glow_curve` in `meaning_room.json` escalate at high stress
- **Anchor tap** — opens a grid of symbols associated with that anchor; tapping a symbol adds it to the sentence bar and returns to the scene
- **Back to scene** — available at any time while browsing an anchor grid

### Tab Grid
The original grid view with 6 tabs: Core · Actions · Feelings · People · Things · More.

### Controls (always visible)

| Control | Default | Effect |
|---|---|---|
| Sort by frequency | On | Within each tier, sorts by number of source word lists, then alphabetically |
| Reorder by stress | Off | Shifts stress-highlighted symbols to the front of the grid |
| Symbol color key | — | Opens Fitzgerald Key color legend popup |
| Break | — | Launches 60-second breathing exercise |

---

## Meaning Room configuration

`meaning_room.json` controls the entire Meaning Room layout. Edit this file to adjust anchor positions, symbol mappings, or glow curves without touching code.

```jsonc
{
  "image": "assets/images/meaning_room_v0_1600x900.png",
  "image_natural_size": [1600, 900],
  "default_glow_intensity": 0.50,
  "stress_glow_curve_default": [0.35, 0.37, 0.40, 0.43, 0.46],
  "anchors": [
    {
      "id": "calm_corner",
      "label": "Calm",
      "icon": "🧘",
      "hotspot": { "x": 0.50, "y": 0.36, "w": 0.17, "h": 0.32 },
      "symbol_ids": ["i_need_a_break", "break", "too_loud", ...],
      "stress_glow_curve": [0.48, 0.60, 0.75, 0.90, 1.00]
    }
  ]
}
```

**Anchor fields:**

| Field | Description |
|---|---|
| `hotspot` | `x, y, w, h` as fractions of image width/height (0–1) |
| `symbol_ids` | Ordered list of `vocabulary.json` symbol IDs shown in the anchor grid |
| `stress_glow_curve` | 5-value array (zones 1–5); `null` = use default flat curve; presence also enables pulse animation at zones 4–5 |
| `icon` | Optional emoji rendered over the hotspot for disambiguation |

`vocabulary.json` → `app_config` sets the default view and toggle visibility:

```json
"app_config": {
  "default_view": "meaning_room",
  "show_view_toggle": true
}
```

---

## Vocabulary

`vocabulary.json` contains 431 symbols drawn from the AMIGA AAC Expansion Packet (v4.5.2026) and AMIGA-AAC additions. Each symbol has:

| Field | Description |
|---|---|
| `id` | Snake_case identifier, matches key in `symbols.js` |
| `display_label` | Human-readable label shown on the card |
| `ui_tab` | Runtime tab assignment: `core`, `actions`, `feelings`, `people`, `things`, `more` |
| `priority_tier` | `1` (MVP core) · `2` (Faison expansion) · `3` (reference, hidden by default) |
| `part_of_speech` | Fitzgerald Key role: `verb/action`, `noun`, `descriptor/adjective`, `pronoun/person`, `location/preposition`, `negation/repair`, `phrase`, `question word`, `word` |
| `phrase_pos` | For phrase-type symbols only: the head word's linguistic POS (e.g., `verb/action` for "help me") |
| `sources` | Source word lists the symbol appears in (used for frequency sort) |
| `allowed_for_grid` | `true` for Tier 1 and 2; `false` for Tier 3 |

**180 symbols** are currently live in the grid (Tier 1: 58, Tier 2: 122 — includes 7 new feelings words added for Meaning Room coverage).

All tier-1 and tier-2 symbols with `allowed_for_grid: true` are assigned to at least one Meaning Room anchor; this is enforced by the test suite.

### Fitzgerald Key colors

Symbol cards show a subtle background tint by grammatical role:

| Color | Role |
|---|---|
| 🟡 Yellow | Pronouns |
| 🟢 Green | Verbs / actions |
| 🔵 Blue | Nouns / things |
| 🟠 Orange | Prepositions / location |
| 🟣 Purple | Descriptors / adjectives |
| 🔴 Red | Negation / repair |
| 🩷 Pink | Phrases |
| ⬜ Gray | Function words (articles, conjunctions, interjections) |
| 🩵 Cyan | Question words |

---

## Tests

```bash
npm test
```

Uses Node's built-in test runner (`node:test`) — no install required. Runs `tests/data/vocab_coverage.test.js` (77 tests, ~100ms).

**What is tested:**

| Suite | Checks |
|---|---|
| `meaning_room.json schema` | Required anchor fields, hotspot bounds (x+w ≤ 1, y+h ≤ 1), glow curve length and range |
| `symbol resolution` | Every `symbol_id` exists in `vocabulary.json`, has `allowed_for_grid: true`, no duplicates within an anchor |
| `tier coverage` | Every tier-1 and tier-2 grid symbol appears in at least one anchor |
| `stress glow integrity` | Glow values in `[0,1]`, curves are monotonically non-decreasing |
| `POS integrity` | Valid POS on every symbol, phrase-type consistency, CSS rule coverage, no curly quotes |

---

## Scripts

### `scripts/generate_symbols.py`

Regenerates `symbols.js` from `vocabulary.json`. Backs up existing `vocabulary.json` and `symbols.js` to `data/` with a datestamp before overwriting.

```bash
python3 scripts/generate_symbols.py
```

### `scripts/vocab_sync.py`

Bidirectional sync between `vocabulary.json` (app-facing) and the canonical CSV (team-facing). The CSV is the artifact Joannalyn and Gabby review; `vocabulary.json` is what the app loads.

```bash
python3 scripts/vocab_sync.py export              # vocabulary.json → CSV
python3 scripts/vocab_sync.py diff                 # show what changed between CSV and JSON
python3 scripts/vocab_sync.py import               # dry-run: preview CSV → JSON changes
python3 scripts/vocab_sync.py import --apply        # write CSV changes back to vocabulary.json
```

**Synced fields:** `display_label`, `part_of_speech`, `phrase_pos`, `ui_tab`. After an `export` + `diff`, there should be zero differences. If the team edits the CSV, `import --apply` writes those changes back.

The canonical CSV lives at `data/canonical_vocabulary.csv`.

### `scripts/build_union_table.py`

Joins `vocabulary.json` and `meaning_room.json` into a single CSV for cross-system collision review.

```bash
python3 scripts/build_union_table.py
```

Outputs `data/vocabulary_union_table.csv` with columns: `symbol_id`, `display_label`, `priority_tier`, `type`, `category_xls`, `ui_tab`, `meaning_room_anchors`, `current_pos`, `phrase_pos`, `collision_flags`.

**Collision flags detected:**
- `tab-anchor-mismatch` — symbol's `ui_tab` doesn't align with its Meaning Room anchor's expected tabs
- `pos-type-mismatch` — symbol has `type: phrase` but POS is not `phrase`
- `orphan-tier-1-2` — tier 1 or 2 symbol not in any Meaning Room anchor

### `scripts/sanity_check_union.py`

Validates `data/vocabulary_union_table.csv` against the rules in `data/category_config.csv`. Writes every flagged row (raw, including known intentional overrides) to `data/union_table_issues.csv`.

```bash
python3 scripts/sanity_check_union.py
```

### `scripts/generate_vocab_review.py`

Curated, decision-oriented subset of the sanity check output. Filters known/intentional overrides and pre-fills `proposed_*` columns where the right correction can be inferred from category defaults.

```bash
python3 scripts/generate_vocab_review.py
```

Outputs `data/vocab_review.csv`. Edit the `action` column (`apply` / `modify` / `skip`) and any `proposed_*` overrides, then run `apply_vocab_review.py`.

### `scripts/apply_vocab_review.py`

Reads `data/vocab_review.csv` and applies rows marked `apply` or `modify` to `canonical_vocabulary.csv` and `meaning_room.json`.

```bash
python3 scripts/apply_vocab_review.py             # dry-run
python3 scripts/apply_vocab_review.py --apply      # write changes
```

### `scripts/backprop_union_table.py`

Alternate writeback path: if you edit `data/vocabulary_union_table.csv` directly in Excel, this script propagates those edits back to `canonical_vocabulary.csv` and `meaning_room.json`.

```bash
python3 scripts/backprop_union_table.py            # dry-run
python3 scripts/backprop_union_table.py --apply     # write changes
```

See `docs/vocabulary-update-guide.md` for the full validation-sweep workflow combining all of the above.

---

## Data quality notes

The source AMIGA AAC spreadsheet grouped vocabulary alphabetically within broad categories, leading to miscategorizations. We audited all 431 symbols across three independent category systems and documented corrections in `data/canonical_vocabulary.csv` (live) and `data/vocabulary_union_table.csv` (review artifact). The original migration trail lives in `data/_archive/` with `.RETIRED.csv` suffixes.

**Changes applied:**
1. **UI tab assignments** (139 symbols) — runtime display decisions mapping spreadsheet categories to our 6-tab UI; original spreadsheet categories preserved in `category_xls`
2. **POS corrections** (121 symbols) — the Tier 3 bulk import had assigned `pronoun/person` to everything from "People/Pronouns/Possessives" and `word` to everything from "Uncategorized"/"Social"; these are now linguistically accurate
3. **Phrase normalization** (30 symbols) — all `type: phrase` symbols now have `part_of_speech: "phrase"` with head-word POS in `phrase_pos`
4. **Compound noun fixes** (4 symbols) — play_doh, toygame, tummystomach, waterjuice reclassified from phrase to word/noun
5. **Curly quote normalization** (19 occurrences) — Unicode curly quotes normalized to straight apostrophes

**Dual source of truth:** The canonical CSV (`data/canonical_vocabulary.csv`) is the team-facing review artifact. `vocabulary.json` is the app-facing artifact. Use `scripts/vocab_sync.py` to keep them in sync.

---

## LAMP compatibility

Symbol positions are stable by default — suggested symbols are highlighted in place (golden ring) without reordering. The optional "Reorder by stress" toggle is available for demonstration purposes only.
