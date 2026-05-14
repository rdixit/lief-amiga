# 🔎 Vocabulary Collision Analysis — AMIGA-AAC Canonical Vocabulary

*Generated from: AMIGA_AAC_Vocabulary_Expansion_Packet_4_5_2026_canonical_vocabulary.xlsx*
*424 total rows · 16 current categories · ~144 questionable classifications*

---

## Overview

The spreadsheet collision problems fall into four distinct failure modes, each with a different root cause and fix. The goal of this analysis is to inform the re-mapping of words to **Meaning Room zones** rather than patching the existing category system.

---

## Failure Mode 1 — `People/Pronouns/Possessives` Is a Catch-All (97 words, ~40% wrong)

This is the worst offender. The category legitimately contains `I, me, my, you, he, she, they, mom, dad` — but also contains, with no defensible logic:

- **Vehicles:** `airplane, bus` → should be Environment / Vehicles
- **Body parts:** `tummy, tummy/stomach, head, hair, hands` → should be Body
- **Emotional states:** `frustrated, nervous, sick` → should be Feelings
- **Adjectives:** `messy, mean, middle, still, well` → should be Descriptors
- **Verbs/auxiliaries:** `bite, came, did, fixed, lift, pick, remember, said, went` → should be Actions
- **Pure function words:** `if, is, it, just, must, some, then, there, those, us, with, when, where` → should be Function/Core
- **Abstract nouns:** `name, piece, side, time, way` → Uncategorized is more honest
- **Animals:** `bird, birds` → no zone for this yet; candidate for Environment
- **Numbers:** `five` → no zone for this yet

**Root cause:** The Marvin Tier 3 bulk import assigned `pronoun/person` as the part-of-speech default to any word that wasn't obviously a verb or adjective.

**Fix:** Split into three clean zones:
- `Self` → I / me / my / mine / myself
- `People` → mom, dad, you, he, she, they, her, him, we, us, our, somebody, someone, everybody, guys, girl, boy, mommy
- Re-route everything else explicitly — nothing silently absorbed

---

## Failure Mode 2 — `Actions` Is a Verb/Noun Salad (109 words, ~30% wrong)

Actions contains actual verbs (correct) but also:

- **Nouns miscategorized as verbs:** `dog, doll, house, door, doctor` — got `verb/action` as POS, which is wrong
- **Adjectives:** `great, ready` — not actions
- **Conjunctions/connectives:** `already, because, together` — not actions
- **Regulation duplicates:** `"too loud / I need a break"`, `"I need help / stop"` — duplicates entries already in Regulation/Safety
- **A meta-note that became a row:** `"could be specific to use quiet space, alone space"` — this is a Joannalyn annotation, not a vocabulary entry; **should be deleted**

**Fix:** Verbs in Actions map cleanly to the 🎯 Intent/Actions zone in the Meaning Room. Nouns, adjectives, and connectives need routing to their correct zones. The meta-note row should be removed.

---

## Failure Mode 3 — `Places` Is Four Different Things (30 words, ~50% wrong)

| Subgroup | Words | Correct Meaning Room Zone |
|---|---|---|
| Actual locations | `home, bathroom, classroom, gym` | 🌍 Environment |
| Spatial prepositions | `in, out, up, down, off, about, inside, around` | 🌍 Environment (directional) |
| Wrong category | `mine, fine, pink, mouth, cup, finger, paint, being, kind` | Possessive / Social / Descriptors / Body / Function |
| Vehicles | `train` | Vehicles / Environment |
| Toys/items | `trampoline` | Preferred Items |

`mine` is a possessive. `fine` is a social response. `pink` is a color/descriptor. `mouth` is a body part. These were miscategorized during the Marvin import.

---

## Failure Mode 4 — Feelings Words Split Across 3 Categories

Emotional vocabulary is fragmented with no consistent logic:

| Current Category | Words |
|---|---|
| `Feelings` | happy, mad, sad, made |
| `Descriptors` | tired |
| `People/Pronouns/Possessives` | frustrated, nervous, sick |

All nine belong in the 🙂 Feelings zone. The split means anyone building the Feelings grid must know to look in three places — which is exactly the kind of thing that causes hand-curation errors downstream.

---

## Other Smaller Issues

- **`Clothing` contains `what` and `what's`** — question words; likely a row-import accident
- **`Social` contains `books, chips, cookie, shirt, white`** — food, clothing, and a color landed here
- **68 `Uncategorized` words** — all Tier 3 Marvin words honestly left unassigned. Subgroups:
  - Function words: `also, almost, both, even, last, lot, many, much, never, only, really, very, yet`
  - Time words: `after, before, today, back, away, again` → belong in 🕒 Time zone
  - Nature/environment nouns: `trees, leaves, bugs, ant` → candidate for outdoor Environment sub-zone
  - Discourse markers / fillers: `oh, um, huh, hum, ya` → Social or Function

---

## Recommended Fix Strategy

Rather than patching the existing `category` column, add a new column **`meaning_room_zone`** and populate it cleanly, leaving `category` as an audit trail. Benefits:

1. Existing app code depending on `category` doesn't break during transition
2. Provides a before/after comparison Joannalyn and Gabby can review
3. The ~144 questionable entries become visible as rows where `meaning_room_zone` differs from what `category` implies — the exact diff the team needs to review

### Proposed 16-Zone Taxonomy (Meaning Room)

`Self` · `People` · `Feelings` · `Body` · `Actions` · `Regulation` · `Time` · `Places/Environment` · `Food/Drink` · `Clothing` · `Preferred Items` · `Descriptors` · `Negation` · `Social` · `Function` · `Questions`

Wide enough to avoid deep nesting at Tier 3. Tight enough to map one-to-one with scene anchor objects at Tier 1.

---

*Next action: add `meaning_room_zone` column to spreadsheet and run bulk re-mapping pass for team review.*
