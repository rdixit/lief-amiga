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
| `data/meaning_room.json` | Meaning Room scene config — image, anchor hotspots, symbol mappings, glow curves |
| `symbols.js` | ES module mapping `symbol_id` → SVG string |
| `app.js` | Application logic — view state machine, glow engine, sentence builder |
| `style.css` | All styles including iPad frame, hotspot glow, and pulse animation |
| `scripts/generate_symbols.py` | Regenerate `symbols.js` from `vocabulary.json` |
| `scripts/build_vocabulary_corrections_export.py` | Diff `vocabulary.json` vs canonical CSV, output correction report |

---

## UI overview

The app has three views, controlled by a toggle button (bottom-left) and persisted in `localStorage`:

### Meaning Room (default)
A spatial scene showing a child's room. Each object is a tappable anchor leading to a focused symbol grid for that category. Anchors glow softly at all times; stress-sensitive anchors (Feelings, Stop, Calm) escalate and pulse at high stress zones.

- **Stress glow** — driven by the Lief HRV device (or the simulated slider); only anchors with a `stress_glow_curve` in `data/meaning_room.json` escalate at high stress
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

`data/meaning_room.json` controls the entire Meaning Room layout. Edit this file to adjust anchor positions, symbol mappings, or glow curves without touching code.

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
| `part_of_speech` | Fitzgerald Key role: `verb/action`, `noun`, `descriptor/adjective`, `pronoun/person`, `location/preposition`, `negation/repair`, `phrase` |
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

---

## Tests

```bash
npm test
```

Uses Node's built-in test runner (`node:test`) — no install required. Runs `tests/data/vocab_coverage.test.js` (71 tests, ~100ms).

**What is tested:**

| Suite | Checks |
|---|---|
| `meaning_room.json schema` | Required anchor fields, hotspot bounds (x+w ≤ 1, y+h ≤ 1), glow curve length and range |
| `symbol resolution` | Every `symbol_id` exists in `vocabulary.json`, has `allowed_for_grid: true`, no duplicates within an anchor |
| `tier coverage` | Every tier-1 and tier-2 grid symbol appears in at least one anchor |
| `stress glow integrity` | Glow values in `[0,1]`, curves are monotonically non-decreasing |

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
