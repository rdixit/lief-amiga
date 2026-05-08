# LiefAAC — Coding Agent Next Steps

**Project:** AMIGA-AAC / LiefAAC prototype  
**Status:** Vocabulary + symbol layer complete. App refactor ready to begin.  
**Working files:** `index.html`, `app.js`, `style.css` (two-file app currently)  
**New assets:** `vocabulary.json`, `symbols.js`, `generate_symbols.py`

---

## Context

The current app (`app.js` + `index.html`) has 40 hardcoded symbols, a flat single-page grid, and all constants (SYMBOLS, NEXT_WORD_MAP, SENTENCE_TEMPLATES, AFFECT_SUGGESTIONS) embedded directly in `app.js`. 

The vocabulary and symbol layers have been rebuilt from source:

- **`vocabulary.json`** — 419 symbols across 3 tiers, with metadata: `ui_tab`, `intent_tags`, `is_quick_phrase`, `is_phrase`, `allowed_for_grid`, `priority_tier`, `scenario_tags`, `phrase_templates`, `requires_personalization`, `synonyms_or_variants`. Also contains `tabs`, `quick_phrases`, `next_word_map`, `sentence_templates`, `affect_suggestions`, `phrase_templates`, and `validation_scenarios`.
- **`symbols.js`** — ES module exporting `SYMBOL_SVGS`, a key-value map of `symbol_id → SVG string`. All 166 grid symbols (Tier 1 + Tier 2) have hand-crafted pictographic SVGs. Tier 3 symbols have text-label fallbacks.

The goal is to refactor the app into a clean, modular structure while adding the tab navigation UI and quick phrase bar.

---

## File Structure After Refactor

```
liefaac/
├── index.html          # Updated layout — 3 bar structure
├── style.css           # Updated styles for tabs + quick phrase bar
├── app.js              # Logic only — no hardcoded vocab or SVGs
├── vocabulary.json     # Source of truth for all vocab + constants
├── symbols.js          # All SVG pictograms, ES module
└── generate_symbols.py # Regenerate symbols.js when vocab changes
```

---

## Step 1 — Refactor `app.js`: Remove Hardcoded Constants

Replace the inline `SYMBOLS`, `NEXT_WORD_MAP`, `SENTENCE_TEMPLATES`, and `AFFECT_SUGGESTIONS` constants with dynamic loading from `vocabulary.json`.

### 1a. Load vocabulary at startup

```javascript
import { SYMBOL_SVGS } from './symbols.js';

let VOCAB = null;
let SYMBOLS = [];
let QUICK_PHRASES = [];
let TABS = [];
let NEXT_WORD_MAP = {};
let SENTENCE_TEMPLATES = {};
let AFFECT_SUGGESTIONS = {};

async function loadVocabulary() {
  const res = await fetch('./vocabulary.json');
  VOCAB = await res.json();
  SYMBOLS = VOCAB.symbols.filter(s => s.allowed_for_grid);
  QUICK_PHRASES = VOCAB.quick_phrases;
  TABS = VOCAB.tabs;
  NEXT_WORD_MAP = VOCAB.next_word_map;
  SENTENCE_TEMPLATES = VOCAB.sentence_templates;
  AFFECT_SUGGESTIONS = VOCAB.affect_suggestions;
}
```

Call `await loadVocabulary()` before rendering anything.

### 1b. Update symbol rendering

Replace the old SVG lookup with `SYMBOL_SVGS`:

```javascript
function getSymbolSVG(sym) {
  return SYMBOL_SVGS[sym.id] 
    || (sym.svg_key && SYMBOL_SVGS[sym.svg_key]) 
    || SYMBOL_SVGS['fallback'] 
    || '';
}
```

### 1c. Update `buildNextWordSuggestions()`

The function signature stays the same. The `NEXT_WORD_MAP` is now loaded from JSON. No logic changes needed — just ensure it references the module-level variable.

### 1d. Update `buildSentence()`

Same pattern — `SENTENCE_TEMPLATES` is now loaded from JSON. The lookup logic is identical.

### 1e. Update affect suggestions

`AFFECT_SUGGESTIONS` from `vocabulary.json` has the same structure as the current hardcoded version. Swap the reference.

---

## Step 2 — Update `index.html`: Three-Bar Layout

The iPad screen currently has: sentence bar → selected strip → symbol grid.

Replace it with: **quick phrase bar → tab bar → symbol grid**.

### New structure inside `.ipad-screen`:

```html
<!-- Bar 1: Quick Phrases (single-tap complete utterances) -->
<div class="quick-phrase-bar" id="quickPhraseBar">
  <!-- Populated dynamically from QUICK_PHRASES in vocabulary.json -->
</div>

<!-- Bar 2: Category Tabs -->
<div class="tab-bar" id="tabBar">
  <!-- Populated dynamically from TABS in vocabulary.json -->
</div>

<!-- Sentence bar (moved below tabs, still visible) -->
<div class="sentence-bar">
  <div class="sentence-display" id="sentenceDisplay">
    <span class="placeholder">Tap symbols below...</span>
  </div>
  <div class="sentence-controls">
    <button class="btn-speak" id="btnSpeak"><!-- speak icon --></button>
    <button class="btn-clear" id="btnClear"><!-- clear icon --></button>
  </div>
</div>

<!-- Selected symbols strip -->
<div class="selected-strip" id="selectedStrip"></div>

<!-- Symbol grid (filtered by active tab) -->
<div class="symbol-grid" id="symbolGrid"></div>

<!-- Break button + modal stay as-is -->
```

### Quick phrase bar behavior:
- Horizontal scrollable row of pill-shaped buttons
- Each pill: icon emoji + label (e.g., "🆘 Help me", "🔇 Too loud")
- Tapping a quick phrase: speaks immediately (bypass prediction), adds to sentence bar display, does NOT add to selectedStrip (it's a complete utterance)
- Affect-aware highlighting: pills with `affect_priority: "stressed"` get a subtle highlight ring when stress level ≥ 3

### Tab bar behavior:
- 6 tabs: Core ⭐, Actions ⚡, Feelings 💛, People 👥, Things 📍, More ➕
- Active tab is highlighted
- Switching tabs re-renders the symbol grid filtered to that tab
- Default active tab: `core`
- Tab colors come from `TABS[i].color` in vocabulary.json

---

## Step 3 — Update `app.js`: Tab + Grid Logic

### 3a. State

```javascript
let activeTab = 'core';
```

### 3b. Render tabs

```javascript
function renderTabs() {
  const tabBar = document.getElementById('tabBar');
  tabBar.innerHTML = TABS.map(tab => `
    <button 
      class="tab-btn ${activeTab === tab.id ? 'active' : ''}" 
      data-tab="${tab.id}"
      style="--tab-color: ${tab.color}"
    >
      <span class="tab-emoji">${tab.emoji}</span>
      <span class="tab-label">${tab.label}</span>
    </button>
  `).join('');

  tabBar.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      activeTab = btn.dataset.tab;
      renderTabs();
      renderGrid();
    });
  });
}
```

### 3c. Filter symbols for grid

```javascript
function getGridSymbols() {
  let syms = SYMBOLS.filter(s => s.ui_tab === activeTab);
  
  // Sort: tier 1 first, then tier 2; within tier sort by display_label
  syms.sort((a, b) => {
    if (a.priority_tier !== b.priority_tier) return a.priority_tier - b.priority_tier;
    return a.display_label.localeCompare(b.display_label);
  });

  // If AI reordering is on, apply suggestion scores
  if (document.getElementById('reorderSymbols').checked) {
    syms = applyAISuggestions(syms);
  }

  return syms;
}
```

### 3d. Render grid

```javascript
function renderGrid() {
  const grid = document.getElementById('symbolGrid');
  const syms = getGridSymbols();

  grid.innerHTML = syms.map(sym => {
    const suggested = isSuggested(sym);
    return `
      <button 
        class="symbol-card ${suggested ? 'suggested' : ''}" 
        data-id="${sym.id}"
        data-label="${sym.display_label}"
        data-phrase="${sym.is_phrase}"
        title="${sym.display_label}"
      >
        <div class="symbol-icon">${getSymbolSVG(sym)}</div>
        <div class="symbol-label">${sym.display_label}</div>
      </button>
    `;
  }).join('');

  grid.querySelectorAll('.symbol-card').forEach(card => {
    card.addEventListener('click', () => onSymbolTap(card.dataset.id));
  });
}
```

### 3e. Render quick phrase bar

```javascript
function renderQuickPhrases() {
  const bar = document.getElementById('quickPhraseBar');
  const stressLevel = parseInt(document.getElementById('mockValenceSlider').value);
  
  bar.innerHTML = QUICK_PHRASES.map(qp => {
    const isStressRelevant = stressLevel >= 3 && qp.affect_priority === 'stressed';
    return `
      <button 
        class="quick-phrase-btn ${isStressRelevant ? 'stress-highlighted' : ''}"
        data-id="${qp.id}"
        data-utterance="${qp.utterance}"
      >
        ${qp.display_label}
      </button>
    `;
  }).join('');

  bar.querySelectorAll('.quick-phrase-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      speakText(btn.dataset.utterance);
      showSentenceInBar(btn.dataset.utterance);
    });
  });
}
```

Re-call `renderQuickPhrases()` whenever stress slider changes.

---

## Step 4 — Update `style.css`: New Components

### Quick phrase bar

```css
.quick-phrase-bar {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  overflow-x: auto;
  scrollbar-width: none;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  min-height: 52px;
  align-items: center;
  flex-shrink: 0;
}

.quick-phrase-btn {
  flex-shrink: 0;
  padding: 8px 14px;
  border-radius: 20px;
  background: rgba(255,255,255,0.12);
  border: 1.5px solid rgba(255,255,255,0.2);
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.quick-phrase-btn:active {
  transform: scale(0.95);
  background: rgba(255,255,255,0.25);
}

.quick-phrase-btn.stress-highlighted {
  border-color: #f97316;
  box-shadow: 0 0 0 2px #f97316;
  background: rgba(249,115,22,0.2);
}
```

### Tab bar

```css
.tab-bar {
  display: flex;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  flex-shrink: 0;
}

.tab-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 4px 6px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: rgba(255,255,255,0.5);
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  gap: 2px;
}

.tab-btn .tab-emoji { font-size: 16px; }

.tab-btn.active {
  color: white;
  border-bottom-color: var(--tab-color);
}

.tab-btn:active { opacity: 0.7; }
```

### Symbol card updates

The existing `.symbol-card` style mostly works. Add:

```css
.symbol-card .symbol-icon svg {
  width: 100%;
  height: 100%;
}

.symbol-card.suggested .symbol-icon {
  /* existing highlight style — keep as-is */
}
```

---

## Step 5 — Handle `is_phrase` Symbols in Grid

Phrase tiles (e.g., "My turn", "I need a break") should behave slightly differently from single-word tiles:

- **Visual distinction:** slightly wider card, italic or colored label
- **On tap:** if `is_quick_phrase` is true, speak immediately and don't add to sentence builder. If `is_phrase` but not `is_quick_phrase`, add to sentence bar as a single utterance unit (don't try to predict next word after it)

```javascript
function onSymbolTap(symId) {
  const sym = SYMBOLS.find(s => s.id === symId);
  if (!sym) return;

  if (sym.is_quick_phrase) {
    speakText(sym.display_label);
    showSentenceInBar(sym.display_label);
    return;
  }

  // Existing flow: add to selected strip, run prediction
  addToSelectedStrip(sym);
  updateSentenceBar();
  runPrediction();
}
```

---

## Step 6 — Personalization Placeholder

Symbols with `requires_personalization: true` exist in the vocabulary (preferred items: specific snacks, toys, names). For now:

- Show them in the grid with a small ✏️ badge overlay
- On tap: show a simple prompt "This symbol can be customized. What should it say?"
- Store the custom label in `localStorage` keyed by `sym.id`
- On next render, use the custom label instead of `display_label`

This is the foundation for the user-profile layer. Don't build the full profile system yet — just the local override mechanism.

---

## Step 7 — OpenAI Key: Move to Proxy

The current app has an obfuscated API key in the JS. Before any external testing:

1. Create a Cloudflare Worker (or equivalent) that accepts `POST /predict` with `{ symbols, stressLevel }` and forwards to the OpenAI API server-side
2. Update `app.js` to call your proxy URL instead of `https://api.openai.com/v1/chat/completions` directly
3. Remove the `atob` key from the client entirely

For now this can be deferred if testing is internal only. Flag it before Faison pilot.

---

## Step 8 — Validation Test Pass

The `vocabulary.json` contains 19 validation scenarios (see `validation_scenarios` key). After the refactor, manually run through each scenario:

| Scenario | Expected quick phrase / grid path |
|---|---|
| Snack request | Things → Food → tap "I want food" quick phrase |
| Drink request | Quick phrase "I want water" |
| Bathroom | Quick phrase "I need the bathroom" |
| Tired | Feelings → Tired → AI suggests "I am tired" |
| Frustration | Quick phrase "Help me" or "I'm frustrated" |
| Overstimulated | Quick phrase "Too loud" — highlighted at stress ≥ 3 |
| Greeting | Core → Hi |
| Turn-taking | Quick phrase "My turn" |
| Rejecting | Quick phrase "I don't want that" or Core → No |
| Transition resistance | Quick phrase "One more minute" |

---

## What NOT to Change

- The breathing exercise / break modal — keep exactly as-is
- The Lief affect bar and stress slider — keep as-is (just wire quick phrase highlighting to stress level)
- The auto-speak and confidence threshold controls — keep as-is
- The LLM prediction call signature — only the data it receives changes (symbol metadata now richer)
- The TTS implementation — keep as-is

---

## Order of Operations

1. `app.js` — load from `vocabulary.json`, remove hardcoded constants *(no visible UI change yet)*
2. `app.js` — implement tab state + `getGridSymbols()` filter *(grid now tab-filtered)*
3. `index.html` + `style.css` — add tab bar HTML + CSS *(tabs visible)*
4. `app.js` — `renderTabs()` wired up *(tabs interactive)*
5. `index.html` + `style.css` — add quick phrase bar HTML + CSS
6. `app.js` — `renderQuickPhrases()` wired up *(quick phrases visible and tappable)*
7. `app.js` — `onSymbolTap()` updated for `is_phrase` handling
8. `style.css` — phrase tile visual distinction
9. Manual validation scenario pass
10. localStorage personalization for `requires_personalization` symbols (optional, do last)
