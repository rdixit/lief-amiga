# LiefAAC

A browser-based AAC (Augmentative and Alternative Communication) prototype for the AMIGA project. Designed for non-speaking individuals, with a focus on LAMP (Language Acquisition through Motor Planning) compatibility — consistent symbol positions, stress-aware highlighting, and Fitzgerald Key color coding.

---

## Running the app

ES modules require a local HTTP server (direct `file://` open won't work):

```bash
python3 -m http.server
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Key files

| File | Purpose |
|---|---|
| `vocabulary.json` | Source of truth — all symbols, tabs, tiers, POS, config |
| `symbols.js` | ES module mapping `symbol_id` → SVG string |
| `scripts/generate_symbols.py` | Regenerate `symbols.js` from `vocabulary.json` |
| `scripts/build_vocabulary_corrections_export.py` | Diff `vocabulary.json` vs canonical CSV, output correction report |
| `data/vocabulary_category_corrections.csv` | Machine-readable log of all tab + POS corrections |

---

## UI overview

- **Quick phrase bar** — horizontally scrollable pill buttons; left/right arrows hide at scroll boundaries; stress-relevant phrases highlighted with an orange ring when stress ≥ 3
- **Tab bar** — 6 tabs: Core · Actions · Feelings · People · Things · More — each with a distinct accent color
- **Symbol grid** — filters by active tab; cards fixed at 100px height with 2-line label clamp

### Controls

| Control | Default | Effect |
|---|---|---|
| Sort by frequency | On | Within each tier, sorts by number of source word lists, then alphabetically |
| Reorder by stress | Off | Shifts stress-highlighted symbols to the front of the grid |
| Symbol color key | — | Opens Fitzgerald Key color legend popup |
| Break | — | Launches 60-second breathing exercise |

---

## Vocabulary

`vocabulary.json` contains 424 symbols drawn from the AMIGA AAC Expansion Packet (v4.5.2026). Each symbol has:

| Field | Description |
|---|---|
| `id` | Snake_case identifier, matches key in `symbols.js` |
| `display_label` | Human-readable label shown on the card |
| `ui_tab` | Runtime tab assignment: `core`, `actions`, `feelings`, `people`, `things`, `more` |
| `priority_tier` | `1` (always shown) · `2` (shown) · `3` (hidden by default) |
| `part_of_speech` | Fitzgerald Key role: `verb/action`, `noun`, `descriptor/adjective`, `pronoun/person`, `location/preposition`, `negation/repair`, `phrase` |
| `sources` | Source word lists the symbol appears in (used for frequency sort) |
| `allowed_for_grid` | `true` for Tier 1 and 2; `false` for Tier 3 |

**173 symbols** are currently live in the grid (Tier 1: 58, Tier 2: 115).

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

---

## Scripts

### `scripts/generate_symbols.py`

Regenerates `symbols.js` from `vocabulary.json`. Backs up existing `vocabulary.json` and `symbols.js` to `data/` with a datestamp before overwriting.

```bash
python3 scripts/generate_symbols.py
```

### `scripts/build_vocabulary_corrections_export.py`

Diffs `vocabulary.json` against the original canonical spreadsheet CSV and writes:
- `data/vocabulary_category_corrections.csv` — every tab and POS change, with reason
- `data/AMIGA-AAC-4.5.2026-canonical_vocabulary_corrected.csv` — proposed corrected CSV for team review

```bash
python3 scripts/build_vocabulary_corrections_export.py
```

---

## Data quality notes

The source AMIGA AAC spreadsheet grouped vocabulary alphabetically within broad categories, leading to miscategorizations. We audited all 424 symbols and documented corrections in `data/vocabulary_category_corrections.csv`.

**Two types of changes:**
1. **UI tab assignments** (124 symbols) — runtime display decisions mapping spreadsheet categories to our 6-tab UI; original spreadsheet categories are preserved in the corrected CSV for future tab expansion
2. **Genuine source corrections** (29 category + 37 POS fixes) — objectively wrong assignments in the spreadsheet (e.g., `dog` in "Actions", `airplane` in "People/Pronouns")

The corrected CSV (`AMIGA-AAC-4.5.2026-canonical_vocabulary_corrected.csv`) is **pending team review** before being merged back to the source spreadsheet.

---

## LAMP compatibility

Symbol positions are stable by default — suggested symbols are highlighted in place (golden ring) without reordering. The optional "Reorder by stress" toggle is available for demonstration purposes only.
