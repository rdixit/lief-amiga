# Meaning Room Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Meaning Room spatial navigation view to the LiefAAC demo — scene image with glowing hotspots, anchor-grid drill-in, and a toggle to swap between Room and Tabs+Grid views.

**Architecture:** Two-view state machine (`meaning_room` / `grid_tabs`) with an `anchor_grid` sub-state. Config-driven anchors in `data/meaning_room.json`; view default + toggle in `vocabulary.json` `app_config`. All rendering in `app.js`; styles in `style.css`; HTML skeleton in `index.html`.

**Tech Stack:** Vanilla HTML/CSS/JS (ES modules), no build step, no frameworks, no dependencies.

---

## File Structure

| File | Responsibility |
|---|---|
| `vocabulary.json` | Add `app_config` block (default view, toggle visibility, auto-return delay) |
| `data/meaning_room.json` | All 11 anchors: ids, labels, icons, hotspot rects, symbol_ids, stress glow curves |
| `index.html` | Restructure `.ipad-screen` body into view containers; add toggle button; move tab bar |
| `style.css` | Meaning Room stage, hotspot glow, anchor-grid header, toggle button, icon overlay |
| `app.js` | Load room config, view state machine, render functions, glow updates, toggle + persistence |

---

## Task 1: Add `app_config` to `vocabulary.json`

**Files:**
- Modify: `vocabulary.json` (top-level, after `"meta"` block)

- [ ] **Step 1: Add the `app_config` block**

Open `vocabulary.json`. Immediately after the `"meta": { ... }` block and before `"tabs"`, insert:

```json
  "app_config": {
    "default_view": "meaning_room",
    "show_view_toggle": true,
    "auto_return_to_scene_ms": 0
  },
```

- [ ] **Step 2: Load `app_config` in `app.js`**

In `app.js`, in the `loadVocabulary()` function, after the line `AFFECT_SUGGESTIONS = VOCAB.affect_suggestions;`, add:

```js
  APP_CONFIG = VOCAB.app_config || {};
```

At the top of `app.js`, near the other `let` declarations (around line 7-13), add:

```js
let APP_CONFIG = {};
```

- [ ] **Step 3: Verify**

Run: `python3 -m http.server`
Open: `http://localhost:8000`
Expected: App loads normally, no console errors. `APP_CONFIG` is accessible (type `APP_CONFIG` in console → shows the object).

---

## Task 2: Create `data/meaning_room.json`

**Files:**
- Create: `data/meaning_room.json`

- [ ] **Step 1: Create the config file with all 11 anchors**

Create `data/meaning_room.json` with the following content. Hotspot coordinates are normalized `[0..1]` and eyeballed against `assets/images/meaning_room_v0.png` (1402×1122).

```json
{
  "image": "assets/images/meaning_room_v0.png",
  "image_natural_size": [1402, 1122],
  "default_glow_intensity": 0.35,
  "stress_glow_curve_default": [0.30, 0.35, 0.45, 0.55, 0.70],
  "deferred_anchors": ["body", "cognition", "relationships"],
  "anchors": [
    {
      "id": "self",
      "label": "Me",
      "icon": null,
      "hotspot": { "x": 0.30, "y": 0.15, "w": 0.16, "h": 0.55 },
      "symbol_ids": ["i", "me", "my", "mine"],
      "stress_glow_curve": null
    },
    {
      "id": "actions",
      "label": "Actions",
      "icon": "⚡",
      "hotspot": { "x": 0.20, "y": 0.72, "w": 0.14, "h": 0.14 },
      "symbol_ids": [
        "want", "need", "like", "do", "make", "open", "close", "put", "take",
        "see", "feel", "turn", "work", "know", "more", "all_done", "good", "yes",
        "want_help", "want_item", "i_like_this",
        "eat", "drink", "play", "go", "walk", "help", "hug", "jump", "run",
        "push", "read", "sleep"
      ],
      "stress_glow_curve": null
    },
    {
      "id": "other_people",
      "label": "People",
      "icon": null,
      "hotspot": { "x": 0.62, "y": 0.40, "w": 0.18, "h": 0.45 },
      "symbol_ids": ["you", "mom", "dad", "them", "their", "your"],
      "stress_glow_curve": null
    },
    {
      "id": "time",
      "label": "Time",
      "icon": null,
      "hotspot": { "x": 0.02, "y": 0.02, "w": 0.14, "h": 0.18 },
      "symbol_ids": ["one_more_minute"],
      "stress_glow_curve": null
    },
    {
      "id": "stop_refusal",
      "label": "Stop",
      "icon": null,
      "hotspot": { "x": 0.14, "y": 0.02, "w": 0.10, "h": 0.14 },
      "symbol_ids": ["stop", "no", "not", "cant", "wont", "i_dont_want_that", "no_i_dont_want_that"],
      "stress_glow_curve": [0.35, 0.45, 0.60, 0.80, 1.00]
    },
    {
      "id": "outside",
      "label": "Outside",
      "icon": null,
      "hotspot": { "x": 0.62, "y": 0.02, "w": 0.26, "h": 0.35 },
      "symbol_ids": ["go", "home", "walk", "playground", "gym", "classroom"],
      "stress_glow_curve": null
    },
    {
      "id": "calm_corner",
      "label": "Calm",
      "icon": null,
      "hotspot": { "x": 0.52, "y": 0.28, "w": 0.16, "h": 0.18 },
      "symbol_ids": [
        "i_need_a_break", "break", "space", "sleep", "help", "help_me",
        "i_need_help", "too_loud", "too_loud_i_need_a_break", "help_me_im_frustrated"
      ],
      "stress_glow_curve": [0.30, 0.45, 0.65, 0.85, 1.00]
    },
    {
      "id": "toys",
      "label": "Toys",
      "icon": null,
      "hotspot": { "x": 0.02, "y": 0.55, "w": 0.22, "h": 0.35 },
      "symbol_ids": [
        "toy", "play", "balloon", "puzzle", "play_doh", "doll", "bubbles",
        "game", "music", "ipad", "books", "read", "car", "train", "boat",
        "airplane", "bus", "slide", "spin", "squeeze", "swing", "tickle",
        "ticklesqueeze", "jump", "run", "push", "hug"
      ],
      "stress_glow_curve": null
    },
    {
      "id": "food_drink",
      "label": "Food",
      "icon": null,
      "hotspot": { "x": 0.60, "y": 0.70, "w": 0.30, "h": 0.25 },
      "symbol_ids": [
        "water", "juice", "fruit", "cookie", "candy", "popcorn", "pretzel",
        "rice", "carrot", "chips", "eat", "drink", "i_want_water",
        "i_want_food", "i_want_apple"
      ],
      "stress_glow_curve": null
    },
    {
      "id": "clothing",
      "label": "Clothes",
      "icon": null,
      "hotspot": { "x": 0.02, "y": 0.22, "w": 0.14, "h": 0.30 },
      "symbol_ids": ["shirt", "jacket", "i_want_a_jacket", "coat", "hat", "pants", "shoe", "sock"],
      "stress_glow_curve": null
    },
    {
      "id": "colors_descriptors",
      "label": "Colors",
      "icon": null,
      "hotspot": { "x": 0.50, "y": 0.02, "w": 0.14, "h": 0.08 },
      "symbol_ids": [
        "red", "orange", "yellow", "green", "blue", "purple", "pink",
        "black", "white", "big", "little", "fast", "slow",
        "happy", "sad", "mad", "tired", "sick", "frustrated", "nervous"
      ],
      "stress_glow_curve": null
    }
  ]
}
```

- [ ] **Step 2: Load the room config in `app.js`**

In `app.js`, add a new global variable near the top (next to the other `let` declarations):

```js
let ROOM_CONFIG = null;
```

Add a new loader function after `loadVocabulary()`:

```js
async function loadRoomConfig() {
  const res = await fetch('./data/meaning_room.json');
  ROOM_CONFIG = await res.json();
}
```

In `init()`, call it right after `loadVocabulary()`:

```js
async function init() {
  await loadVocabulary();
  await loadRoomConfig();
  // ... rest of init
}
```

- [ ] **Step 3: Verify**

Reload `http://localhost:8000`.
Expected: No console errors. Type `ROOM_CONFIG` in console → shows the full object with 11 anchors. Type `ROOM_CONFIG.anchors.length` → `11`.

---

## Task 3: Restructure HTML — view containers + toggle button

**Files:**
- Modify: `index.html`

This task restructures the `.ipad-screen` body so the tab bar, symbol grid, and new meaning room view are wrapped in switchable containers.

- [ ] **Step 1: Replace the tab bar + symbol grid section**

In `index.html`, replace this block (lines 27-53):

```html
        <!-- Tab bar -->
        <div class="tab-bar" id="tabBar"></div>

        <!-- Sentence bar -->
        <div class="sentence-bar">
          <div class="sentence-display" id="sentenceDisplay">
            <span class="placeholder">Tap symbols below to build a sentence...</span>
          </div>
          <div class="sentence-controls">
            <button class="btn-speak" id="btnSpeak" title="Speak sentence">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M11 5L6 9H2v6h4l5 4V5z"/>
                <path d="M19.07 4.93a10 10 0 010 14.14M15.54 8.46a5 5 0 010 7.08" stroke-linecap="round"/>
              </svg>
            </button>
            <button class="btn-clear" id="btnClear" title="Clear sentence">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Selected symbols strip -->
        <div class="selected-strip" id="selectedStrip"></div>

        <!-- Symbol grid -->
        <div class="symbol-grid" id="symbolGrid"></div>
```

With:

```html
        <!-- Sentence bar -->
        <div class="sentence-bar">
          <div class="sentence-display" id="sentenceDisplay">
            <span class="placeholder">Tap symbols below to build a sentence...</span>
          </div>
          <div class="sentence-controls">
            <button class="btn-speak" id="btnSpeak" title="Speak sentence">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M11 5L6 9H2v6h4l5 4V5z"/>
                <path d="M19.07 4.93a10 10 0 010 14.14M15.54 8.46a5 5 0 010 7.08" stroke-linecap="round"/>
              </svg>
            </button>
            <button class="btn-clear" id="btnClear" title="Clear sentence">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Selected symbols strip -->
        <div class="selected-strip" id="selectedStrip"></div>

        <!-- === VIEW BODY: exactly one visible at a time === -->

        <!-- Meaning Room view -->
        <div class="view-body" id="meaningRoomView">
          <div class="meaning-room-stage" id="meaningRoomStage"></div>
        </div>

        <!-- Anchor grid view (drills in from Meaning Room) -->
        <div class="view-body hidden" id="anchorGridView">
          <div class="anchor-grid-header" id="anchorGridHeader">
            <button class="anchor-back-btn" id="anchorBackBtn">← Back to scene</button>
            <span class="anchor-grid-label" id="anchorGridLabel"></span>
          </div>
          <div class="symbol-grid" id="anchorGrid"></div>
        </div>

        <!-- Tabs + Grid view -->
        <div class="view-body hidden" id="gridTabsView">
          <div class="tab-bar" id="tabBar"></div>
          <div class="symbol-grid" id="symbolGrid"></div>
        </div>
```

- [ ] **Step 2: Add the view toggle button next to Break**

Immediately before the existing `<button id="btnBreak" ...>` element, add:

```html
        <!-- View toggle button -->
        <button id="btnViewToggle" class="btn-view-toggle" title="Switch view">
          <span>▦ Grid</span>
        </button>
```

- [ ] **Step 3: Verify**

Reload `http://localhost:8000`.
Expected: The page loads but the grid may not render (the `symbolGrid` container moved). No crash. We'll wire up rendering in Task 5. The toggle button should be visible (unstyled) at bottom of screen.

---

## Task 4: Add CSS for Meaning Room, hotspots, anchor grid, and toggle

**Files:**
- Modify: `style.css`

- [ ] **Step 1: Add view-body base styles**

Append to `style.css`, before the `/* Responsive */` media query section:

```css
/* === View body containers === */
.view-body {
  flex: 1 1 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.view-body.hidden { display: none; }

/* === Meaning Room === */
.meaning-room-stage {
  position: relative;
  width: 100%;
  flex: 1 1 0;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.meaning-room-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  user-select: none;
  -webkit-user-select: none;
  pointer-events: none;
}

/* Hotspot overlays */
.mr-hotspot {
  position: absolute;
  background: transparent;
  border: 0;
  border-radius: 12px;
  cursor: pointer;
  transition: box-shadow 0.3s ease, background 0.15s ease;
  box-shadow:
    0 0 calc(12px * var(--glow, 0.35)) calc(2px * var(--glow, 0.35))
      rgba(255, 220, 120, calc(0.55 * var(--glow, 0.35))),
    inset 0 0 calc(20px * var(--glow, 0.35))
      rgba(255, 220, 120, calc(0.30 * var(--glow, 0.35)));
  display: flex;
  align-items: center;
  justify-content: center;
}

.mr-hotspot:hover,
.mr-hotspot:focus-visible {
  background: rgba(255, 220, 120, 0.12);
  box-shadow:
    0 0 24px 6px rgba(255, 220, 120, 0.65),
    inset 0 0 28px rgba(255, 220, 120, 0.45);
  outline: none;
}
.mr-hotspot:active { transform: scale(0.97); }

.mr-hotspot-icon {
  font-size: 28px;
  line-height: 1;
  filter: drop-shadow(0 1px 3px rgba(0,0,0,0.25));
  pointer-events: none;
}

/* === Anchor grid header === */
.anchor-grid-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f1f5f9;
  border-bottom: 2px solid #e2e8f0;
  flex-shrink: 0;
}

.anchor-back-btn {
  background: rgba(74, 144, 217, 0.12);
  border: 1.5px solid rgba(74, 144, 217, 0.3);
  border-radius: 8px;
  color: #4a90d9;
  font-size: 13px;
  font-weight: 700;
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.anchor-back-btn:hover {
  background: rgba(74, 144, 217, 0.22);
}
.anchor-back-btn:active { transform: scale(0.95); }

.anchor-grid-label {
  font-size: 15px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #334155;
}

/* === View toggle button (mirrors .btn-break positioning) === */
.btn-view-toggle {
  position: absolute;
  bottom: 6px;
  left: 6px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(224, 242, 254, 0.92);
  color: #0369a1;
  border: 1.5px solid #7dd3fc;
  border-radius: 20px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  font-family: inherit;
}
.btn-view-toggle:hover {
  background: rgba(186, 230, 253, 0.95);
  transform: scale(1.05);
}
.btn-view-toggle:active { transform: scale(0.95); }
.btn-view-toggle.hidden { display: none; }
```

- [ ] **Step 2: Update the responsive media query**

Inside the existing `@media (max-width: 600px)` block, add:

```css
  .mr-hotspot-icon { font-size: 22px; }
  .anchor-back-btn { font-size: 11px; padding: 5px 8px; }
  .anchor-grid-label { font-size: 13px; }
  .btn-view-toggle { padding: 4px 8px; font-size: 10px; }
```

- [ ] **Step 3: Verify**

Reload `http://localhost:8000`.
Expected: Toggle button visible bottom-left, styled as a pill. The main content area may be empty (Meaning Room rendering not wired yet). No console errors.

---

## Task 5: Implement view state machine in `app.js`

**Files:**
- Modify: `app.js`

This is the core wiring: view switching, Meaning Room rendering, and Tabs+Grid rendering in their new containers.

- [ ] **Step 1: Add view state variables and DOM refs**

In `app.js`, near the existing DOM reference block (around line 96), add these new refs:

```js
const meaningRoomView = document.getElementById('meaningRoomView');
const meaningRoomStage = document.getElementById('meaningRoomStage');
const anchorGridView = document.getElementById('anchorGridView');
const anchorGridHeader = document.getElementById('anchorGridHeader');
const anchorGridLabel = document.getElementById('anchorGridLabel');
const anchorGrid = document.getElementById('anchorGrid');
const anchorBackBtn = document.getElementById('anchorBackBtn');
const gridTabsView = document.getElementById('gridTabsView');
const btnViewToggle = document.getElementById('btnViewToggle');
```

Near the existing `let activeTab = 'core';` line, add:

```js
let currentView = 'meaning_room';
let currentAnchor = null;
```

- [ ] **Step 2: Add the view rendering functions**

Add these functions in `app.js`, after the `clearAll()` function and before the utility section:

```js
// ============================================================
// View state machine
// ============================================================

const VIEW_CONTAINERS = {
  meaning_room: () => meaningRoomView,
  anchor_grid: () => anchorGridView,
  grid_tabs: () => gridTabsView,
};

function setView(view, anchor) {
  currentView = view;
  if (anchor !== undefined) currentAnchor = anchor;

  meaningRoomView.classList.add('hidden');
  anchorGridView.classList.add('hidden');
  gridTabsView.classList.add('hidden');

  const container = VIEW_CONTAINERS[view]?.();
  if (container) container.classList.remove('hidden');

  if (view === 'meaning_room') renderMeaningRoom();
  if (view === 'anchor_grid' && currentAnchor) renderAnchorGrid(currentAnchor);
  if (view === 'grid_tabs') { renderTabs(); renderGrid(); }

  renderViewToggleButton();
  localStorage.setItem('liefaac.view', view === 'anchor_grid' ? 'meaning_room' : view);
}

function loadInitialView() {
  return localStorage.getItem('liefaac.view')
    || APP_CONFIG.default_view
    || 'meaning_room';
}

function renderViewToggleButton() {
  if (!APP_CONFIG.show_view_toggle) {
    btnViewToggle.classList.add('hidden');
    return;
  }
  btnViewToggle.classList.remove('hidden');
  const isRoom = currentView === 'meaning_room' || currentView === 'anchor_grid';
  btnViewToggle.innerHTML = isRoom
    ? '<span>▦ Grid</span>'
    : '<span>🏠 Room</span>';
  btnViewToggle.title = isRoom ? 'Switch to Grid view' : 'Switch to Room view';
}

// ============================================================
// Meaning Room rendering
// ============================================================

function renderMeaningRoom() {
  if (!ROOM_CONFIG) return;
  meaningRoomStage.innerHTML = '';

  const img = document.createElement('img');
  img.className = 'meaning-room-img';
  img.src = ROOM_CONFIG.image;
  img.alt = 'Meaning Room scene';
  img.draggable = false;
  meaningRoomStage.appendChild(img);

  const stressZone = parseInt(mockValenceSlider.value, 10);

  ROOM_CONFIG.anchors.forEach(anchor => {
    const btn = document.createElement('button');
    btn.className = 'mr-hotspot';
    btn.dataset.anchorId = anchor.id;
    btn.setAttribute('aria-label', anchor.label);

    const h = anchor.hotspot;
    btn.style.left = `${h.x * 100}%`;
    btn.style.top = `${h.y * 100}%`;
    btn.style.width = `${h.w * 100}%`;
    btn.style.height = `${h.h * 100}%`;

    const glow = effectiveGlow(anchor, stressZone);
    btn.style.setProperty('--glow', glow.toFixed(2));

    if (anchor.icon) {
      const iconEl = document.createElement('span');
      iconEl.className = 'mr-hotspot-icon';
      iconEl.textContent = anchor.icon;
      btn.appendChild(iconEl);
    }

    btn.addEventListener('click', () => setView('anchor_grid', anchor));
    meaningRoomStage.appendChild(btn);
  });
}

function effectiveGlow(anchor, stressZone) {
  const curve = anchor.stress_glow_curve || ROOM_CONFIG.stress_glow_curve_default;
  const idx = Math.max(0, Math.min(4, stressZone - 1));
  return curve[idx] ?? ROOM_CONFIG.default_glow_intensity;
}

function updateMeaningRoomGlow() {
  if (currentView !== 'meaning_room') return;
  const stressZone = parseInt(mockValenceSlider.value, 10);
  meaningRoomStage.querySelectorAll('.mr-hotspot').forEach(btn => {
    const anchorId = btn.dataset.anchorId;
    const anchor = ROOM_CONFIG.anchors.find(a => a.id === anchorId);
    if (!anchor) return;
    const glow = effectiveGlow(anchor, stressZone);
    btn.style.setProperty('--glow', glow.toFixed(2));
  });
}

// ============================================================
// Anchor grid rendering
// ============================================================

function renderAnchorGrid(anchor) {
  anchorGridLabel.textContent = anchor.label;

  anchorGrid.innerHTML = '';
  const symMap = new Map(SYMBOLS.map(s => [s.id, s]));

  anchor.symbol_ids.forEach(id => {
    const sym = symMap.get(id);
    if (!sym) return;

    const svgContent = getSymbolSVG(sym);
    const card = document.createElement('button');
    card.className = 'symbol-card';
    card.dataset.id = sym.id;
    card.dataset.tab = sym.ui_tab;
    card.dataset.pos = sym.part_of_speech || 'word';

    card.innerHTML = `
      <div class="symbol-icon">${svgContent}</div>
      <div class="symbol-label">${escapeHtml(sym.display_label)}</div>
    `;
    card.addEventListener('click', () => {
      handleSymbolTap(sym);
      const delay = APP_CONFIG.auto_return_to_scene_ms || 0;
      if (delay > 0) {
        setTimeout(() => setView('meaning_room'), delay);
      } else {
        setView('meaning_room');
      }
    });
    anchorGrid.appendChild(card);
  });
}
```

- [ ] **Step 3: Wire up event listeners**

In the `setupEventListeners()` function in `app.js`, add:

```js
  btnViewToggle.addEventListener('click', () => {
    const isRoom = currentView === 'meaning_room' || currentView === 'anchor_grid';
    setView(isRoom ? 'grid_tabs' : 'meaning_room');
  });

  anchorBackBtn.addEventListener('click', () => setView('meaning_room'));
```

Also, in the existing `mockValenceSlider` `input` handler (the one that calls `renderQuickPhrases()` and `updateSuggestions()`), add a call to `updateMeaningRoomGlow()`:

```js
  mockValenceSlider.addEventListener('input', () => {
    // ... existing code ...
    updateMeaningRoomGlow();
  });
```

- [ ] **Step 4: Update `init()` to use view state**

Replace the body of `init()` with:

```js
async function init() {
  await loadVocabulary();
  await loadRoomConfig();
  setupEventListeners();
  renderAffectWidget();
  renderQuickPhrases();

  const initialView = loadInitialView();
  setView(initialView);
}
```

This replaces the old `renderTabs(); renderGrid(); updateSuggestions();` calls — `setView('grid_tabs')` handles those internally, and `setView('meaning_room')` renders the room.

- [ ] **Step 5: Verify Meaning Room view**

Reload `http://localhost:8000`.
Expected:
1. The Meaning Room image fills the body area with 11 glowing hotspot rectangles overlaid
2. The Actions hotspot shows the ⚡ icon
3. Hovering a hotspot brightens its glow
4. The toggle button in the bottom-left says "▦ Grid"
5. No console errors

- [ ] **Step 6: Verify toggle to Tabs+Grid**

Click the "▦ Grid" toggle button.
Expected:
1. The Meaning Room disappears; the tab bar + symbol grid appear
2. The toggle button now says "🏠 Room"
3. Tabs and grid work normally (click tabs, symbols render, Fitzgerald colors apply)
4. Click "🏠 Room" → returns to Meaning Room with hotspots

- [ ] **Step 7: Verify anchor grid drill-in**

From the Meaning Room, click the "Toys" hotspot (lower-left toy box area).
Expected:
1. View switches to anchor grid showing "← Back to scene" button and "TOYS" label
2. Grid contains toy/play symbols (balloon, puzzle, car, etc.)
3. Click any symbol → it appears in the selected strip + sentence bar, and view auto-returns to the Meaning Room
4. Click "← Back to scene" → returns to Meaning Room without adding a symbol

- [ ] **Step 8: Verify stress glow**

Return to Meaning Room. Move the simulated stress slider from Zone 1 to Zone 5.
Expected: The `calm_corner` and `stop_refusal` hotspots glow noticeably more at Zone 5 than other hotspots. The Actions and Self hotspots glow moderately. Colors/descriptors glow least.

---

## Task 6: Persist view choice in localStorage

**Files:**
- Modify: `app.js` (already partially done in Task 5)

- [ ] **Step 1: Verify persistence**

This was wired in Task 5 (`setView` writes `localStorage`, `loadInitialView` reads it). Verify:

1. Load page → Meaning Room shows (default)
2. Toggle to Grid → reload page → Grid shows (persisted)
3. Toggle back to Room → reload → Room shows
4. Open console, run `localStorage.removeItem('liefaac.view')` → reload → Meaning Room shows (falls back to `app_config.default_view`)

- [ ] **Step 2: Verify `default_view` config change**

Edit `vocabulary.json`: change `"default_view": "meaning_room"` to `"default_view": "grid_tabs"`.
Clear localStorage: `localStorage.removeItem('liefaac.view')`.
Reload page.
Expected: Grid view loads as default.

Revert `vocabulary.json` back to `"default_view": "meaning_room"` after testing.

---

## Task 7: Verify all exit criteria

**Files:** None (verification only)

- [ ] **Step 1: Run through all 10 exit criteria from spec §13**

1. ✓ App loads with Meaning Room as default
2. ✓ Room image renders with 11 hotspots (Actions has ⚡ overlay)
3. ✓ Stress slider 1→5 increases glow on calm/stop more than colors
4. ✓ Tapping any anchor opens anchor grid with "← Back to scene"
5. ✓ Tapping symbol in anchor grid adds to sentence and returns to room
6. ✓ Toggle switches views; persists across reloads
7. ✓ Changing `default_view` to `"grid_tabs"` + clearing localStorage → Grid loads
8. ✓ In Grid view, tab bar is above symbol grid (not above sentence builder)
9. ✓ Break button accessible from every view
10. ✓ No console errors; quick phrases, prediction, breathing modal, affect widget all work

- [ ] **Step 2: Test sentence building end-to-end**

Build a sentence: tap "Me" (self anchor) → tap "want" (actions anchor) → tap "water" (food anchor).
Expected: Selected strip shows three symbols. Sentence prediction generates something like "I want water." Speak button works.

- [ ] **Step 3: Test Break from each view**

Click Break from: Meaning Room, anchor grid, Tabs+Grid.
Expected: Break modal appears every time. "I'm ready!" returns to the previous view.

---

*End of implementation plan. Each task is self-contained and verifiable. Commit after each task passes verification.*
