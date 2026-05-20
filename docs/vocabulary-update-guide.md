# Vocabulary Update Guide

How to add, correct, or reclassify vocabulary in the AMIGA-AAC system.

## Architecture: Three Canonical Stores

```
data/canonical_vocabulary.csv     ← team-facing source of truth (flat CSV)
meaning_room.json                 ← anchor membership (spatial layout)
        │
        │  vocab_sync.py import --apply
        ▼
vocabulary.json                   ← app-facing runtime data
        │
        │  build_union_table.py
        ▼
data/vocabulary_union_table.csv   ← joined review/validation artifact
        │
        ├──→ sanity_check_union.py   → data/union_table_issues.csv  (raw flags)
        ├──→ generate_vocab_review.py → data/vocab_review.csv       (curated decisions)
        ├──→ apply_vocab_review.py    → writes back to canonical + meaning_room
        └──→ backprop_union_table.py  → alternate writeback path
```

**`data/canonical_vocabulary.csv`** is the authoritative flat file. All category, POS, tab, and metadata changes land here first, then sync to `vocabulary.json`.

**`vocabulary.json`** is what the app loads. Never edit it directly for category/tab/POS changes -- use the sync pipeline.

**`meaning_room.json`** defines anchor hotspots and which symbols appear in each anchor. Updated by either `apply_vocab_review.py` or `backprop_union_table.py` when anchor membership changes.

**`data/category_config.csv`** defines the 16 categories and their default tab, anchor, and subtab mappings. All scripts read from this instead of hardcoding.

## Workflow: Full Validation Sweep (recommended)

Use this when doing a bulk audit of categories, tabs, POS, or anchors. Output is a single CSV (`vocab_review.csv`) of *only* the items that need a decision, with proposed corrections pre-filled.

### 1. Build the union table and run the sanity check

```bash
python3 scripts/build_union_table.py        # vocabulary.json + meaning_room.json → vocabulary_union_table.csv
python3 scripts/sanity_check_union.py       # → data/union_table_issues.csv (all flagged rows)
```

`union_table_issues.csv` is the raw list of every symbol that fails any rule, including known/intentional overrides.

### 2. Generate the curated review file

```bash
python3 scripts/generate_vocab_review.py    # → data/vocab_review.csv
```

`vocab_review.csv` is a filtered, decision-oriented subset. It drops symbols on the `INTENTIONAL_OVERRIDES` / `AMBIGUOUS` lists inside `generate_vocab_review.py` and pre-fills `proposed_*` columns where the right correction can be inferred from category defaults.

### 3. Mark and edit the review CSV

Open `data/vocab_review.csv` (Excel or any CSV editor). For each row, set the `action` column:

- `apply` — proposed values are correct as-is
- `modify` — override at least one `proposed_*` value, then apply
- `skip` — current placement is intentional; no change

Columns you can override per row:
- `proposed_category`, `proposed_ui_tab`, `proposed_secondary_tabs`, `proposed_pos`, `proposed_anchors`

Leave a `proposed_*` cell blank to keep the current canonical value.

If a row is a recurring intentional override, add its `symbol_id` to `INTENTIONAL_OVERRIDES` in `scripts/generate_vocab_review.py` so it stops surfacing in future review passes.

### 4. Apply the review

```bash
python3 scripts/apply_vocab_review.py            # dry run — show exactly what will change
python3 scripts/apply_vocab_review.py --apply    # write changes
```

Writes to:
- `data/canonical_vocabulary.csv` (category, ui_tab, secondary_tabs, part_of_speech)
- `meaning_room.json` (anchor membership; anchors must already exist)

### 5. Sync canonical to vocabulary.json

```bash
python3 scripts/vocab_sync.py import --apply
```

Pushes canonical CSV fields into `vocabulary.json`. Synced fields: `display_label`, `part_of_speech`, `phrase_pos`, `ui_tab`, `category` (→ `category_xls`), `secondary_tabs` (→ `additional_tabs`).

### 6. Verify the round trip is clean

```bash
python3 scripts/build_union_table.py        # rebuild union table from updated JSON
python3 scripts/sanity_check_union.py       # confirm only known/accepted issues remain
python3 scripts/backprop_union_table.py     # dry run — should report "Nothing to do"
python3 scripts/vocab_sync.py diff          # should report zero diffs
```

If `backprop_union_table.py` and `vocab_sync.py diff` both report empty, `canonical_vocabulary.csv ↔ vocabulary.json ↔ vocabulary_union_table.csv ↔ meaning_room.json` are all in sync.

## Workflow: Edit the Union Table Directly (alternate path)

If you'd rather edit `data/vocabulary_union_table.csv` in Excel directly (older flow), the legacy backprop pipeline still works:

| Column | What to edit | Notes |
|--------|-------------|-------|
| `category_xls` | Semantic category | Must match a row in `data/category_config.csv` |
| `ui_tab` | Primary tab | Use `tab1;tab2` for multi-tab (first = primary, rest = secondary) |
| `current_pos` | Part of speech | `verb/action`, `noun`, `pronoun/person`, `descriptor/adjective`, `negation/repair`, `question word`, `location/preposition`, `word`, `phrase` |
| `phrase_pos` | Semantic POS for phrases | Only for `type=phrase`; the grammatical POS of the phrase's intent |
| `meaning_room_anchors` | Anchor membership | Semicolon-separated anchor IDs; leave blank for T3 without anchors |

Then:

```bash
python3 scripts/backprop_union_table.py             # dry run
python3 scripts/backprop_union_table.py --apply     # writes canonical_vocabulary.csv + meaning_room.json
python3 scripts/vocab_sync.py import --apply        # syncs canonical to vocabulary.json
```

## Workflow: Quick Single-Word Fix

For a small number of corrections, skip the union table:

1. Edit `data/canonical_vocabulary.csv` directly (change category, POS, tab, etc.)
2. Run `python3 scripts/vocab_sync.py import --apply`
3. Verify with `python3 scripts/vocab_sync.py diff`

For anchor changes, edit `meaning_room.json` directly (add/remove symbol_ids from the relevant anchor).

## Workflow: Adding New Words

1. Add the word to `vocabulary.json` with all required fields (id, canonical_term, display_label, type, category_xls, ui_tab, part_of_speech, priority_tier, etc.)
2. Run `python3 scripts/vocab_sync.py export` to regenerate the canonical CSV
3. Add anchor membership in `meaning_room.json` if the word should appear in the meaning room
4. Run `python3 scripts/generate_symbols.py` to generate/regenerate SVG icons

## Key Concepts

### Category vs Tab vs Anchor

- **Category** (`category_xls`): semantic classification -- *what kind of word is this?* (16 categories in `category_config.csv`)
- **Tab** (`ui_tab`): where the child finds it in the grid -- *which tab does it appear under?* Defaults from category via config, but can be overridden per-symbol (e.g., `help` is category=Actions but tab=core for accessibility)
- **Anchor** (`meaning_room_anchors`): spatial location in the meaning room scene. Derived from category's default anchor, but can include multiple anchors (verb duplication pattern)

### Secondary Tabs

A word can appear in multiple tabs. The `ui_tab` field is the primary tab; `secondary_tabs` lists additional tabs (semicolon-separated in CSV, JSON array in vocabulary.json).

Example: `slide` has `ui_tab=things`, `secondary_tabs=actions` -- it shows in both the things grid and the actions grid.

### Multi-value Fields in the Union Table

- `ui_tab`: `things;actions` → primary=things, secondary=actions
- `meaning_room_anchors`: `actions;toys` → symbol appears in both anchors
- `category_xls`: single value only (no semicolons)

### Homographs

Words with the same spelling but different meanings need distinct symbol_ids. Example: `well` (descriptor) vs `we_ll` (contraction of "we will"). The `display_label` shows the human-readable form; the `id`/`symbol_id` must be unique.

## Scripts Reference

| Script | Purpose | Modifies |
|--------|---------|----------|
| `scripts/build_union_table.py` | Generate union table by joining `vocabulary.json` + `meaning_room.json` | `data/vocabulary_union_table.csv` |
| `scripts/sanity_check_union.py` | Validate union table; flag every rule violation | `data/union_table_issues.csv` |
| `scripts/generate_vocab_review.py` | Curated, decision-oriented subset of sanity findings (filters known overrides) | `data/vocab_review.csv` |
| `scripts/apply_vocab_review.py` | Apply marked `apply`/`modify` rows from `vocab_review.csv` to canonical stores | `data/canonical_vocabulary.csv`, `meaning_room.json` |
| `scripts/backprop_union_table.py` | Alternate writeback: push union table edits directly to canonical stores | `data/canonical_vocabulary.csv`, `meaning_room.json` |
| `scripts/vocab_sync.py export` | vocabulary.json → canonical CSV | `data/canonical_vocabulary.csv` |
| `scripts/vocab_sync.py import` | canonical CSV → vocabulary.json | `vocabulary.json` |
| `scripts/vocab_sync.py diff` | Show differences between CSV and JSON | (read-only) |
| `scripts/category_utils.py` | Shared config loader (imported by other scripts) | (library) |
| `scripts/generate_symbols.py` | Generate SVG icons for all symbols | `symbols.js` |

### Archived (no longer in active use)

These scripts were one-shot migrations/bootstraps used to bring the system to its current shape; they live in `scripts/_archive/` for reference. The data they produced (e.g. `data/_archive/pos_corrections.RETIRED.csv`, `data/_archive/category_audit.RETIRED.csv`) is also retired.

- `scripts/_archive/apply_pos_corrections.py` — applied historical POS fixes from `pos_corrections.csv`
- `scripts/_archive/audit_categories.py` — older cross-validator; superseded by `sanity_check_union.py` + `generate_vocab_review.py`
- `scripts/_archive/build_vocabulary_corrections_export.py` — diffed `vocabulary.json` against a legacy spreadsheet
- `scripts/_archive/update_expansion_packet.py` — original bootstrap of `canonical_vocabulary.csv` from the expansion packet
