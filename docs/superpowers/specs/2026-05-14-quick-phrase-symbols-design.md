# Quick Phrase Bar — Symbol Design Spec

**Date:** 2026-05-14  
**Status:** Approved

## Problem

The quick phrase bar currently renders text-only pill buttons. Pre-literate users (target age ~5–10) cannot read the phrases, so the bar is inaccessible without caregiver support.

## Solution

Add an emoji symbol above each label in the quick phrase bar, using a compact stacked layout. Symbols are chosen for immediate recognizability by non-readers.

## Layout

**Style:** Stacked — emoji icon centered above text label  
**Icon size:** 16px  
**Label size:** 10px  
**Button shape:** Rounded rectangle (border-radius: 10–12px), min-width: 54px  
**Bar height:** ~56px (up from 52px, a +4px increase)  
**Padding:** 5px vertical, 10px horizontal

## Symbol Source

Emoji. No new assets required. Universally rendered on iOS and modern Android.

## Symbol Map

| ID | Full phrase | Emoji | Bar label |
|---|---|---|---|
| help_me | Help me. | 🙋 | Help me |
| i_need_a_break | I need a break. | ⏸️ | Need a break |
| too_loud | Too loud. | 🔊 | Too loud |
| i_want_water | I want water. | 💧 | I want water |
| i_need_the_bathroom | I need the bathroom. | 🚽 | Bathroom |
| all_done | All done. | ✅ | All done |
| i_dont_want_that | I don't want that. | 🙅 | Don't want |
| my_turn | My turn. | 🔄 | My turn |
| i_like_this | I like this. | 👍 | I like this |
| im_frustrated | I'm frustrated. | 😡 | Frustrated |
| one_more_minute | One more minute. | ☝️ | 1 more min |
| thats_funny | That's funny. | 😂 | That's funny |
| hi_hello | Hi / Hello. | 👋 | Hi / Hello |

## Data Changes

Add two fields to each entry in the `quick_phrases` array in `vocabulary.json`:

- **`emoji`** — the symbol character  
- **`bar_label`** — short label for display in the bar; falls back to `display_label` if absent

## Code Changes

### vocabulary.json
Add `emoji` and `bar_label` fields to all 13 quick phrase entries.

### app.js — `renderQuickPhrases()`
Update the rendered button HTML to include an emoji span above the label span:

```html
<button class="quick-phrase-btn ...">
  <span class="qp-emoji">🙋</span>
  <span class="qp-label">Help me</span>
</button>
```

### style.css — `.quick-phrase-btn`
Change from horizontal pill to stacked layout:
- `flex-direction: column`
- `align-items: center`
- `gap: 2px`
- `font-size` for label: 10px
- `padding`: 5px 10px
- `border-radius`: 10px
- `min-width`: 54px

Bump `.quick-phrase-bar` `min-height` from 52px to 56px.

## Non-goals

- Custom SVG symbols (emoji is sufficient for prototype stage)
- Symbol customization UI (not in scope)
- Changing which phrases appear in the bar
