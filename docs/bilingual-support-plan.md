# Bilingual AAC Support (En/Es)

> Status: planned, not yet implemented

## Overview

Add English/Spanish bilingual support with a simple En/Es toggle in the top-right corner. No i18n library is needed -- the approach is to add locale-suffixed fields to the vocabulary JSON and a small `UI_STRINGS` dictionary in `app.js`.

## Architecture

```
En/Es Toggle
    └── currentLang = 'en' | 'es'
            ├── getLocalizedLabel(sym) → Grid labels, Selected strip
            ├── t(key)                 → UI chrome (buttons, modals, placeholders)
            └── speakText(text, lang)  → TTS voice language
```

## Implementation Steps

### Step 1 -- Vocabulary JSON: add Spanish fields

Add parallel `_es` fields to the existing schema. English fields are unchanged (no rename).

**`symbols[]`:** add `display_label_es`, `phrase_templates_es`  
**`quick_phrases[]`:** add `display_label_es`, `utterance_es`  
**`tabs[]`:** add `label_es`, `description_es`  
**Top-level:** add `sentence_templates_es` (same id-chain keys as `sentence_templates`, Spanish values)

Example:

```json
{
  "id": "want",
  "display_label": "want",
  "display_label_es": "quiero",
  "phrase_templates": ["I want {0}"],
  "phrase_templates_es": ["Quiero {0}"]
}
```

Apply to both `vocabulary.json` (runtime) and `data/amiga-aac-vocabulary_20260507.json` (source snapshot).

---

### Step 2 -- Translation script: `scripts/translate_vocabulary.py`

New one-time script that:
1. Reads `vocabulary.json`
2. For each symbol, quick phrase, and tab -- calls an LLM or translation API to populate `_es` fields
3. Writes the updated JSON back

> **Manual review required after running.** AAC core vocabulary is clinically specific -- e.g., "more" as a core AAC word needs careful contextual translation, not a direct dictionary lookup. A fluent Spanish speaker should audit the output.

---

### Step 3 -- `app.js`: language state and resolver functions

Add near the top of the module:

```javascript
let currentLang = localStorage.getItem('aac_lang') || 'en';

function getLocalizedLabel(sym) {
  if (currentLang === 'es' && sym.display_label_es) return sym.display_label_es;
  return sym.display_label;
}

const UI_STRINGS = {
  en: {
    sentencePlaceholder: "Tap symbols to build a sentence...",
    speakButton: "Speak",
    clearButton: "Clear",
    breakTitle: "Let's take a break",
    breatheIn: "Breathe in...",
    greatJob: "Great job!",
    liefConnected: "Connected to Lief",
    // ... ~20-30 keys covering all hardcoded chrome
  },
  es: {
    sentencePlaceholder: "Toca los símbolos para formar una oración...",
    speakButton: "Hablar",
    clearButton: "Borrar",
    breakTitle: "Tomemos un descanso",
    breatheIn: "Inhala...",
    greatJob: "¡Muy bien!",
    liefConnected: "Conectado a Lief",
    // ...
  }
};

function t(key) {
  return UI_STRINGS[currentLang]?.[key] ?? UI_STRINGS.en[key];
}
```

---

### Step 4 -- `app.js`: update all render functions

Replace `sym.display_label` with `getLocalizedLabel(sym)` and hardcoded strings with `t(key)` in:

| Function | What changes |
|----------|-------------|
| `renderGrid()` | Symbol card labels |
| `renderSelectedStrip()` | Chip labels |
| `renderQuickPhrases()` | Button text and utterance |
| `renderTabs()` | Tab labels |
| Break/breathing modal | All modal copy |
| Sentence placeholder | Empty state text |
| `buildSentencePrompt()` | Tell OpenAI to produce Spanish output when `currentLang === 'es'` |
| Local sentence fallback | Use `sentence_templates_es` when available |

---

### Step 5 -- `app.js` / TTS: language-aware speech

```javascript
// Browser TTS
const utterance = new SpeechSynthesisUtterance(text);
utterance.lang = currentLang === 'es' ? 'es-ES' : 'en-US';

// OpenAI TTS (if used) -- no voice change needed, but prompt should be in the target language
```

---

### Step 6 -- `index.html`: toggle button + dynamic chrome

Add a language toggle to the header:

```html
<button id="langToggle" class="lang-toggle">En | Es</button>
```

Move any static English text in `index.html` that also appears in `UI_STRINGS` into JS-driven updates via a `updateUILanguage()` function called on toggle and on init.

Toggle handler in `app.js`:

```javascript
function toggleLanguage() {
  currentLang = currentLang === 'en' ? 'es' : 'en';
  localStorage.setItem('aac_lang', currentLang);
  updateUILanguage();
  renderTabs();
  renderGrid();
  renderQuickPhrases();
  renderSelectedStrip();
}
```

---

### Step 7 -- `style.css`: toggle styling

Small pill-style button in the top-right, ~10 lines of CSS. Active language highlighted.

---

### Step 8 -- Fallback SVGs in `symbols.js` (optional / deferred)

Fallback SVGs embed English text as `<text>` elements inside the icon. Two options:

- **(A) Skip for v1** -- the text label below each icon already switches to Spanish. The fallback circle icon stays English, which is acceptable for the initial release.
- **(B) Full localization** -- modify `generate_symbols.py` to emit a parallel `SYMBOL_SVGS_ES` map with Spanish text in fallbacks. `getSymbolSVG` selects the right map based on `currentLang`. Doubles `symbols.js` file size.

**Recommendation: go with option A for v1.**

---

## What Needs Human/Clinical Review Before Shipping

- **~500+ vocabulary `display_label_es` values** -- translation script provides a first pass; a fluent Spanish speaker with AAC familiarity should audit all entries
- **`sentence_templates_es`** -- grammatical patterns (not just word swaps); needs a fluent author
- **`next_word_map`** -- word-prediction chains are keyed by symbol `id` (language-neutral), so they work for v1, but Spanish word order and verb conjugation may make predictions feel unnatural; a Spanish-specific map would be a future improvement

## Files to Modify

| File | Change |
|------|--------|
| `vocabulary.json` | Add `_es` fields; add `sentence_templates_es` top-level key |
| `data/amiga-aac-vocabulary_20260507.json` | Same (keep in sync as source snapshot) |
| `app.js` | Language state, `UI_STRINGS`, resolver functions, toggle handler, update all render calls |
| `index.html` | Add toggle button; move static text to JS-driven updates |
| `style.css` | Toggle button styling |
| `scripts/translate_vocabulary.py` | New script to batch-populate `_es` fields |
