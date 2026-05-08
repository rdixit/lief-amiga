# PR: `mjp/vocab_add` → `master`

**LiefAAC Phase I: Modular vocabulary, tab navigation, and LAMP-consistent grid**

---

## Summary

This PR refactors the LiefAAC prototype from a hardcoded single-file app into a modular, vocabulary-driven system with tab navigation, stress-aware highlighting, and a corrected symbol set. It also delivers a fully audited and corrected canonical vocabulary CSV ready to sync back to the source spreadsheet.

---

## What changed

### Architecture
- Migrated `app.js` to an ES module (`type="module"`) with `import { SYMBOL_SVGS } from './symbols.js'`
- Removed all hardcoded `SYMBOLS`, `NEXT_WORD_MAP`, `SENTENCE_TEMPLATES`, `AFFECT_SUGGESTIONS` constants
- Vocabulary and configuration now loaded async from `vocabulary.json` at startup
- Added graceful error display if HTTP server is not running (ES module CORS requirement)

### Vocabulary (`vocabulary.json` + `symbols.js`)
- Added 424-symbol vocabulary from the AMIGA AAC Expansion Packet
- Added 5 orphan symbols restored from v1: `feel`, `school`, `food`, `thank_you`, `he_she`
- Promoted `he` and `she` to Tier 1
- Restored **33 original hand-crafted v1 SVGs** for Tier 1 symbols (pronouns, core verbs, feelings, etc.)
- Fixed `made` SVG (was showing an angry face due to substring match against `mad` in the generator)
- Redesigned `make`/`made` as a clear stacked building-blocks icon

### Vocabulary data audit & corrections
A systematic cross-reference of `vocabulary.json` against the canonical expansion-packet CSV revealed widespread miscategorization in the source spreadsheet (words were grouped alphabetically within broad categories, not by semantic role). All corrections are documented in `data/vocabulary_category_corrections.csv` and applied back to the canonical CSV.

**Tab/category corrections — 124 symbols moved to correct tab:**
- `dog`, `doll`, `playground` were in Actions → moved to Things (nouns, not verbs)
- `airplane`, `bus`, `tummy` were in People → moved to Things (vehicles/body parts)
- `doctor`, `man`, `baby` were in People → moved to People (confirmed) or Things
- `chips`, `cookie`, `shirt`, `books` were in Social/Core → moved to Things (nouns)
- `bathroom`, `school`, `home`, `gym`, `train`, `trampoline`, `classroom` were in Places → moved to Things (nouns)
- `dog`, `doll`, `down`, `ready`, `great`, `house`, `door`, `doctor`, `together` were in Actions → moved to correct tabs
- `tired`, `fine`, `great`, `mean` moved to Feelings (adjectives, not misc)
- `help`, `want`, `no`, `stop`, `more` moved to Core (high-frequency essential words)
- `know` moved from Negation/Repair → Actions (it's a verb)

**POS corrections — 37 symbols corrected:**
- `good`, `bad`, `great`, `fine`, `tired`, `nervous`, `sick`, `frustrated` → `descriptor/adjective`
- `dog`, `doll`, `airplane`, `bus`, `tummy`, `playground`, `bathroom`, `home`, `gym`, `train`, `trampoline`, `classroom`, `mouth` → `noun`
- `stop` → `negation/repair`
- `made`, `need`, `know` → `verb/action`
- `mine` → `pronoun/person`
- `down`, `pink` → `location/preposition` / `descriptor/adjective`
- `more`, `yes`, `goodbye`, `books`, `bad`, `white` → corrected from `verb/action` or `word`

**Canonical CSV updated** (`data/AMIGA_AAC_Vocabulary_Expansion_Packet_4.5.2026_canonical_vocabulary.csv`):
- 1004 rows (999 original + 5 additions: feel, food, school, thank you, he/she)
- 124 `category` fields corrected
- 37 `part_of_speech` fields corrected
- Ready to merge back to source spreadsheet

### Fitzgerald Key background tints
- Symbol cards now show a subtle background tint by grammar role (Fitzgerald Key standard)
- 🟡 Yellow = pronouns, 🟢 Green = verbs, 🔵 Blue = nouns, 🟠 Orange = prepositions, 🟣 Purple = descriptors, 🔴 Red = negation, 🩷 Pink = phrases
- Tab left-border accent color preserved for navigation context
- `?` button in controls panel opens a color key popup (Escape or click-outside to dismiss)
- Hover uses `filter: brightness` to preserve tint color

### UI: Three-bar layout
- **Quick phrase bar** — horizontally scrollable, with left/right arrows that hide at scroll boundaries
- **Tab bar** — 6 tabs (Core, Actions, Feelings, People, Things, More) styled as distinct raised buttons with per-tab accent colors
- **Symbol grid** — filters by active tab; cards fixed at 100px height with 2-line label clamp for consistent layout

### Symbol highlighting & sorting (LAMP-compatible)
- Suggested symbols always highlighted in place (golden ring + dot) — positions never change by default
- "Reorder by stress" toggle (default off) — optionally shifts stress-relevant symbols to front of grid
- "Sort by frequency" toggle (default on) — sorts within tier by number of source word lists, then alphabetically
- Tier ordering always applied first (Tier 1 → 2 → 3)

### Other
- Breathing exercise reduced from 120s to 60s
- `scripts/generate_symbols.py` added — generates `symbols.js` from vocabulary with datestamped backups
- `scripts/build_vocabulary_corrections_export.py` added — regenerates corrections CSV from vocabulary.json + canonical CSV diff
- `data/` directory added with original vocabulary source archive, v1 symbols backup, corrections CSV, and corrected canonical CSV
- `.gitignore` updated to track `.claude/` but ignore `.claude/worktrees/`
- New docs: `VOCAB_TIER_1_UPDATE.md`, `vocabulary-tiers.md`, `API_KEY_SECURITY.md`, `SPATIAL_UI_CONCEPT.md`

---

## Files changed

| File | Change |
|---|---|
| `app.js` | Full refactor (~845 lines) |
| `index.html` | New three-bar layout, module script tag, controls, color key button |
| `style.css` | Tab bar, quick phrase bar, card grid, Fitzgerald Key tints, modal |
| `vocabulary.json` | 424-symbol vocabulary, 124 tab + 37 POS corrections applied |
| `symbols.js` | 424 SVGs — 33 v1 restored, make/made redesigned |
| `scripts/generate_symbols.py` | New: generates symbols.js from vocabulary |
| `scripts/build_vocabulary_corrections_export.py` | New: diffs vocabulary.json vs canonical CSV, outputs corrections |
| `data/AMIGA_AAC_Vocabulary_Expansion_Packet_4.5.2026_canonical_vocabulary.csv` | Corrected canonical CSV (1004 rows) |
| `data/vocabulary_category_corrections.csv` | 144-row machine-readable correction changelist |
| `data/symbols_v1_backup.json` | Original v1 symbol SVG archive |
| `docs/` | 4 new docs, 1 archived |

---

## Test scenarios

1. Core tab loads on startup with Tier 1 symbols visible
2. Tapping a tab filters grid correctly — no cross-tab bleed
3. Quick phrase bar scrolls; arrows hide at boundaries
4. Stress zone slider highlights relevant cards without moving them
5. "Reorder by stress" moves suggested cards to front when checked
6. "Sort by frequency" orders within tier by source count, then alphabetically
7. Sentence bar builds, predicts, and speaks
8. Break button → breathing exercise runs 60s then auto-closes
9. `dog`, `doll`, `airplane` appear under **Things** (not Actions/People)
10. `happy`, `sad`, `frustrated` appear under **Feelings**
11. `him`, `his`, `she`, `he` appear under **People**
12. Symbol color key popup opens, dismisses with Escape or outside click
13. Fitzgerald Key tints visible on cards; gold highlight wins on suggested symbols
