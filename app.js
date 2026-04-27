// ============================================================
// LiefAAC - AI-Powered AAC Prototype
// ============================================================

// --- Symbol Definitions with inline SVG ---
const SYMBOLS = [
  // PRONOUNS (yellow left border)
  {
    id: 'i', word: 'I', category: 'pronoun',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="14" r="8" fill="#f59e0b"/><path d="M15 50 V32 a10 10 0 0 1 20 0 V50" fill="#f59e0b"/><circle cx="25" cy="14" r="5" fill="#fff3cd"/><circle cx="23" cy="13" r="1.2" fill="#333"/><circle cx="27" cy="13" r="1.2" fill="#333"/><path d="M23 17 Q25 19 27 17" stroke="#333" fill="none" stroke-width="1.2"/><line x1="25" y1="28" x2="25" y2="22" stroke="#333" stroke-width="1" stroke-dasharray="2"/></svg>`
  },
  {
    id: 'you', word: 'You', category: 'pronoun',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="16" r="8" fill="#fbbf24"/><circle cx="25" cy="16" r="5" fill="#fef3c7"/><circle cx="23" cy="15" r="1.2" fill="#333"/><circle cx="27" cy="15" r="1.2" fill="#333"/><path d="M23 19 Q25 21 27 19" stroke="#333" fill="none" stroke-width="1.2"/><path d="M15 50 V34 a10 10 0 0 1 20 0 V50" fill="#fbbf24"/><path d="M10 30 L22 24" stroke="#f59e0b" stroke-width="3" stroke-linecap="round"/><circle cx="8" cy="31" r="3" fill="#f59e0b"/></svg>`
  },
  {
    id: 'he_she', word: 'He/She', category: 'pronoun',
    svg: `<svg viewBox="0 0 50 50"><circle cx="18" cy="16" r="7" fill="#60a5fa"/><circle cx="18" cy="16" r="4.5" fill="#dbeafe"/><circle cx="16.5" cy="15" r="1" fill="#333"/><circle cx="19.5" cy="15" r="1" fill="#333"/><circle cx="34" cy="16" r="7" fill="#f472b6"/><circle cx="34" cy="16" r="4.5" fill="#fce7f3"/><circle cx="32.5" cy="15" r="1" fill="#333"/><circle cx="35.5" cy="15" r="1" fill="#333"/><path d="M10 50 V34 a8 8 0 0 1 16 0 V50" fill="#60a5fa"/><path d="M26 50 V34 a8 8 0 0 1 16 0 V50" fill="#f472b6"/></svg>`
  },
  {
    id: 'we', word: 'We', category: 'pronoun',
    svg: `<svg viewBox="0 0 50 50"><circle cx="16" cy="14" r="6" fill="#f59e0b"/><circle cx="16" cy="14" r="4" fill="#fff3cd"/><circle cx="34" cy="14" r="6" fill="#fbbf24"/><circle cx="34" cy="14" r="4" fill="#fef3c7"/><circle cx="25" cy="18" r="7" fill="#f97316"/><circle cx="25" cy="18" r="4.5" fill="#ffedd5"/><circle cx="23.5" cy="17" r="1" fill="#333"/><circle cx="26.5" cy="17" r="1" fill="#333"/><path d="M12 50 V32 a13 13 0 0 1 26 0 V50" fill="#f97316"/></svg>`
  },

  // VERBS (green left border)
  {
    id: 'want', word: 'Want', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><path d="M25 8 L30 20 L43 20 L32 28 L36 42 L25 34 L14 42 L18 28 L7 20 L20 20 Z" fill="#10b981" stroke="#059669" stroke-width="1.5"/><circle cx="25" cy="25" r="4" fill="#fff" opacity="0.5"/></svg>`
  },
  {
    id: 'need', word: 'Need', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="22" r="14" fill="none" stroke="#10b981" stroke-width="3"/><text x="25" y="28" text-anchor="middle" font-size="20" font-weight="bold" fill="#10b981">!</text><path d="M20 40 L25 46 L30 40" fill="#10b981"/></svg>`
  },
  {
    id: 'go', word: 'Go', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><path d="M10 25 L35 25" stroke="#10b981" stroke-width="4" stroke-linecap="round"/><path d="M28 16 L40 25 L28 34" fill="#10b981"/><circle cx="15" cy="38" r="3" fill="#86efac"/><circle cx="22" cy="42" r="2.5" fill="#86efac"/><circle cx="9" cy="41" r="2" fill="#86efac"/></svg>`
  },
  {
    id: 'stop', word: 'Stop', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><polygon points="25,4 43,14 43,34 25,44 7,34 7,14" fill="#ef4444" stroke="#dc2626" stroke-width="1.5"/><rect x="18" y="20" width="14" height="8" rx="2" fill="white"/></svg>`
  },
  {
    id: 'help', word: 'Help', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><path d="M18 38 L12 22 Q10 16 16 14 L25 10 L34 14 Q40 16 38 22 L32 38" fill="#10b981"/><path d="M18 38 Q25 44 32 38" fill="#059669"/><rect x="22" y="18" width="6" height="10" rx="3" fill="white"/><rect x="23" y="30" width="4" height="4" rx="2" fill="white"/></svg>`
  },
  {
    id: 'eat', word: 'Eat', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><ellipse cx="25" cy="32" rx="16" ry="10" fill="#fbbf24"/><ellipse cx="25" cy="30" rx="16" ry="10" fill="#fcd34d"/><circle cx="20" cy="28" r="3" fill="#ef4444"/><circle cx="30" cy="26" r="4" fill="#a3e635"/><circle cx="24" cy="32" r="2.5" fill="#fb923c"/><path d="M25 6 L25 18" stroke="#9ca3af" stroke-width="2"/><circle cx="22" cy="10" r="3" fill="none" stroke="#9ca3af" stroke-width="1.5"/><circle cx="28" cy="7" r="3" fill="none" stroke="#9ca3af" stroke-width="1.5"/></svg>`
  },
  {
    id: 'drink', word: 'Drink', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><path d="M15 10 L18 42 Q18 46 22 46 L28 46 Q32 46 32 42 L35 10 Z" fill="#60a5fa" stroke="#3b82f6" stroke-width="1.5"/><path d="M16 18 L34 18 L32 42 Q32 46 28 46 L22 46 Q18 46 18 42 Z" fill="#93c5fd" opacity="0.6"/><ellipse cx="25" cy="10" rx="10" ry="2" fill="#3b82f6"/></svg>`
  },
  {
    id: 'play', word: 'Play', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="16" fill="#a78bfa" stroke="#8b5cf6" stroke-width="2"/><polygon points="20,15 38,25 20,35" fill="white"/></svg>`
  },
  {
    id: 'like', word: 'Like', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><path d="M25 42 C15 34 5 26 5 18 A10 10 0 0 1 25 14 A10 10 0 0 1 45 18 C45 26 35 34 25 42Z" fill="#f472b6" stroke="#ec4899" stroke-width="1.5"/></svg>`
  },
  {
    id: 'walk', word: 'Walk', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="8" r="5" fill="#10b981"/><line x1="25" y1="13" x2="25" y2="30" stroke="#10b981" stroke-width="3" stroke-linecap="round"/><line x1="25" y1="20" x2="16" y2="26" stroke="#10b981" stroke-width="2.5" stroke-linecap="round"/><line x1="25" y1="20" x2="34" y2="24" stroke="#10b981" stroke-width="2.5" stroke-linecap="round"/><line x1="25" y1="30" x2="17" y2="44" stroke="#10b981" stroke-width="2.5" stroke-linecap="round"/><line x1="25" y1="30" x2="34" y2="42" stroke="#10b981" stroke-width="2.5" stroke-linecap="round"/></svg>`
  },
  {
    id: 'look', word: 'Look', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><ellipse cx="25" cy="25" rx="18" ry="12" fill="white" stroke="#10b981" stroke-width="2.5"/><circle cx="25" cy="25" r="7" fill="#10b981"/><circle cx="25" cy="25" r="3.5" fill="#064e3b"/><circle cx="27" cy="23" r="1.5" fill="white"/></svg>`
  },
  {
    id: 'give', word: 'Give', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><path d="M8 28 Q8 20 16 20 L26 20" stroke="#10b981" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M26 14 L26 26" stroke="#10b981" stroke-width="3" stroke-linecap="round"/><path d="M20 20 L26 14 L32 20" stroke="#10b981" stroke-width="2.5" fill="none" stroke-linecap="round"/><rect x="28" y="16" width="16" height="12" rx="3" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/><path d="M36 16 V28 M28 22 H44" stroke="#f59e0b" stroke-width="1.5"/></svg>`
  },
  {
    id: 'feel', word: 'Feel', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="16" fill="#fbbf24" stroke="#f59e0b" stroke-width="2"/><circle cx="19" cy="22" r="2" fill="#333"/><circle cx="31" cy="22" r="2" fill="#333"/><path d="M18 31 Q25 38 32 31" stroke="#333" fill="none" stroke-width="2" stroke-linecap="round"/></svg>`
  },
  {
    id: 'sleep', word: 'Sleep', category: 'verb',
    svg: `<svg viewBox="0 0 50 50"><circle cx="22" cy="28" r="10" fill="#818cf8"/><circle cx="22" cy="28" r="7" fill="#c7d2fe"/><path d="M17 27 Q22 24 27 27" stroke="#333" stroke-width="1.5" fill="none"/><path d="M19 31 Q22 33 25 31" stroke="#333" fill="none" stroke-width="1"/><text x="34" y="18" font-size="10" font-weight="bold" fill="#818cf8">Z</text><text x="38" y="12" font-size="8" font-weight="bold" fill="#a5b4fc">Z</text><text x="42" y="8" font-size="6" font-weight="bold" fill="#c7d2fe">Z</text></svg>`
  },

  // NOUNS (blue left border)
  {
    id: 'bathroom', word: 'Bathroom', category: 'noun',
    svg: `<svg viewBox="0 0 50 50"><rect x="14" y="8" width="22" height="28" rx="4" fill="#60a5fa" stroke="#3b82f6" stroke-width="1.5"/><rect x="18" y="12" width="14" height="8" rx="2" fill="white" opacity="0.5"/><ellipse cx="25" cy="28" rx="6" ry="4" fill="white" opacity="0.4"/><circle cx="25" cy="4" r="2" fill="#93c5fd"/><rect x="20" y="38" width="10" height="6" rx="2" fill="#3b82f6"/></svg>`
  },
  {
    id: 'home', word: 'Home', category: 'noun',
    svg: `<svg viewBox="0 0 50 50"><path d="M25 6 L5 24 L10 24 L10 44 L40 44 L40 24 L45 24 Z" fill="#3b82f6" stroke="#2563eb" stroke-width="1.5"/><rect x="20" y="28" width="10" height="16" rx="1" fill="#fbbf24"/><circle cx="28" cy="36" r="1.2" fill="#92400e"/><rect x="14" y="18" width="8" height="6" rx="1" fill="#bfdbfe"/><rect x="28" y="18" width="8" height="6" rx="1" fill="#bfdbfe"/></svg>`
  },
  {
    id: 'school', word: 'School', category: 'noun',
    svg: `<svg viewBox="0 0 50 50"><rect x="8" y="20" width="34" height="24" rx="2" fill="#f59e0b" stroke="#d97706" stroke-width="1.5"/><path d="M25 6 L8 20 L42 20 Z" fill="#fbbf24" stroke="#d97706" stroke-width="1.5"/><rect x="21" y="30" width="8" height="14" rx="1" fill="#92400e"/><rect x="12" y="26" width="6" height="5" rx="1" fill="#bfdbfe"/><rect x="32" y="26" width="6" height="5" rx="1" fill="#bfdbfe"/><rect x="23" y="10" width="4" height="8" fill="#d97706"/><circle cx="25" cy="9" r="2.5" fill="#ef4444"/></svg>`
  },
  {
    id: 'food', word: 'Food', category: 'noun',
    svg: `<svg viewBox="0 0 50 50"><ellipse cx="25" cy="36" rx="18" ry="8" fill="#e5e7eb"/><ellipse cx="25" cy="34" rx="18" ry="8" fill="#f3f4f6"/><circle cx="18" cy="24" r="5" fill="#ef4444"/><path d="M16 24 Q18 20 20 24" fill="#22c55e"/><circle cx="32" cy="22" r="6" fill="#fbbf24"/><path d="M29 18 Q32 10 35 18" fill="#a16207" stroke-width="0"/><circle cx="25" cy="28" r="4" fill="#fb923c"/></svg>`
  },
  {
    id: 'water', word: 'Water', category: 'noun',
    svg: `<svg viewBox="0 0 50 50"><path d="M25 6 Q35 22 35 30 A10 10 0 0 1 15 30 Q15 22 25 6Z" fill="#60a5fa" stroke="#3b82f6" stroke-width="1.5"/><path d="M20 28 Q22 24 24 28 Q26 32 28 28" stroke="white" stroke-width="1.5" fill="none" opacity="0.6"/></svg>`
  },
  {
    id: 'mom', word: 'Mom', category: 'noun',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="14" r="8" fill="#f472b6"/><circle cx="25" cy="14" r="5.5" fill="#fce7f3"/><path d="M17 10 Q20 4 25 6 Q30 4 33 10" fill="#7c2d12" stroke="none"/><circle cx="23" cy="13" r="1.2" fill="#333"/><circle cx="27" cy="13" r="1.2" fill="#333"/><path d="M23 17 Q25 19 27 17" stroke="#333" fill="none" stroke-width="1.2"/><path d="M14 50 V32 a11 11 0 0 1 22 0 V50" fill="#f472b6"/><path d="M25 25 L25 28" stroke="#f9a8d4" stroke-width="3"/></svg>`
  },
  {
    id: 'dad', word: 'Dad', category: 'noun',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="14" r="8" fill="#3b82f6"/><circle cx="25" cy="14" r="5.5" fill="#dbeafe"/><rect x="17" y="8" width="16" height="4" rx="2" fill="#1e3a5f"/><circle cx="23" cy="13" r="1.2" fill="#333"/><circle cx="27" cy="13" r="1.2" fill="#333"/><path d="M23 17 Q25 19 27 17" stroke="#333" fill="none" stroke-width="1.2"/><path d="M14 50 V32 a11 11 0 0 1 22 0 V50" fill="#3b82f6"/></svg>`
  },
  {
    id: 'toy', word: 'Toy', category: 'noun',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="20" r="10" fill="#a78bfa" stroke="#8b5cf6" stroke-width="1.5"/><circle cx="22" cy="18" r="1.5" fill="#333"/><circle cx="28" cy="18" r="1.5" fill="#333"/><path d="M22 23 Q25 26 28 23" stroke="#333" fill="none" stroke-width="1.2"/><circle cx="25" cy="10" r="2.5" fill="#ec4899"/><rect x="22" y="30" width="6" height="10" rx="3" fill="#8b5cf6"/><circle cx="18" cy="35" r="3" fill="#c084fc"/><circle cx="32" cy="35" r="3" fill="#c084fc"/></svg>`
  },
  {
    id: 'book', word: 'Book', category: 'noun',
    svg: `<svg viewBox="0 0 50 50"><rect x="10" y="10" width="28" height="32" rx="2" fill="#3b82f6" stroke="#2563eb" stroke-width="1.5"/><rect x="13" y="10" width="25" height="32" rx="2" fill="#60a5fa"/><rect x="16" y="14" width="18" height="3" rx="1" fill="white" opacity="0.7"/><rect x="16" y="20" width="14" height="2" rx="1" fill="white" opacity="0.4"/><rect x="16" y="25" width="16" height="2" rx="1" fill="white" opacity="0.4"/><rect x="16" y="30" width="10" height="2" rx="1" fill="white" opacity="0.4"/><line x1="13" y1="10" x2="13" y2="42" stroke="#2563eb" stroke-width="2"/></svg>`
  },

  // ADJECTIVES / RESPONSES (purple left border)
  {
    id: 'happy', word: 'Happy', category: 'adjective',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="18" fill="#fbbf24" stroke="#f59e0b" stroke-width="2"/><circle cx="18" cy="21" r="2.5" fill="#333"/><circle cx="32" cy="21" r="2.5" fill="#333"/><path d="M16 30 Q25 40 34 30" stroke="#333" fill="none" stroke-width="2.5" stroke-linecap="round"/></svg>`
  },
  {
    id: 'sad', word: 'Sad', category: 'adjective',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="18" fill="#60a5fa" stroke="#3b82f6" stroke-width="2"/><circle cx="18" cy="21" r="2.5" fill="#333"/><circle cx="32" cy="21" r="2.5" fill="#333"/><path d="M16 35 Q25 27 34 35" stroke="#333" fill="none" stroke-width="2.5" stroke-linecap="round"/><path d="M18 24 L15 28" stroke="#93c5fd" stroke-width="1.5" stroke-linecap="round"/></svg>`
  },
  {
    id: 'more', word: 'More', category: 'adjective',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="16" fill="#8b5cf6" stroke="#7c3aed" stroke-width="2"/><line x1="25" y1="16" x2="25" y2="34" stroke="white" stroke-width="4" stroke-linecap="round"/><line x1="16" y1="25" x2="34" y2="25" stroke="white" stroke-width="4" stroke-linecap="round"/></svg>`
  },

  // SOCIAL (pink left border)
  {
    id: 'yes', word: 'Yes', category: 'social',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="18" fill="#22c55e" stroke="#16a34a" stroke-width="2"/><path d="M15 25 L22 33 L36 18" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`
  },
  {
    id: 'no', word: 'No', category: 'social',
    svg: `<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="18" fill="#ef4444" stroke="#dc2626" stroke-width="2"/><line x1="16" y1="16" x2="34" y2="34" stroke="white" stroke-width="4" stroke-linecap="round"/><line x1="34" y1="16" x2="16" y2="34" stroke="white" stroke-width="4" stroke-linecap="round"/></svg>`
  },
  {
    id: 'please', word: 'Please', category: 'social',
    svg: `<svg viewBox="0 0 50 50"><path d="M25 6 C15 6 8 14 8 22 C8 34 25 46 25 46 C25 46 42 34 42 22 C42 14 35 6 25 6Z" fill="#ec4899" stroke="#db2777" stroke-width="1.5"/><path d="M18 22 Q25 16 32 22 Q25 30 18 22Z" fill="white" opacity="0.4"/></svg>`
  },
  {
    id: 'thank_you', word: 'Thank You', category: 'social',
    svg: `<svg viewBox="0 0 50 50"><path d="M10 30 L10 18 Q10 12 16 12 L20 12" stroke="#ec4899" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M20 8 L20 22 L28 22 L28 8" stroke="#ec4899" stroke-width="2.5" fill="none" stroke-linecap="round"/><path d="M28 12 L34 12 Q40 12 40 18 L40 30" stroke="#ec4899" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M8 34 Q25 46 42 34" stroke="#ec4899" stroke-width="2.5" fill="none" stroke-linecap="round"/><circle cx="25" cy="40" r="3" fill="#f9a8d4"/></svg>`
  },
];

// --- Sentence Prediction Engine (rule-based fallback) ---
const SENTENCE_TEMPLATES = {
  'i_want': 'I want {0}',
  'i_need': 'I need {0}',
  'i_want_go': 'I want to go {0}',
  'i_go': 'I want to go {0}',
  'i_want_eat': 'I want to eat something',
  'i_want_drink': 'I want something to drink',
  'i_want_play': 'I want to play',
  'i_eat': 'I want to eat',
  'i_drink': 'I want to drink something',
  'i_play': 'I want to play',
  'i_feel_happy': 'I am feeling happy',
  'i_feel_sad': 'I am feeling sad',
  'i_feel': 'I am feeling {0}',
  'i_like': 'I like {0}',
  'i_need_help': 'I need help',
  'i_need_bathroom': 'I need to use the bathroom',
  'i_need_water': 'I need water, please',
  'i_walk': 'I want to walk',
  'i_walk_home': 'I want to walk home',
  'i_walk_school': 'I want to walk to school',
  'i_walk_bathroom': 'I want to walk to the bathroom',
  'i_go_home': 'I want to go home',
  'i_go_school': 'I want to go to school',
  'i_go_bathroom': 'I need to go to the bathroom',
  'i_look_book': 'I want to look at a book',
  'i_sleep': 'I want to go to sleep',
  'i_look': 'I want to look at something',
  'i_stop': 'I want to stop',
  'i_happy': 'I am happy',
  'i_sad': 'I am sad',
  'you_help': 'Can you help me?',
  'you_give': 'Can you give me {0}?',
  'you_look': 'Can you look at this?',
  'you_stop': 'Can you please stop?',
  'you_play': 'Do you want to play?',
  'help': 'I need help!',
  'stop': 'Please stop!',
  'more': 'I want more, please',
  'more_food': 'I want more food, please',
  'more_water': 'I want more water, please',
  'i_more': 'I want more',
  'i_more_food': 'I want more food, please',
  'i_more_water': 'I want more water, please',
  'please_help': 'Please help me!',
  'want_food': 'I want food',
  'want_water': 'I want water',
  'want_go_home': 'I want to go home',
  'want_play': 'I want to play',
  'want_mom': 'I want Mom',
  'want_dad': 'I want Dad',
  'i_want_mom': 'I want my Mom',
  'i_want_dad': 'I want my Dad',
  'i_like_play': 'I like to play',
  'i_like_book': 'I like this book',
  'i_like_food': 'I like the food',
  'i_like_school': 'I like school',
  'give_water': 'Can you give me water?',
  'give_food': 'Can you give me food?',
  'give_book': 'Can you give me the book?',
  'give_toy': 'Can you give me the toy?',
  'he_she_happy': 'He is happy',
  'he_she_sad': 'She is sad',
  'we_go_home': 'We want to go home',
  'we_play': 'We want to play',
  'we_eat': 'We want to eat',
  'yes_please': 'Yes, please!',
  'no_stop': 'No, stop!',
  'no_thank_you': 'No, thank you',
  'yes_more': 'Yes, more please!',
  'thank_you': 'Thank you!',
  'please': 'Please',
  'yes': 'Yes!',
  'no': 'No',
};

// Next-word suggestions based on current sequence
const NEXT_WORD_MAP = {
  '': ['i', 'you', 'want', 'need', 'help', 'more', 'yes', 'no', 'please', 'stop'],
  'i': ['want', 'need', 'feel', 'like', 'go', 'eat', 'drink', 'play', 'walk', 'look', 'sleep', 'happy', 'sad', 'stop'],
  'you': ['help', 'give', 'look', 'stop', 'play', 'like', 'want', 'go'],
  'i_want': ['food', 'water', 'go', 'eat', 'drink', 'play', 'mom', 'dad', 'toy', 'book', 'more', 'help'],
  'i_need': ['help', 'bathroom', 'water', 'food', 'mom', 'dad', 'go'],
  'i_feel': ['happy', 'sad'],
  'i_like': ['play', 'food', 'book', 'school', 'toy', 'mom', 'dad'],
  'i_go': ['home', 'school', 'bathroom'],
  'i_walk': ['home', 'school', 'bathroom'],
  'i_want_go': ['home', 'school', 'bathroom'],
  'want': ['food', 'water', 'play', 'go', 'mom', 'dad', 'toy', 'more', 'help'],
  'more': ['food', 'water', 'play', 'toy'],
  'i_more': ['food', 'water', 'play', 'toy'],
  'give': ['water', 'food', 'book', 'toy'],
  'you_give': ['water', 'food', 'book', 'toy'],
  'he_she': ['happy', 'sad', 'play', 'eat', 'sleep', 'walk', 'go'],
  'we': ['go', 'play', 'eat', 'walk', 'like'],
  'we_go': ['home', 'school'],
  'yes': ['please', 'more'],
  'no': ['stop', 'thank_you'],
  'please': ['help', 'stop', 'give', 'more'],
  'stop': ['please'],
  'help': ['please'],
};

// ============================================================
// Lief affect state (Sub-Phase 0 — mock-only)
// ============================================================

let liefState = {
  hrv: null,
  hrv_baseline_z: null,
  quintile: 1,
  valence: 0.9,
  arousal: 0.5,
  confidence: 0.0,
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

// --- App State ---
let selectedSymbols = [];
// Demo key (obfuscated)
// NOTE(mjp): use env var for this, anyone can still decode this key
const _k = atob('c2stcHJvai1WbHFqVjRTLS1NajRqQWpqSVljYm96QndWTFY2SElobEIxdlNhWUFGNk5QWVRURC1wS05meHdlS3pWd0l2R09qZVhUVlNwVEVOLVQzQmxia0ZKMjJGd0ZKNldoQ1F1NkdHNnZ5RTV3RkVSN2xPdE84TDdaenczX0ZfUlFSQ3FNUTlBaGRjTHpuazhzYVpEdk55WGg1RWZNREdBa0E=');
let apiKey = _k;
let pendingRequest = null;

// --- DOM References ---
const grid = document.getElementById('symbolGrid');
const sentenceDisplay = document.getElementById('sentenceDisplay');
const selectedStrip = document.getElementById('selectedStrip');
const btnSpeak = document.getElementById('btnSpeak');
const btnClear = document.getElementById('btnClear');
const autoSpeakCheckbox = document.getElementById('autoSpeak');
const showSuggestionsCheckbox = document.getElementById('showSuggestions');
const reorderSymbolsCheckbox = document.getElementById('reorderSymbols');
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

// --- Initialize ---
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

// Future extension: additional preset phrases ("I'm all done", "I need space",
// "I need to take a breath") can be added as buttons inside the break modal
// or as a quick-tap bar above the symbol grid.
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

  const totalSeconds = 120;
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

function init() {
  renderGrid();
  setupEventListeners();
  renderAffectWidget();
  updateSuggestions();
}

function renderGrid() {
  grid.innerHTML = '';
  SYMBOLS.forEach(sym => {
    const card = document.createElement('div');
    card.className = 'symbol-card';
    card.dataset.id = sym.id;
    card.dataset.category = sym.category;
    card.innerHTML = `
      <div class="symbol-icon">${sym.svg}</div>
      <div class="symbol-label">${sym.word}</div>
    `;
    card.addEventListener('click', () => handleSymbolTap(sym));
    grid.appendChild(card);
  });
}

function setupEventListeners() {
  btnSpeak.addEventListener('click', speakSentence);
  btnClear.addEventListener('click', clearAll);
  showSuggestionsCheckbox.addEventListener('change', () => {
    updateSuggestions();
  });
  reorderSymbolsCheckbox.addEventListener('change', () => {
    // Immediately reset all card ordering when toggled off
    if (!reorderSymbolsCheckbox.checked) {
      grid.querySelectorAll('.symbol-card').forEach(card => {
        card.style.order = '';
      });
    }
    updateSuggestions();
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
  });

  liefConnectBtn.addEventListener('click', () => {
    alert('Live Lief device connection coming soon. Use the simulated affect slider below to explore affect-aware predictions.');
  });

  btnBreak.addEventListener('click', showBreakModal);
  btnBreakResume.addEventListener('click', hideBreakModal);
  btnStartBreathe.addEventListener('click', startBreathingExercise);
  btnStopBreathe.addEventListener('click', hideBreakModal);
}

// --- Symbol Tap Handler ---
function handleSymbolTap(sym) {
  selectedSymbols.push(sym);
  renderSelectedStrip();
  updatePrediction();
  updateSuggestions();

  // Brief visual feedback
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
    const chip = document.createElement('div');
    chip.className = 'selected-chip';
    chip.innerHTML = `
      <svg viewBox="0 0 50 50" width="18" height="18">${sym.svg.replace(/<svg[^>]*>/, '').replace('</svg>', '')}</svg>
      ${sym.word}
      <span class="chip-remove">&times;</span>
    `;
    chip.addEventListener('click', () => removeSymbol(i));
    selectedStrip.appendChild(chip);
  });
}

// --- Prediction ---
async function updatePrediction() {
  if (selectedSymbols.length === 0) {
    sentenceDisplay.innerHTML = '<span class="placeholder">Tap symbols below to build a sentence...</span>';
    sentenceDisplay.classList.remove('loading');
    return;
  }

  const key = selectedSymbols.map(s => s.id).join('_');
  const words = selectedSymbols.map(s => s.word);
  const threshold = parseInt(confidenceSlider.value, 10);

  // Show loading state
  sentenceDisplay.classList.add('loading');

  // Dampening: the LLM tends to over-estimate confidence, so we apply a
  // structural multiplier based on how many symbols + what types are present.
  // This ensures 1-2 vague symbols can't cross the threshold no matter what the LLM says.
  const categories = selectedSymbols.map(s => s.category);
  const hasNounOrAdj = categories.some(c => c === 'noun' || c === 'adjective' || c === 'person');
  function dampenConfidence(rawConfidence) {
    let multiplier;
    if (selectedSymbols.length === 1) multiplier = 0.3;
    else if (selectedSymbols.length === 2 && !hasNounOrAdj) multiplier = 0.55;
    else if (selectedSymbols.length === 2) multiplier = 0.85;
    else if (selectedSymbols.length >= 3 && hasNounOrAdj) multiplier = 1.0;
    else multiplier = 0.75;
    return Math.round(rawConfidence * multiplier);
  }

  // Try API prediction
  if (apiKey) {
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

  // Fallback: rule-based prediction with local confidence
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
  // Estimate confidence based on what categories are present
  const categories = selectedSymbols.map(s => s.category);
  const hasSubject = categories.some(c => c === 'pronoun' || c === 'person');
  const hasVerb = categories.some(c => c === 'verb');
  const hasObject = categories.some(c => c === 'noun' || c === 'adjective');

  let confidence;
  if (selectedSymbols.length === 1) confidence = 25;
  else if (hasSubject && hasVerb && hasObject) confidence = 85;
  else if (hasSubject && hasVerb) confidence = 45;
  else if (hasVerb && hasObject) confidence = 65;
  else confidence = 30 + (selectedSymbols.length * 10);

  // Build the sentence
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
  // Basic sentence construction
  let sentence = words.map((w, i) => {
    if (i === 0) return w;
    return w.toLowerCase();
  }).join(' ');

  // Add period if not ending with punctuation
  if (!/[.!?]$/.test(sentence)) sentence += '.';
  return sentence;
}

// ============================================================
// Affect → prediction modulation (v1 mechanism, first implementation)
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

function getAffectTemperature(state) {
  return 0.25 + (state.valence * 0.65);
}

function applyAffectToRequest(state) {
  if (state.confidence < 0.3) {
    return { systemPrompt: '', temperature: 0.3 };
  }
  // Temperature is fixed — style modulation comes entirely from the system prompt.
  // getAffectTemperature() is preserved if we want to re-enable valence-scaled temp.
  return {
    systemPrompt: buildAffectSystemPrompt(state),
    temperature: 0.3,
  };
}

async function predictWithAPI(words) {
  // Cancel any pending request
  if (pendingRequest) {
    pendingRequest.abort();
  }

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
  if (affect.systemPrompt) {
    messages.push({ role: 'system', content: affect.systemPrompt });
  }
  messages.push({ role: 'user', content: prompt });

  // NOTE(mjp): replace with local SLM in later phases
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: messages,
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

// --- Auto-Suggest ---
function updateSuggestions() {
  // Clear all suggestions and reset order
  grid.querySelectorAll('.symbol-card').forEach(card => {
    card.classList.remove('suggested');
    card.style.order = '';
  });

  // If both toggles are off, nothing to do
  if (!showSuggestionsCheckbox.checked && !reorderSymbolsCheckbox.checked) return;

  const key = selectedSymbols.map(s => s.id).join('_');

  // Find matching suggestions
  let suggestedIds = NEXT_WORD_MAP[key];

  // If no exact match, try shorter keys
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

  if (!suggestedIds) suggestedIds = NEXT_WORD_MAP[''];

  // Apply suggestions — highlight and/or reorder based on toggles
  suggestedIds.forEach((id, index) => {
    const card = grid.querySelector(`[data-id="${id}"]`);
    if (card) {
      if (showSuggestionsCheckbox.checked) {
        card.classList.add('suggested');
      }
      if (reorderSymbolsCheckbox.checked) {
        card.style.order = -100 + index;
      }
    }
  });
}

// --- Text to Speech ---
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
  if (isSpeaking) {
    stopSpeaking();
    return;
  }
  // Read only the predicted sentence text, not the confidence badge
  const predictedEl = sentenceDisplay.querySelector('.predicted-text');
  const text = predictedEl ? predictedEl.textContent.trim() : '';
  if (text) speakText(text);
}

async function speakText(text) {
  stopSpeaking();
  updateSpeakButtonState(true);

  if (apiKey) {
    try {
      await speakWithOpenAI(text);
      return;
    } catch (e) {
      console.warn('OpenAI TTS failed, falling back to browser:', e);
    }
  }

  speakWithBrowser(text);
}

async function speakWithOpenAI(text) {
  const response = await fetch('https://api.openai.com/v1/audio/speech', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: 'tts-1',
      input: text,
      voice: 'nova',
      speed: 0.9
    })
  });

  if (!response.ok) throw new Error(`TTS API error: ${response.status}`);

  const audioBlob = await response.blob();
  const audioUrl = URL.createObjectURL(audioBlob);
  currentAudio = new Audio(audioUrl);
  currentAudio.addEventListener('ended', () => {
    URL.revokeObjectURL(audioUrl);
    currentAudio = null;
    updateSpeakButtonState(false);
  });
  currentAudio.addEventListener('error', () => {
    URL.revokeObjectURL(audioUrl);
    currentAudio = null;
    updateSpeakButtonState(false);
  });
  await currentAudio.play();
}

function speakWithBrowser(text) {
  if (!('speechSynthesis' in window)) {
    updateSpeakButtonState(false);
    return;
  }
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
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
  window.speechSynthesis?.cancel();
  updateSpeakButtonState(false);
}

// Preload browser voices as fallback
if ('speechSynthesis' in window) {
  window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

// --- Clear ---
function clearAll() {
  selectedSymbols = [];
  renderSelectedStrip();
  sentenceDisplay.innerHTML = '<span class="placeholder">Tap symbols below to build a sentence...</span>';
  sentenceDisplay.classList.remove('loading');
  updateSuggestions();
  stopSpeaking();
}

// --- Utility ---
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// --- Start ---
init();
