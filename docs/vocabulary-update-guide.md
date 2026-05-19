# Vocabulary Update Guide

How to add, correct, or reclassify vocabulary in the AMIGA-AAC system.

## Architecture: Three Canonical Stores

```
data/vocabulary_union_table.csv   ← validation/review artifact (editable)
        │
        ▼  backprop_union_table.py --apply
data/canonical_vocabulary.csv     ← team-facing source of truth (flat CSV)
meaning_room.json                 ← anchor membership (spatial layout)
        │
        ▼  vocab_sync.py import --apply
vocabulary.json                   ← app-facing runtime data
```

**`data/canonical_vocabulary.csv`** is the authoritative flat file. All category, POS, tab, and metadata changes land here first, then sync to `vocabulary.json`.

**`vocabulary.json`** is what the app loads. Never edit it directly for category/tab/POS changes -- use the sync pipeline.

**`meaning_room.json`** defines anchor hotspots and which symbols appear in each anchor. Updated by the backprop script when you change `meaning_room_anchors` in the union table.

**`data/category_config.csv`** defines the 16 categories and their default tab, anchor, and subtab mappings. All scripts read from this instead of hardcoding.

## Workflow: Full Validation Sweep

Use this when doing a bulk review of categories, tabs, POS, or anchors.

### 1. Generate the union table

```bash
python3 scripts/build_union_table.py
```

This produces `data/vocabulary_union_table.csv` by joining `vocabulary.json` + `meaning_room.json`. It flags tab-anchor mismatches, POS-type mismatches, and T1-T2 orphans.

### 2. Edit in Excel

Open `data/vocabulary_union_table.xlsx` (or the CSV) and review/correct:

| Column | What to edit | Notes |
|--------|-------------|-------|
| `category_xls` | Semantic category | Must match a row in `data/category_config.csv` |
| `ui_tab` | Primary tab | Use `tab1;tab2` for multi-tab (first = primary, rest = secondary) |
| `current_pos` | Part of speech | `verb/action`, `noun`, `pronoun/person`, `descriptor/adjective`, `negation/repair`, `question word`, `location/preposition`, `word`, `phrase` |
| `phrase_pos` | Semantic POS for phrases | Only for `type=phrase`; the grammatical POS of the phrase's intent |
| `meaning_room_anchors` | Anchor membership | Semicolon-separated anchor IDs; leave blank for T3 without anchors |

Export the xlsx back to CSV when done.

### 3. Sanity check

```bash
python3 scripts/sanity_check_union.py
```

Generates `data/union_table_issues.csv` with all questionable rows. Fix issues in the xlsx and re-export until clean.

### 4. Backprop to canonical stores

```bash
# Dry run -- see all changes before writing
python3 scripts/backprop_union_table.py

# Apply -- writes to canonical_vocabulary.csv + meaning_room.json
python3 scripts/backprop_union_table.py --apply
```

This propagates:
- `category_xls` → `category` column in canonical CSV
- `ui_tab` with `;` → `ui_tab` (primary) + `secondary_tabs` (rest)
- `current_pos` → `part_of_speech`
- `phrase_pos` → `phrase_pos`
- `meaning_room_anchors` → symbol_ids arrays in `meaning_room.json`

### 5. Sync to vocabulary.json

```bash
python3 scripts/vocab_sync.py import --apply
```

Pushes canonical CSV fields into `vocabulary.json`. Synced fields: `display_label`, `part_of_speech`, `phrase_pos`, `ui_tab`, `category` (→ `category_xls`), `secondary_tabs` (→ `additional_tabs`).

### 6. Verify

```bash
python3 scripts/vocab_sync.py diff    # should report zero diffs
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
| `scripts/build_union_table.py` | Generate union table for review | `data/vocabulary_union_table.csv` |
| `scripts/sanity_check_union.py` | Validate edited union table | `data/union_table_issues.csv` |
| `scripts/backprop_union_table.py` | Push union table edits to canonical stores | `data/canonical_vocabulary.csv`, `meaning_room.json` |
| `scripts/vocab_sync.py export` | vocabulary.json → canonical CSV | `data/canonical_vocabulary.csv` |
| `scripts/vocab_sync.py import` | canonical CSV → vocabulary.json | `vocabulary.json` |
| `scripts/vocab_sync.py diff` | Show differences between CSV and JSON | (read-only) |
| `scripts/audit_categories.py` | Cross-validate category × tab × POS | `data/category_audit.csv` |
| `scripts/category_utils.py` | Shared config loader (imported by other scripts) | (library) |
| `scripts/generate_symbols.py` | Generate SVG icons for all symbols | `symbols.js` |
