// ============================================================
// LiefAAC - AI-Powered AAC Prototype
// ============================================================
import { SYMBOL_SVGS } from './symbols.js';

// --- Vocabulary (loaded async from vocabulary.json) ---
let VOCAB = null;
let SYMBOLS = [];
let QUICK_PHRASES = [];
let TABS = [];
let NEXT_WORD_MAP = {};
let SENTENCE_TEMPLATES = {};
let AFFECT_SUGGESTIONS = {};
let APP_CONFIG = {};
let ROOM_CONFIG = null;

async function loadVocabulary() {
  const res = await fetch(`./vocabulary.json?_=${Date.now()}`);
  VOCAB = await res.json();
  SYMBOLS = VOCAB.symbols.filter(s => s.allowed_for_grid);
  QUICK_PHRASES = VOCAB.quick_phrases;
  TABS = VOCAB.tabs;
  NEXT_WORD_MAP = VOCAB.next_word_map;
  SENTENCE_TEMPLATES = VOCAB.sentence_templates;
  AFFECT_SUGGESTIONS = VOCAB.affect_suggestions;
  APP_CONFIG = VOCAB.app_config || {};
}

async function loadRoomConfig() {
  const res = await fetch(`./meaning_room.json?_=${Date.now()}`);
  ROOM_CONFIG = await res.json();
}

function getSymbolSVG(sym) {
  return SYMBOL_SVGS[sym.id]
    || (sym.svg_key && SYMBOL_SVGS[sym.svg_key])
    || '';
}

// ============================================================
// Lief affect state (Sub-Phase 0 — mock-only)
// ============================================================

let liefState = {
  hrv: null,
  hrv_baseline_z: null,
  quintile: 2,
  valence: 0.7,
  arousal: 0.5,
  confidence: 0.6,
  source: 'mock',
  available_modalities: ['hrv'],
  inferred_category_prior: null,
  lastUpdated: null,
};

const STRESS_ZONES = [
  null,
  { zone: 1, emoji: '😊', label: 'No stress',       valence: 0.9 },
  { zone: 2, emoji: '🙂', label: 'Low stress',      valence: 0.7 },
  { zone: 3, emoji: '😐', label: 'Medium stress',   valence: 0.5 },
  { zone: 4, emoji: '😟', label: 'High stress',     valence: 0.3 },
  { zone: 5, emoji: '😫', label: 'Extreme stress',  valence: 0.1 },
];

function getStressZone(zoneIndex) {
  return STRESS_ZONES[zoneIndex] ?? STRESS_ZONES[3];
}

function getStressZoneFromValence(valence) {
  if (valence >= 0.8) return STRESS_ZONES[1];
  if (valence >= 0.6) return STRESS_ZONES[2];
  if (valence >= 0.4) return STRESS_ZONES[3];
  if (valence >= 0.2) return STRESS_ZONES[4];
  return STRESS_ZONES[5];
}

// Affect-aware suggestion overrides.
// Keys match NEXT_WORD_MAP; values are { stressed: [...], calm: [...] }.
// Stressed = zones 4-5 (valence < 0.4), calm = zone 1 (valence >= 0.8).
// Neutral zones 2-3 use default NEXT_WORD_MAP ordering.
function getAffectAwareSuggestions(key, baseSuggestions) {
  if (liefState.confidence < 0.3) return { ordered: baseSuggestions, highlighted: new Set(baseSuggestions) };
  const override = AFFECT_SUGGESTIONS[key];
  if (!override) return { ordered: baseSuggestions, highlighted: new Set(baseSuggestions) };
  let priority;
  if (liefState.valence <= 0.3) priority = override.stressed;
  else if (liefState.valence >= 0.8) priority = override.calm;
  else return { ordered: baseSuggestions, highlighted: new Set(baseSuggestions) };
  const remaining = baseSuggestions.filter(id => !priority.includes(id));
  return { ordered: [...priority, ...remaining], highlighted: new Set(priority) };
}

// --- App State ---
let selectedSymbols = [];
let activeTab = 'core';
let currentView = 'meaning_room';
let currentAnchor = null;

// Cloudflare Worker proxy URL — set after deploying worker.js to Workers & Pages.
// Leave empty string to fall back to browser TTS / local prediction.
const PROXY_BASE_URL = 'https://lief-aac-proxy.mpesaven.workers.dev';
let pendingRequest = null;

// --- DOM References ---
const quickPhraseBar = document.getElementById('quickPhraseBar');
const qpArrowLeft    = document.getElementById('qpArrowLeft');
const qpArrowRight   = document.getElementById('qpArrowRight');
const tabBar = document.getElementById('tabBar');
const grid = document.getElementById('symbolGrid');
const sentenceDisplay = document.getElementById('sentenceDisplay');
const selectedStrip = document.getElementById('selectedStrip');
const btnSpeak = document.getElementById('btnSpeak');
const btnClear = document.getElementById('btnClear');
const autoSpeakCheckbox = document.getElementById('autoSpeak');
const showSuggestionsCheckbox = document.getElementById('showSuggestions');
const reorderSymbolsCheckbox  = document.getElementById('reorderSymbols');

const confidenceSlider = document.getElementById('confidenceThreshold');
const confidenceValueLabel = document.getElementById('confidenceValue');
const affectEmojiEl = document.getElementById('affectEmoji');
const affectLabelEl = document.getElementById('affectLabel');
const affectSourceEl = document.getElementById('affectSource');
const liefConnectBtn = document.getElementById('liefConnectBtn');
const mockValenceSlider = document.getElementById('mockValenceSlider');
const mockValenceLabel = document.getElementById('mockValenceLabel');
const btnBreak = document.getElementById('btnBreak');
const breakModal = document.getElementById('breakModal');
const breakLanding = document.getElementById('breakLanding');
const btnBreakResume = document.getElementById('btnBreakResume');
const btnStartBreathe = document.getElementById('btnStartBreathe');
const breatheScreen = document.getElementById('breatheScreen');
const breatheCircle = document.getElementById('breatheCircle');
const breatheInstruction = document.getElementById('breatheInstruction');
const breatheTimerFill = document.getElementById('breatheTimerFill');
const breatheTimerLabel = document.getElementById('breatheTimerLabel');
const btnStopBreathe = document.getElementById('btnStopBreathe');

// --- Meaning Room DOM refs ---
const meaningRoomView  = document.getElementById('meaningRoomView');
const meaningRoomStage = document.getElementById('meaningRoomStage');
const anchorGridView   = document.getElementById('anchorGridView');
const anchorGridLabel  = document.getElementById('anchorGridLabel');
const anchorGrid       = document.getElementById('anchorGrid');
const anchorBackBtn    = document.getElementById('anchorBackBtn');
const gridTabsView     = document.getElementById('gridTabsView');
const btnViewToggle    = document.getElementById('btnViewToggle');

// --- Affect widget ---
function renderAffectWidget() {
  const zone = getStressZoneFromValence(liefState.valence);
  affectEmojiEl.textContent = zone.emoji;
  affectLabelEl.textContent = zone.label;
  if (liefState.source === 'mock') {
    affectSourceEl.textContent = '(simulated)';
    affectSourceEl.classList.remove('live');
  } else {
    affectSourceEl.textContent = '(Lief — live)';
    affectSourceEl.classList.add('live');
  }
}

let toastHideTimer = null;

function showToast(message, durationMs = 5200) {
  let host = document.getElementById('toastHost');
  if (!host) {
    host = document.createElement('div');
    host.id = 'toastHost';
    host.className = 'toast-host';
    host.setAttribute('aria-live', 'polite');
    host.setAttribute('aria-atomic', 'true');
    document.body.appendChild(host);
  }

  clearTimeout(toastHideTimer);
  host.replaceChildren();

  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = message;
  host.appendChild(el);

  requestAnimationFrame(() => {
    el.classList.add('toast-visible');
  });

  toastHideTimer = window.setTimeout(() => {
    el.classList.remove('toast-visible');
    const removeAfter = Number.parseFloat(getComputedStyle(el).transitionDuration) * 1000 || 220;
    window.setTimeout(() => el.remove(), removeAfter + 40);
    toastHideTimer = null;
  }, durationMs);
}

// --- Break / Breathing (unchanged) ---
let breatheInterval = null;
let breatheTimeout = null;

function showBreakModal() {
  stopSpeaking();
  stopBreathingExercise();
  breakLanding.classList.remove('hidden');
  breatheScreen.classList.add('hidden');
  breakModal.classList.remove('hidden');
  speakText('I need a break.');
}

function hideBreakModal() {
  stopBreathingExercise();
  breakModal.classList.add('hidden');
}

function startBreathingExercise() {
  breakLanding.classList.add('hidden');
  breatheScreen.classList.remove('hidden');

  const totalSeconds = 60;
  const phaseSeconds = 4;
  let elapsed = 0;
  let isInhale = true;

  breatheTimerFill.style.transition = 'none';
  breatheTimerFill.style.width = '0%';
  updateBreathTimer(totalSeconds);

  breatheCircle.classList.remove('inhale', 'exhale');
  void breatheCircle.offsetWidth;
  setBreathPhase(true);

  breatheInterval = setInterval(() => {
    elapsed++;
    const posInPhase = elapsed % phaseSeconds;
    if (posInPhase === 0) {
      isInhale = !isInhale;
      setBreathPhase(isInhale);
    }
    const pct = Math.min((elapsed / totalSeconds) * 100, 100);
    breatheTimerFill.style.transition = 'width 1s linear';
    breatheTimerFill.style.width = `${pct}%`;
    updateBreathTimer(totalSeconds - elapsed);
    if (elapsed >= totalSeconds) {
      stopBreathingExercise();
      breatheInstruction.textContent = 'Great job!';
      breatheCircle.classList.remove('inhale', 'exhale');
    }
  }, 1000);
}

function setBreathPhase(inhale) {
  if (inhale) {
    breatheCircle.classList.remove('exhale');
    breatheCircle.classList.add('inhale');
    breatheInstruction.textContent = 'Breathe in';
  } else {
    breatheCircle.classList.remove('inhale');
    breatheCircle.classList.add('exhale');
    breatheInstruction.textContent = 'Breathe out';
  }
}

function updateBreathTimer(remaining) {
  const mins = Math.floor(Math.max(0, remaining) / 60);
  const secs = Math.max(0, remaining) % 60;
  breatheTimerLabel.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
}

function stopBreathingExercise() {
  if (breatheInterval) {
    clearInterval(breatheInterval);
    breatheInterval = null;
  }
  breatheCircle.classList.remove('inhale', 'exhale');
}

// ============================================================
// Tab navigation
// ============================================================

function renderTabs() {
  tabBar.innerHTML = TABS.map(tab => `
    <button
      class="tab-btn${activeTab === tab.id ? ' active' : ''}"
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

function getGridSymbols() {
  const sortByFreq = document.getElementById('sortByFrequency').checked;
  let syms = SYMBOLS.filter(s => s.ui_tab === activeTab);
  syms.sort((a, b) => {
    if (a.priority_tier !== b.priority_tier) return a.priority_tier - b.priority_tier;
    if (sortByFreq) {
      const aFreq = (a.sources || []).length;
      const bFreq = (b.sources || []).length;
      if (aFreq !== bFreq) return bFreq - aFreq;
    }
    return a.display_label.localeCompare(b.display_label);
  });
  return syms;
}

// ============================================================
// Quick phrase bar
// ============================================================

function updateQPArrows() {
  const { scrollLeft, scrollWidth, clientWidth } = quickPhraseBar;
  qpArrowLeft.classList.toggle('hidden', scrollLeft <= 2);
  qpArrowRight.classList.toggle('hidden', scrollLeft + clientWidth >= scrollWidth - 2);
}

function renderQuickPhrases() {
  const stressLevel = parseInt(mockValenceSlider.value, 10);
  quickPhraseBar.innerHTML = QUICK_PHRASES.map(qp => {
    const isStressHighlighted = stressLevel >= 3 && qp.affect_priority === 'stressed';
    const label = qp.bar_label || qp.display_label;
    const emojiSpan = qp.emoji ? `<span class="qp-emoji" aria-hidden="true">${qp.emoji}</span>` : '';
    return `<button
      class="quick-phrase-btn${isStressHighlighted ? ' stress-highlighted' : ''}"
      data-utterance="${escapeAttr(qp.utterance)}"
      aria-label="${escapeAttr(qp.display_label)}"
    >${emojiSpan}<span class="qp-label">${escapeHtml(label)}</span></button>`;
  }).join('');

  quickPhraseBar.querySelectorAll('.quick-phrase-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const utterance = btn.dataset.utterance;
      speakText(utterance);
      sentenceDisplay.innerHTML = `<span class="predicted-text">${escapeHtml(utterance)}</span>`;
    });
  });

  // Update arrow visibility after render (content width may have changed)
  requestAnimationFrame(updateQPArrows);
}

// ============================================================
// Grid rendering
// ============================================================

function renderGrid() {
  grid.innerHTML = '';
  const syms = getGridSymbols();
  const key = selectedSymbols.map(s => s.id).join('_');

  // Build suggestion set for this render
  let suggestedIds = getSuggestedIds(key);
  const { highlighted } = getAffectAwareSuggestions(key, suggestedIds);
  const highlightSet = highlighted;

  syms.forEach(sym => {
    const svgContent = getSymbolSVG(sym);
    const isSuggested = highlightSet.has(sym.id);
    const card = document.createElement('button');
    card.className = 'symbol-card' + (isSuggested ? ' suggested' : '');
    card.dataset.id = sym.id;
    card.dataset.tab = sym.ui_tab;
    card.dataset.pos = sym.part_of_speech || 'word';


    card.innerHTML = `
      <div class="symbol-icon">${svgContent}</div>
      <div class="symbol-label">${escapeHtml(sym.display_label)}</div>
    `;
    card.addEventListener('click', () => handleSymbolTap(sym));
    grid.appendChild(card);
  });
}

// ============================================================
// Symbol tap handler
// ============================================================

function handleSymbolTap(sym) {
  // Quick phrases and standalone phrase tiles: speak immediately, don't add to strip
  if (sym.is_quick_phrase) {
    const utterance = sym.phrase_templates?.[0] || sym.display_label;
    speakText(utterance);
    sentenceDisplay.innerHTML = `<span class="predicted-text">${escapeHtml(utterance)}</span>`;
    return;
  }

  selectedSymbols.push(sym);
  renderSelectedStrip();
  updatePrediction();
  updateSuggestions();

  const card = grid.querySelector(`[data-id="${sym.id}"]`);
  if (card) {
    card.style.transform = 'scale(0.9)';
    setTimeout(() => card.style.transform = '', 150);
  }
}

function removeSymbol(index) {
  selectedSymbols.splice(index, 1);
  renderSelectedStrip();
  updatePrediction();
  updateSuggestions();
}

function renderSelectedStrip() {
  selectedStrip.innerHTML = '';
  selectedSymbols.forEach((sym, i) => {
    const svgContent = getSymbolSVG(sym);
    const chip = document.createElement('div');
    chip.className = 'selected-chip';
    // Extract original viewBox so coordinates render correctly at chip size
    const vbMatch = svgContent.match(/viewBox="([^"]+)"/);
    const viewBox = vbMatch ? vbMatch[1] : '0 0 100 100';
    const innerSvg = svgContent.replace(/<svg[^>]*>/, '').replace('</svg>', '');
    chip.innerHTML = `
      <svg viewBox="${viewBox}" width="18" height="18">${innerSvg}</svg>
      ${escapeHtml(sym.display_label)}
      <span class="chip-remove">&times;</span>
    `;
    chip.addEventListener('click', () => removeSymbol(i));
    selectedStrip.appendChild(chip);
  });
}

// ============================================================
// Suggestions
// ============================================================

function getSuggestedIds(key) {
  let suggestedIds = NEXT_WORD_MAP[key];
  if (!suggestedIds) {
    const ids = key.split('_');
    for (let len = ids.length - 1; len >= 0; len--) {
      const subKey = ids.slice(0, len).join('_');
      if (NEXT_WORD_MAP[subKey]) {
        suggestedIds = NEXT_WORD_MAP[subKey];
        break;
      }
    }
  }
  return suggestedIds || NEXT_WORD_MAP[''] || [];
}

function updateSuggestions() {
  grid.querySelectorAll('.symbol-card').forEach(card => {
    card.classList.remove('suggested');
    card.style.order = '';
  });

  const key = selectedSymbols.map(s => s.id).join('_');
  const suggestedIds = getSuggestedIds(key);
  const { ordered, highlighted } = getAffectAwareSuggestions(key, suggestedIds);

  ordered.forEach((id, index) => {
    const card = grid.querySelector(`[data-id="${id}"]`);
    if (!card) return;
    if (highlighted.has(id)) {
      card.classList.add('suggested');
    }
    if (reorderSymbolsCheckbox.checked) {
      card.style.order = -100 + index;
    }
  });
}

// ============================================================
// Prediction
// ============================================================

async function updatePrediction() {
  if (selectedSymbols.length === 0) {
    sentenceDisplay.innerHTML = '<span class="placeholder">Tap symbols below to build a sentence...</span>';
    sentenceDisplay.classList.remove('loading');
    return;
  }

  const key = selectedSymbols.map(s => s.id).join('_');
  const words = selectedSymbols.map(s => s.display_label);
  const threshold = parseInt(confidenceSlider.value, 10);

  sentenceDisplay.classList.add('loading');

  const categories = selectedSymbols.map(s => s.ui_tab);
  const hasNounOrAdj = categories.some(c => c === 'things' || c === 'feelings' || c === 'more');

  function dampenConfidence(rawConfidence) {
    let multiplier;
    if (selectedSymbols.length === 1) multiplier = 0.3;
    else if (selectedSymbols.length === 2 && !hasNounOrAdj) multiplier = 0.55;
    else if (selectedSymbols.length === 2) multiplier = 0.85;
    else if (selectedSymbols.length >= 3 && hasNounOrAdj) multiplier = 1.0;
    else multiplier = 0.75;
    return Math.round(rawConfidence * multiplier);
  }

  if (PROXY_BASE_URL) {
    try {
      const result = await predictWithAPI(words);
      const confidence = dampenConfidence(result.confidence);
      sentenceDisplay.classList.remove('loading');
      if (confidence >= threshold) {
        sentenceDisplay.innerHTML = `<span class="predicted-text">${escapeHtml(result.sentence)}</span>
          <span class="confidence-badge high">${confidence}%</span>`;
        if (autoSpeakCheckbox.checked) speakText(result.sentence);
      } else {
        const partial = words.join(' ').toLowerCase().replace(/^./, c => c.toUpperCase());
        sentenceDisplay.innerHTML = `<span class="predicted-text">${escapeHtml(partial)}...</span>
          <span class="confidence-badge low">${confidence}%</span>`;
      }
      return;
    } catch (e) {
      console.warn('API prediction failed, falling back to local:', e);
    }
  }

  const result = predictLocal(key, words);
  const confidence = dampenConfidence(result.confidence);
  sentenceDisplay.classList.remove('loading');

  if (confidence >= threshold) {
    sentenceDisplay.innerHTML = `<span class="predicted-text">${escapeHtml(result.sentence)}</span>
      <span class="confidence-badge high">${confidence}%</span>`;
    if (autoSpeakCheckbox.checked) speakText(result.sentence);
  } else {
    const partial = words.join(' ').toLowerCase().replace(/^./, c => c.toUpperCase());
    sentenceDisplay.innerHTML = `<span class="predicted-text">${escapeHtml(partial)}...</span>
      <span class="confidence-badge low">${result.confidence}%</span>`;
  }
}

function predictLocal(key, words) {
  const tabs = selectedSymbols.map(s => s.ui_tab);
  const hasSubject = tabs.some(c => c === 'people');
  const hasVerb = tabs.some(c => c === 'actions' || c === 'core');
  const hasObject = tabs.some(c => c === 'things' || c === 'feelings' || c === 'more');

  let confidence;
  if (selectedSymbols.length === 1) confidence = 25;
  else if (hasSubject && hasVerb && hasObject) confidence = 85;
  else if (hasSubject && hasVerb) confidence = 45;
  else if (hasVerb && hasObject) confidence = 65;
  else confidence = 30 + (selectedSymbols.length * 10);

  let sentence;
  if (SENTENCE_TEMPLATES[key]) {
    sentence = SENTENCE_TEMPLATES[key].replace('{0}', '');
  } else {
    const ids = key.split('_');
    let found = false;
    for (let len = ids.length; len > 0; len--) {
      const subKey = ids.slice(0, len).join('_');
      if (SENTENCE_TEMPLATES[subKey]) {
        const remaining = words.slice(len).join(' ').toLowerCase();
        sentence = SENTENCE_TEMPLATES[subKey].replace('{0}', remaining).replace(/\s+/g, ' ').trim();
        found = true;
        break;
      }
    }
    if (!found) sentence = buildSimpleSentence(words);
  }

  return { sentence, confidence };
}

function buildSimpleSentence(words) {
  if (words.length === 0) return '';
  let sentence = words.map((w, i) => i === 0 ? w : w.toLowerCase()).join(' ');
  if (!/[.!?]$/.test(sentence)) sentence += '.';
  return sentence;
}

// ============================================================
// Affect → prediction modulation
// ============================================================

function buildAffectSystemPrompt(state) {
  if (state.valence < 0.35) {
    return `The user appears anxious or highly stressed (HRV signal low). Prioritize short, simple, calming phrases. Avoid complex constructions. Prefer: needs, requests for comfort, simple statements.`;
  } else if (state.valence < 0.55) {
    return `The user shows mild stress. Prefer clear, direct sentences.`;
  } else if (state.valence < 0.75) {
    return `The user appears calm and regulated. Suggest natural, expressive sentences.`;
  } else {
    return `The user is very calm and engaged. Support rich, expressive communication.`;
  }
}

function applyAffectToRequest(state) {
  if (state.confidence < 0.3) return { systemPrompt: '', temperature: 0.3 };
  return { systemPrompt: buildAffectSystemPrompt(state), temperature: 0.3 };
}

async function predictWithAPI(words) {
  if (pendingRequest) pendingRequest.abort();
  const controller = new AbortController();
  pendingRequest = controller;

  const prompt = `You are a grammar engine for an AAC (Augmentative and Alternative Communication) device used by minimally verbal children with autism.

The child has tapped these symbol words in order: ${words.join(', ')}

YOUR ONLY JOB: Convert these symbols into the most natural, grammatically correct English sentence. You may ONLY:
- Add grammar/function words: articles (a, the), prepositions (to, in, at), helper verbs (need to, want to, am, is), pronouns, conjunctions
- Adjust verb tense or form (e.g. "go" → "going", "feel" → "feeling")
- Reorder slightly for natural grammar

You must NEVER:
- Add any content words (nouns, verbs, adjectives, adverbs) the child did not tap
- Add reasons, explanations, or elaborations (e.g. NEVER add "because...", "so that...", etc.)
- Guess what the child might mean beyond their symbols
- Add emotional context or motivation

CRITICAL RULE — "You" means a request TO another person:
When "You" is the first symbol, the child is addressing a caregiver or helper. Treat it as a request or instruction directed AT that person, NOT a statement about what "you" want to do.
- WRONG: "You want to give water." / "You go home."
- RIGHT: "Can you give me water?" / "Can you help me?" / "Give me water."

Examples:
- Symbols: "I, Go, Bathroom" → "I need to go to the bathroom."
- Symbols: "I, Feel, Sad" → "I feel sad."
- Symbols: "I, Want" → "I want..."
- Symbols: "Want, Water" → "I want water."
- Symbols: "He/She, Eat, Food" → "He wants to eat food."
- Symbols: "You, Give, Water" → "Can you give me water?"
- Symbols: "You, Help" → "Can you help me?"
- Symbols: "You, Stop" → "Please stop."

Also rate your confidence (0-100) that the symbols form a COMPLETE thought:
- Incomplete (missing object/subject): 20-50%
- Complete thought: 75-95%

Respond with ONLY a JSON object, no markdown:
{"sentence": "the sentence", "confidence": 75}`;

  const affect = applyAffectToRequest(liefState);
  const messages = [];
  if (affect.systemPrompt) messages.push({ role: 'system', content: affect.systemPrompt });
  messages.push({ role: 'user', content: prompt });

  // NOTE(mjp): replace with local SLM in later phases
  const response = await fetch(`${PROXY_BASE_URL}/v1/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages,
      max_tokens: 80,
      temperature: affect.temperature
    }),
    signal: controller.signal
  });

  if (!response.ok) throw new Error(`API error: ${response.status}`);
  const data = await response.json();
  pendingRequest = null;
  const raw = data.choices[0].message.content.trim();
  try {
    const parsed = JSON.parse(raw);
    return { sentence: parsed.sentence, confidence: parseInt(parsed.confidence, 10) || 50 };
  } catch (e) {
    // If JSON parsing fails, treat as a raw sentence with medium confidence
    return { sentence: raw.replace(/^["']|["']$/g, ''), confidence: 50 };
  }
}

// ============================================================
// Text to Speech (unchanged)
// ============================================================

let currentAudio = null;
let isSpeaking = false;

const SPEAK_SVG = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
  <path d="M11 5L6 9H2v6h4l5 4V5z"/>
  <path d="M19.07 4.93a10 10 0 010 14.14M15.54 8.46a5 5 0 010 7.08" stroke-linecap="round"/>
</svg>`;

const STOP_SVG = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
  <rect x="5" y="5" width="14" height="14" rx="2"/>
</svg>`;

function updateSpeakButtonState(speaking) {
  isSpeaking = speaking;
  btnSpeak.classList.toggle('speaking', speaking);
  btnSpeak.title = speaking ? 'Stop speaking' : 'Speak sentence';
  btnSpeak.innerHTML = speaking ? STOP_SVG : SPEAK_SVG;
}

function speakSentence() {
  if (isSpeaking) { stopSpeaking(); return; }
  const predictedEl = sentenceDisplay.querySelector('.predicted-text');
  const text = predictedEl ? predictedEl.textContent.trim() : '';
  if (text) speakText(text);
}

async function speakText(text) {
  stopSpeaking();
  updateSpeakButtonState(true);
  if (PROXY_BASE_URL) {
    try { await speakWithOpenAI(text); return; }
    catch (e) { console.warn('OpenAI TTS failed, falling back to browser:', e); }
  }
  speakWithBrowser(text);
}

async function speakWithOpenAI(text) {
  const response = await fetch(`${PROXY_BASE_URL}/v1/audio/speech`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'tts-1', input: text, voice: 'nova', speed: 0.9 })
  });
  if (!response.ok) throw new Error(`TTS API error: ${response.status}`);
  const audioBlob = await response.blob();
  const audioUrl = URL.createObjectURL(audioBlob);
  currentAudio = new Audio(audioUrl);
  currentAudio.addEventListener('ended', () => { URL.revokeObjectURL(audioUrl); currentAudio = null; updateSpeakButtonState(false); });
  currentAudio.addEventListener('error', () => { URL.revokeObjectURL(audioUrl); currentAudio = null; updateSpeakButtonState(false); });
  await currentAudio.play();
}

function speakWithBrowser(text) {
  if (!('speechSynthesis' in window)) { updateSpeakButtonState(false); return; }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.85;
  utterance.pitch = 1.1;
  utterance.addEventListener('end', () => updateSpeakButtonState(false));
  utterance.addEventListener('error', () => updateSpeakButtonState(false));
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v => v.name.includes('Samantha') || v.name.includes('Alex') || v.name.includes('Karen'));
  if (preferred) utterance.voice = preferred;
  window.speechSynthesis.speak(utterance);
}

function stopSpeaking() {
  if (currentAudio) { currentAudio.pause(); currentAudio = null; }
  window.speechSynthesis?.cancel();
  updateSpeakButtonState(false);
}

if ('speechSynthesis' in window) {
  window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

// ============================================================
// ============================================================
// View state machine
// ============================================================

const STORAGE_KEY = 'liefaac.view';

function loadInitialView() {
  const params = new URLSearchParams(window.location.search);
  // ?view=meaning_room or ?view=grid_tabs overrides localStorage (useful for debugging)
  if (params.has('view')) return params.get('view');
  return localStorage.getItem(STORAGE_KEY)
    || APP_CONFIG.default_view
    || 'meaning_room';
}

function setView(view, anchor) {
  currentView = view;
  if (anchor !== undefined) currentAnchor = anchor;

  meaningRoomView.classList.add('hidden');
  anchorGridView.classList.add('hidden');
  gridTabsView.classList.add('hidden');

  if (view === 'meaning_room') {
    meaningRoomView.classList.remove('hidden');
    renderMeaningRoom();
  } else if (view === 'anchor_grid' && currentAnchor) {
    anchorGridView.classList.remove('hidden');
    renderAnchorGrid(currentAnchor);
  } else if (view === 'grid_tabs') {
    gridTabsView.classList.remove('hidden');
    renderTabs();
    renderGrid();
  }

  renderViewToggleButton();
  // Persist top-level view (anchor_grid is a sub-state of meaning_room)
  localStorage.setItem(STORAGE_KEY, view === 'anchor_grid' ? 'meaning_room' : view);
}

const GRID_ICON_SVG = `<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
  <rect x="0" y="0" width="7" height="7" rx="1.5"/>
  <rect x="9" y="0" width="7" height="7" rx="1.5"/>
  <rect x="0" y="9" width="7" height="7" rx="1.5"/>
  <rect x="9" y="9" width="7" height="7" rx="1.5"/>
</svg>`;

const ROOM_ICON_SVG = `<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M2 8.5L8 3l6 5.5"/>
  <path d="M3.5 7.5V13h9V7.5"/>
</svg>`;

function renderViewToggleButton() {
  if (APP_CONFIG.show_view_toggle === false) {
    btnViewToggle.classList.add('hidden');
    return;
  }
  btnViewToggle.classList.remove('hidden');
  const isRoom = currentView === 'meaning_room' || currentView === 'anchor_grid';
  btnViewToggle.innerHTML = isRoom
    ? `${GRID_ICON_SVG} <span>Grid</span>`
    : `${ROOM_ICON_SVG} <span>Room</span>`;
  btnViewToggle.title = isRoom ? 'Switch to Grid view' : 'Switch to Room view';
}

// ============================================================
// Meaning Room rendering
// ============================================================

function renderMeaningRoom() {
  if (!ROOM_CONFIG) return;
  meaningRoomStage.innerHTML = '';

  // Compute stage size to fit within the view while preserving the image aspect ratio.
  // Reading clientWidth/clientHeight triggers a synchronous layout, giving accurate dims.
  const [imgW, imgH] = ROOM_CONFIG.image_natural_size;
  const ratio = imgW / imgH;
  const viewW = meaningRoomView.clientWidth;
  const viewH = meaningRoomView.clientHeight;


  let stageW, stageH;
  if (viewH > 0 && viewW / viewH > ratio) {
    // View is wider than the image ratio — constrain by height
    stageH = viewH;
    stageW = stageH * ratio;
  } else {
    // View is taller — constrain by width
    stageW = viewW || imgW;
    stageH = stageW / ratio;
  }

  meaningRoomStage.style.width  = `${Math.floor(stageW)}px`;
  meaningRoomStage.style.height = `${Math.floor(stageH)}px`;
  meaningRoomStage.style.aspectRatio = ''; // clear CSS hint; JS drives size now

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
    btn.style.left   = `${h.x * 100}%`;
    btn.style.top    = `${h.y * 100}%`;
    btn.style.width  = `${h.w * 100}%`;
    btn.style.height = `${h.h * 100}%`;
    applyHotspotGlow(btn, anchor, stressZone);

    if (anchor.icon) {
      const iconEl = document.createElement('span');
      iconEl.className = 'mr-hotspot-icon';
      iconEl.textContent = anchor.icon;
      btn.appendChild(iconEl);
    }

    const labelEl = document.createElement('span');
    labelEl.className = 'mr-hotspot-label';
    labelEl.textContent = anchor.label;
    btn.appendChild(labelEl);

    btn.addEventListener('click', () => setView('anchor_grid', anchor));
    meaningRoomStage.appendChild(btn);
  });
}

function effectiveGlow(anchor, stressZone) {
  const curve = anchor.stress_glow_curve || ROOM_CONFIG.stress_glow_curve_default;
  const idx = Math.max(0, Math.min(4, stressZone - 1));
  return curve[idx] ?? ROOM_CONFIG.default_glow_intensity;
}

function applyHotspotGlow(btn, anchor, stressZone) {
  btn.style.setProperty('--glow', effectiveGlow(anchor, stressZone).toFixed(2));
  // Only stress-sensitive anchors (those with a custom curve) pulse at zones 4-5
  const isStressSensitive = Array.isArray(anchor.stress_glow_curve);
  const isPulsing = isStressSensitive && stressZone >= 4;
  btn.classList.toggle('stress-pulse', isPulsing);
  if (isPulsing) {
    // Zone 5 = fast urgent pulse; zone 4 = slower warning pulse
    btn.style.setProperty('--pulse-dur', stressZone >= 5 ? '1.1s' : '1.8s');
  }
}

function updateMeaningRoomGlow() {
  if (currentView !== 'meaning_room') return;
  const stressZone = parseInt(mockValenceSlider.value, 10);
  meaningRoomStage.querySelectorAll('.mr-hotspot').forEach(btn => {
    const anchor = ROOM_CONFIG.anchors.find(a => a.id === btn.dataset.anchorId);
    if (anchor) applyHotspotGlow(btn, anchor, stressZone);
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
    card.dataset.id  = sym.id;
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

// ============================================================
// Clear
// ============================================================

function clearAll() {
  selectedSymbols = [];
  renderSelectedStrip();
  sentenceDisplay.innerHTML = '<span class="placeholder">Tap symbols below to build a sentence...</span>';
  sentenceDisplay.classList.remove('loading');
  updateSuggestions();
  stopSpeaking();
}

// ============================================================
// Utility
// ============================================================

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function escapeAttr(text) {
  return text.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ============================================================
// Event listeners
// ============================================================

function setupEventListeners() {
  btnSpeak.addEventListener('click', speakSentence);
  btnClear.addEventListener('click', clearAll);

  const fitzModal = document.getElementById('fitzgeraldModal');
  const closeFitz = () => fitzModal.classList.add('hidden');
  document.getElementById('btnColorKey').addEventListener('click', () => fitzModal.classList.remove('hidden'));
  document.getElementById('btnFitzClose').addEventListener('click', closeFitz);
  fitzModal.addEventListener('click', e => { if (e.target === fitzModal) closeFitz(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeFitz(); });

  showSuggestionsCheckbox.addEventListener('change', () => updateSuggestions());
  reorderSymbolsCheckbox.addEventListener('change', () => {
    if (!reorderSymbolsCheckbox.checked) {
      grid.querySelectorAll('.symbol-card').forEach(card => { card.style.order = ''; });
    }
    updateSuggestions();
  });

  document.getElementById('sortByFrequency').addEventListener('change', () => renderGrid());

  document.getElementById('showAnchorLabels').addEventListener('change', e => {
    document.body.classList.toggle('show-anchor-labels', e.target.checked);
  });

  confidenceSlider.addEventListener('input', () => {
    confidenceValueLabel.textContent = `${confidenceSlider.value}%`;
  });

  mockValenceSlider.addEventListener('input', () => {
    const zoneIndex = parseInt(mockValenceSlider.value, 10);
    const zone = getStressZone(zoneIndex);
    liefState.valence = zone.valence;
    liefState.quintile = zoneIndex;
    liefState.confidence = 0.6;
    liefState.lastUpdated = Date.now();
    mockValenceLabel.textContent = `Zone ${zone.zone} — ${zone.label} ${zone.emoji}`;
    renderAffectWidget();
    renderQuickPhrases();
    updateSuggestions();
    updateMeaningRoomGlow();
  });

  liefConnectBtn.addEventListener('click', () => {
    showToast(
      'Live Lief device connection coming soon. Use the simulated affect slider below to explore affect-aware predictions.',
    );
  });

  quickPhraseBar.addEventListener('scroll', updateQPArrows);
  qpArrowLeft.addEventListener('click', () => {
    quickPhraseBar.scrollBy({ left: -220, behavior: 'smooth' });
  });
  qpArrowRight.addEventListener('click', () => {
    quickPhraseBar.scrollBy({ left: 220, behavior: 'smooth' });
  });

  btnBreak.addEventListener('click', showBreakModal);
  btnBreakResume.addEventListener('click', hideBreakModal);
  btnStartBreathe.addEventListener('click', startBreathingExercise);
  btnStopBreathe.addEventListener('click', hideBreakModal);

  btnViewToggle.addEventListener('click', () => {
    const isRoom = currentView === 'meaning_room' || currentView === 'anchor_grid';
    setView(isRoom ? 'grid_tabs' : 'meaning_room');
  });

  anchorBackBtn.addEventListener('click', () => setView('meaning_room'));

  // Re-fit the meaning room stage whenever the view is resized (orientation, window resize)
  if (window.ResizeObserver) {
    new ResizeObserver(() => {
      if (currentView === 'meaning_room') renderMeaningRoom();
    }).observe(meaningRoomView);
  }
}

// ============================================================
// Init
// ============================================================

async function init() {
  if (new URLSearchParams(window.location.search).has('debug')) {
    document.body.classList.add('debug-hotspots');
  }
  await loadVocabulary();
  await loadRoomConfig();
  setupEventListeners();
  renderAffectWidget();
  renderQuickPhrases();
  setView(loadInitialView());
}

init().catch(err => {
  console.error('LiefAAC failed to initialize:', err);
  document.getElementById('sentenceDisplay').innerHTML =
    `<span style="color:#ef4444;font-size:14px;">⚠️ Failed to load: ${err.message}. Open via HTTP server, not file://</span>`;
});
