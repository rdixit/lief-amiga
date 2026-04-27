# Lief Affect Integration — AMIGA-AAC

> **Status:** In progress — Week of 2026-04-24  
> **Goal:** Add real-time HRV/affect signal from Lief wearable into the AAC prediction pipeline  
> **Owner:** Mike Pesavento (PezTek consulting)

---

## Overview

The Lief device is a chest-worn biofeedback wearable that provides real-time HRV and
physiological stress/anxiety markers via BLE. This document describes the plan to:

1. Add a **valence/arousal UI widget** (emoji-based) showing current emotional state
2. Build a **BLE connection hook** to receive real-time HRV data from the Lief device
3. **Modulate GPT prediction** (system prompt + temperature) based on affect state
4. Map Lief HRV **quintile/quartile scores** → valence buckets → emoji display

The first implementation milestone (by end of week, ~2026-04-27) is a **functional placeholder**:
mock state object, visible emoji widget, wired prediction hook, and BLE scaffold with UUID
stubs — enough to demonstrate the full integration path at the Monday team meeting.

---

## Architecture

```
┌─────────────────────┐     BLE Notifications
│   Lief Device        │ ──────────────────────────────────►  connectLief()
│  (HRV / stress)     │                                         │
└─────────────────────┘                                         ▼
                                                        handleHRVData()
                                                                │
                                                                ▼
                                                        liefState = {
                                                          hrv: <rmssd>,
                                                          quintile: 0–4,
                                                          valence: 0.0–1.0,
                                                          arousal: 0.0–1.0,
                                                          source: 'lief-ble' | 'mock'
                                                        }
                                                                │
                                          ┌─────────────────────┤
                                          ▼                     ▼
                                   Emoji Widget          GPT Prompt Builder
                                   (valence →           (stress context injection
                                    emoji display)       + temperature modulation)
```

---

## 1. `liefState` Object

Central state object. Initialize as mock; swap source to `'lief-ble'` on real connection.

```javascript
let liefState = {
  hrv: null,          // Raw RMSSD value from device (ms), null if no connection
  quintile: null,     // 0–4, mapped from Lief DB quintile scores (0=most stressed)
  valence: 0.5,       // 0.0 (distressed) → 1.0 (calm/positive), derived from quintile
  arousal: 0.5,       // 0.0 (low energy) → 1.0 (high energy), secondary axis
  source: 'mock',     // 'mock' | 'lief-ble'
  lastUpdated: null,  // timestamp of last reading
};
```

### Quintile → Valence Mapping

Lief uses quintile/quartile scoring relative to the user's own HRV baseline. Higher quintile
= higher HRV = calmer state.

```javascript
const QUINTILE_TO_VALENCE = {
  0: 0.1,  // Most stressed — 😫
  1: 0.3,  // Stressed      — 😟
  2: 0.5,  // Neutral        — 😐
  3: 0.7,  // Calm           — 🙂
  4: 0.9,  // Most calm      — 😊
};

function quintileToValence(q) {
  return QUINTILE_TO_VALENCE[q] ?? 0.5;
}
```

> **Note:** Initially this mapping is approximate. Once we have access to the Lief DB/API
> to pull actual quintile boundaries per user, this should be calibrated to real baselines.
> The DB integration is a Phase I stretch goal — see open questions below.

---

## 2. Valence Emoji Widget

A small persistent UI element. Displays current affect state. Shows `(simulated)` badge
when running on mock data so testers/reviewers understand the status.

```javascript
const VALENCE_EMOJIS = [
  { threshold: 0.2, emoji: '😫', label: 'High stress' },
  { threshold: 0.4, emoji: '😟', label: 'Stressed' },
  { threshold: 0.6, emoji: '😐', label: 'Neutral' },
  { threshold: 0.8, emoji: '🙂', label: 'Calm' },
  { threshold: 1.1, emoji: '😊', label: 'Very calm' },
];

function getValenceEmoji(valence) {
  return VALENCE_EMOJIS.find(v => valence < v.threshold) ?? VALENCE_EMOJIS[4];
}

function renderAffectWidget() {
  const { emoji, label } = getValenceEmoji(liefState.valence);
  const sourceLabel = liefState.source === 'mock' ? ' (simulated)' : '';
  const hrvDisplay = liefState.hrv ? ` · HRV ${liefState.hrv}ms` : '';
  
  document.getElementById('lief-affect-widget').innerHTML = `
    <span class="affect-emoji" title="${label}">${emoji}</span>
    <span class="affect-label">${label}${hrvDisplay}</span>
    <span class="affect-source">${sourceLabel}</span>
  `;
}
```

**HTML placement** — add above or alongside the sentence strip:

```html
<div id="lief-affect-widget" class="lief-affect-panel">
  <!-- Populated by renderAffectWidget() -->
</div>
<button id="lief-connect-btn" onclick="connectLief()">🫀 Connect Lief</button>
```

---

## 3. BLE Connection Hook

Uses the Web Bluetooth API. Works in Chrome/Edge (desktop + Android). **Does not work in
Safari or Firefox** — flag this for the demo environment.

```javascript
// ⚠️  PLACEHOLDER — replace with real Lief GATT UUIDs from Rohan / Lief device docs
const LIEF_SERVICE_UUID      = 'TBD';   // e.g. '0000180d-0000-1000-8000-00805f9b34fb'
const LIEF_HRV_CHAR_UUID     = 'TBD';   // HRV/RMSSD characteristic
const LIEF_QUINTILE_CHAR_UUID = 'TBD';  // Quintile score characteristic (if available)

let liefDevice = null;

async function connectLief() {
  const btn = document.getElementById('lief-connect-btn');
  
  if (!navigator.bluetooth) {
    alert('Web Bluetooth not supported. Use Chrome or Edge on desktop/Android.');
    return;
  }
  
  try {
    btn.textContent = '🔄 Connecting...';
    btn.disabled = true;
    
    liefDevice = await navigator.bluetooth.requestDevice({
      filters: [{ namePrefix: 'Lief' }],
      optionalServices: [LIEF_SERVICE_UUID],
    });
    
    liefDevice.addEventListener('gattserverdisconnected', onLiefDisconnected);
    
    const server  = await liefDevice.gatt.connect();
    const service = await server.getPrimaryService(LIEF_SERVICE_UUID);
    const hrvChar = await service.getCharacteristic(LIEF_HRV_CHAR_UUID);
    
    await hrvChar.startNotifications();
    hrvChar.addEventListener('characteristicvaluechanged', handleHRVData);
    
    liefState.source = 'lief-ble';
    btn.textContent = '🫀 Lief Connected';
    btn.style.color = 'green';
    
  } catch (err) {
    console.error('Lief BLE error:', err);
    btn.textContent = '🫀 Connect Lief';
    btn.disabled = false;
    // Fall back to mock gracefully — don't crash the AAC tool
  }
}

function handleHRVData(event) {
  const dataView = event.target.value;
  // TODO: parse actual byte format from Lief device spec
  // Placeholder: assume first uint16 is RMSSD in ms
  const rmssd = dataView.getUint16(0, /*littleEndian=*/true);
  
  liefState.hrv = rmssd;
  liefState.lastUpdated = Date.now();
  
  // TODO: derive quintile from RMSSD using user baseline
  // For now: rough RMSSD → valence mapping (replace with Lief quintile API)
  liefState.valence = Math.min(1.0, rmssd / 80);  // 80ms RMSSD ≈ very calm
  
  renderAffectWidget();
}

function onLiefDisconnected() {
  liefState.source = 'mock';
  const btn = document.getElementById('lief-connect-btn');
  btn.textContent = '🫀 Connect Lief';
  btn.disabled = false;
  btn.style.color = '';
  console.log('Lief device disconnected — falling back to mock state');
}
```

---

## 4. Affect → Prediction Modulation

Two levers, both active. Prompt injection is the primary and most legible to stakeholders;
temperature modulation is a secondary fine-tune.

### 4a. System Prompt Injection

```javascript
function buildAffectSystemPrompt(liefState) {
  let affectContext = '';
  
  if (liefState.valence < 0.35) {
    affectContext = `The user appears anxious or highly stressed (HRV signal low). 
Prioritize short, simple, calming phrases. Avoid complex constructions. 
Prefer: needs, requests for comfort, simple statements.`;
  } else if (liefState.valence < 0.55) {
    affectContext = `The user shows mild stress. Prefer clear, direct sentences.`;
  } else if (liefState.valence < 0.75) {
    affectContext = `The user appears calm and regulated. Suggest natural, expressive sentences.`;
  } else {
    affectContext = `The user is very calm and engaged. Support rich, expressive communication.`;
  }
  
  return `You are an AAC (Augmentative and Alternative Communication) assistant helping 
a user with autism build sentences from symbol selections.

${affectContext}

Rules:
- Suggest exactly 3 likely sentence completions from the provided symbols
- Only use concepts grounded in the selected symbols (anti-hallucination)
- Keep suggestions under 12 words each
- Vary complexity across the 3 options (simple → more expressive)
- Return as JSON array: ["sentence 1", "sentence 2", "sentence 3"]`;
}
```

### 4b. Temperature Modulation

```javascript
function getAffectTemperature(liefState) {
  // High stress → lower temp → more conservative/predictable
  // Calm        → higher temp → more expressive/varied
  return 0.25 + (liefState.valence * 0.65);  // Range: 0.25 → 0.90
}
```

### Integration with Existing GPT Call

```javascript
// In the existing prediction function, replace static system prompt + temp with:
const response = await fetch('https://api.openai.com/v1/chat/completions', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'gpt-4o-mini',
    temperature: getAffectTemperature(liefState),   // ← affect-modulated
    messages: [
      { role: 'system', content: buildAffectSystemPrompt(liefState) },  // ← affect-aware
      { role: 'user', content: `Selected symbols: ${selectedSymbols.join(', ')}` }
    ]
  })
});
```

---

## 5. Week 1 Milestone Checklist

**Target: Sunday 2026-04-27 — functional placeholder in prototype**

- [ ] Add `liefState` mock object to `index.html` / main JS
- [ ] Render affect emoji widget in UI (visible, styled)
- [ ] Add "Connect Lief" button with connect/disconnect/unsupported states
- [ ] Replace static GPT system prompt with `buildAffectSystemPrompt(liefState)`
- [ ] Add `getAffectTemperature()` to GPT call
- [ ] BLE scaffold wired up — UUID constants stubbed as `'TBD'`
- [ ] Mock valence slider or toggle for demo/testing (so Faison team can see affect changing)
- [ ] Confirm works in Chrome (Web Bluetooth target browser)

---

## Open Questions / Blockers

| Question | Owner | Priority |
|---|---|---|
| What are the Lief GATT service + characteristic UUIDs? | Rohan / Lief team | 🔴 Blocking BLE |
| What byte format does the HRV characteristic send? | Lief team | 🔴 Blocking parsing |
| Does Lief expose quintile score over BLE, or only RMSSD? | Lief team | 🟡 Affects mapping |
| Is there a Lief SDK / JS library, or raw BLE only? | Rohan | 🟡 Could simplify |
| Access to Lief DB for per-user quintile baselines? | Rohan / Lief team | 🟠 Phase I stretch goal |
| Target demo browser/device for Faison pilots? | Joannalyn | 🟡 Affects BLE support |

---

## Future: Quintile/Quartile DB Integration

Once Lief DB access is available, replace the raw-RMSSD → valence approximation with
user-personalized quintile scoring:

```
Lief DB → user's personal HRV baseline → quintile boundaries
        → map live RMSSD reading → quintile (0–4)
        → QUINTILE_TO_VALENCE[quintile] → liefState.valence
```

This gives affect readings relative to the individual user's own baseline rather than
a population norm — much more meaningful for communication modulation.

---

## References

- Lief device: [getlief.com](https://getlief.com)
- Web Bluetooth API: [developer.chrome.com/docs/capabilities/bluetooth](https://developer.chrome.com/docs/capabilities/bluetooth)
- AMIGA-AAC prototype: [rdixit.github.io/lief-amiga](https://rdixit.github.io/lief-amiga)
- AMIGA-AAC repo: [github.com/rdixit/lief-amiga](https://github.com/rdixit/lief-amiga)
- SOW: ARPA-H SBIR Phase I, Zenso/Lief Therapeutics
