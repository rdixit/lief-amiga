#!/usr/bin/env python3
"""
Cross-validate category × tab × POS for all vocabulary symbols.

Reads data/canonical_vocabulary.csv and generates data/category_audit.csv
with one row per symbol that has a finding (error, override, or review).

Usage:
  python3 scripts/audit_categories.py             # generate audit CSV (read-only)
  python3 scripts/audit_categories.py --apply     # apply approved=Y rows to canonical CSV

Buckets:
  error    — POS definitively contradicts the current category; proposed_category is filled in
  override — Category and POS agree, but current ui_tab differs from category_config default
  review   — Ambiguous; proposed_category left blank for human decision
  (consistent symbols are omitted from the audit CSV)
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CANONICAL_PATH = REPO / "data" / "canonical_vocabulary.csv"
AUDIT_PATH = REPO / "data" / "category_audit.csv"
VOCAB_PATH = REPO / "vocabulary.json"
ROOM_PATH = REPO / "meaning_room.json"

# These POS values unambiguously require a specific category.
POS_TO_REQUIRED_CAT = {
    "verb/action": "Actions",
    "pronoun/person": "People/Pronouns/Possessives",
    "negation/repair": "Negation/Repair",
    "question word": "Question Words",
}

# Categories that are acceptable for a given POS even if not the primary category.
POS_ALLOWED_CATS = {
    "verb/action": {"Actions", "Function/Core"},
}

# These POS values restrict to a small valid set; outside = error.
POS_TO_VALID_CATS = {
    "descriptor/adjective": {"Descriptors", "Feelings"},
}

# Valid noun categories for each ui_tab (including pre-Phase-2 mappings).
TAB_NOUN_CATEGORIES = {
    "things": {"Body Parts", "Clothing", "Places", "Preferred Items", "Vehicles", "Food/Drink"},
    "people": {"People/Pronouns/Possessives"},
    "feelings": {"Feelings"},
    "actions": {"Actions"},
    "food": {"Food/Drink"},
    "more": {"Function/Core", "Uncategorized", "Question Words", "Descriptors"},
    "core": {"Social", "Negation/Repair", "Regulation/Safety"},
    "describe": {"Descriptors"},
}

# Anchor → category mapping for subcategory disambiguation.
ANCHOR_TO_CAT = {
    "food_drink": "Food/Drink",
    "toys": "Preferred Items",
    "clothing": "Clothing",
    "self": "Body Parts",
    "outside": "Places",
    "feelings": "Feelings",
    "actions": "Actions",
    "stop_refusal": "Negation/Repair",
    "calm_corner": "Regulation/Safety",
    "other_people": "People/Pronouns/Possessives",
    "colors_descriptors": "Descriptors",
    "time": "Function/Core",
}

# Known word patterns for subcategory detection when anchor data isn't available.
KNOWN_QUESTION_WORDS = {"what", "what's", "which", "how", "who", "why", "when", "where", "where's"}
KNOWN_FUNCTION_WORDS = {
    "is", "isn't", "just", "must", "if", "first", "five", "middle",
    "here", "here's", "some", "sometimes", "still", "then", "there",
    "there's", "these", "this", "that", "well", "with", "another",
    "about", "again", "being", "everything", "something", "kind",
    "while", "side", "time", "already",
}
KNOWN_REGULATION = {"one more minute"}
KNOWN_DIRECTIONAL = {"up", "down", "in", "out", "off", "on", "around", "away", "back", "through", "inside"}


def _load_anchor_membership():
    """Load symbol_id → [anchor_ids] from meaning_room.json."""
    membership = {}
    if ROOM_PATH.exists():
        with open(ROOM_PATH) as f:
            room = json.load(f)
        for a in room.get("anchors", []):
            for sid in a["symbol_ids"]:
                membership.setdefault(sid, []).append(a["id"])
    return membership


def _load_vocab_ids():
    """Load canonical_term → symbol_id mapping from vocabulary.json."""
    mapping = {}
    if VOCAB_PATH.exists():
        with open(VOCAB_PATH) as f:
            vocab = json.load(f)
        for sym in vocab.get("symbols", []):
            ct = sym.get("canonical_term", "").strip()
            if ct:
                mapping[ct] = sym["id"]
    return mapping


KNOWN_VEHICLES = {"airplane", "bus", "car", "train", "boat", "truck", "bike", "bicycle", "helicopter", "motorcycle"}
KNOWN_PLACES = {"playground", "hill", "house", "door", "home", "school", "bathroom", "gym",
                "classroom", "sand", "outside", "park", "store", "church", "library", "room",
                "kitchen", "bedroom", "yard", "garden", "pool", "beach", "forest", "farm",
                "fire", "ant", "bugs", "bird", "birds", "leaves", "trees"}
KNOWN_BODY_PARTS = {"tummy", "stomach", "tummy/stomach", "hair", "head", "ear", "eye",
                    "hand", "leg", "nose", "mouth", "face", "arm", "foot", "feet",
                    "finger", "toe", "teeth", "tooth", "back", "knee", "neck", "belly"}
KNOWN_CLOTHING = {"shirt", "jacket", "coat", "hat", "pants", "shoe", "sock", "dress",
                  "boots", "gloves", "mittens", "scarf", "shorts", "sweater", "pajamas"}
KNOWN_FOOD = {"chips", "cookie", "candy", "popcorn", "pretzel", "rice", "fruit", "carrot",
              "corn", "bean", "lunch", "breakfast", "dinner", "snack", "apple", "banana",
              "milk", "cheese", "bread", "chicken", "pizza", "cake", "ice cream", "egg",
              "cereal", "soup", "sandwich", "yogurt", "cracker", "noodles", "meat"}
KNOWN_PEOPLE = {"doctor", "teacher", "friend", "baby", "man", "woman", "boy", "girl",
                "brother", "sister", "grandma", "grandpa", "aunt", "uncle", "cousin",
                "neighbor", "nurse", "therapist"}


def _propose_things_subcategory(canonical_term, anchor_ids):
    """Pick the best subcategory for a noun in the 'things' tab."""
    ct_lower = canonical_term.lower()

    # Keyword match first (more specific than anchor)
    if ct_lower in KNOWN_VEHICLES:
        return "Vehicles"
    if ct_lower in KNOWN_PLACES:
        return "Places"
    if ct_lower in KNOWN_BODY_PARTS:
        return "Body Parts"
    if ct_lower in KNOWN_CLOTHING:
        return "Clothing"
    if ct_lower in KNOWN_FOOD:
        return "Food/Drink"

    # Fall back to anchor membership
    for aid in anchor_ids:
        cat = ANCHOR_TO_CAT.get(aid)
        if cat and cat in TAB_NOUN_CATEGORIES["things"]:
            return cat
    return "Preferred Items"


def _propose_more_subcategory(canonical_term, pos):
    """Pick the best subcategory for a word in the 'more' tab."""
    term_lower = canonical_term.lower().replace("\u2019", "'")
    if term_lower in KNOWN_QUESTION_WORDS:
        return "Question Words"
    if term_lower in KNOWN_DIRECTIONAL:
        return "Descriptors"
    if term_lower in KNOWN_REGULATION:
        return "Regulation/Safety"
    if term_lower in KNOWN_FUNCTION_WORDS or pos == "word":
        return "Function/Core"
    return "Uncategorized"


def _effective_pos(row):
    """For phrases, use phrase_pos as the semantic signal when available."""
    if row.get("type", "").strip() == "phrase":
        pp = row.get("phrase_pos", "").strip()
        if pp:
            return pp
    return row.get("part_of_speech", "").strip()


def classify(row, cat_config, anchor_membership, term_to_id):
    """
    Return (bucket, proposed_category, rationale).
    bucket is one of: 'error', 'override', 'review', 'consistent'
    """
    ct = row.get("canonical_term", "").strip()
    cat = row.get("category", "").strip()
    pos = _effective_pos(row)
    ui_tab = row.get("ui_tab", "").strip()

    sym_id = term_to_id.get(ct, ct.replace(" ", "_"))
    anchors = anchor_membership.get(sym_id, [])

    # --- Rule 0: Known noun-like words with wrong POS=verb/action ---
    # These have stale POS tags; use ui_tab + keyword lookup to catch them.
    ct_lower = ct.lower()
    if pos == "verb/action" and ui_tab not in ("actions", "core"):
        is_known_noun = (
            ct_lower in KNOWN_PLACES
            or ct_lower in KNOWN_PEOPLE
            or ct_lower in KNOWN_VEHICLES
            or ct_lower in KNOWN_BODY_PARTS
            or ct_lower in KNOWN_CLOTHING
            or ct_lower in KNOWN_FOOD
        )
        if is_known_noun:
            if ui_tab == "things":
                proposed = _propose_things_subcategory(ct, anchors)
            elif ui_tab == "people":
                proposed = "People/Pronouns/Possessives"
            elif ui_tab == "food":
                proposed = "Food/Drink"
            else:
                proposed = "Uncategorized"
            return (
                "error",
                proposed,
                f"POS=verb/action but known noun ({ct!r}); ui_tab={ui_tab!r} → {proposed!r}; also fix POS",
            )

    # --- Rule 1: POS unambiguously requires a specific category ---
    if pos in POS_TO_REQUIRED_CAT:
        required = POS_TO_REQUIRED_CAT[pos]
        allowed = POS_ALLOWED_CATS.get(pos, {required})
        if cat not in allowed:
            return "error", required, f"POS={pos!r} requires category={required!r}"

    if pos in POS_TO_VALID_CATS and row.get("type", "").strip() != "phrase":
        valid = POS_TO_VALID_CATS[pos]
        if cat not in valid:
            proposed = "Feelings" if ui_tab == "feelings" else "Descriptors"
            return "error", proposed, f"POS={pos!r} requires category in {sorted(valid)}"

    # --- Rule 2: noun/location/word in a category that doesn't match ui_tab ---
    if pos in ("noun", "location/preposition", "word"):
        cat_default_tab = cat_config.get(cat, {}).get("default_tab", "")
        if cat_default_tab and ui_tab and cat_default_tab != ui_tab:
            valid_cats = TAB_NOUN_CATEGORIES.get(ui_tab, set())
            if cat not in valid_cats:
                # Smart subcategory proposal based on tab + anchor + keywords
                ct_lower = ct.lower()
                if ui_tab == "things":
                    proposed = _propose_things_subcategory(ct, anchors)
                elif ui_tab == "more":
                    proposed = _propose_more_subcategory(ct, pos)
                elif ui_tab == "people":
                    if ct_lower in KNOWN_PEOPLE:
                        proposed = "People/Pronouns/Possessives"
                    else:
                        proposed = "People/Pronouns/Possessives"
                elif ui_tab == "core":
                    proposed = "Social"
                elif ui_tab == "feelings":
                    proposed = "Feelings"
                elif ui_tab == "food":
                    proposed = "Food/Drink"
                elif ui_tab == "actions":
                    if ct_lower in KNOWN_PLACES:
                        proposed = "Places"
                    elif ct_lower in KNOWN_FOOD:
                        proposed = "Food/Drink"
                    elif ct_lower in KNOWN_PEOPLE:
                        proposed = "People/Pronouns/Possessives"
                    elif ct_lower in KNOWN_VEHICLES:
                        proposed = "Vehicles"
                    elif pos == "noun":
                        proposed = "Preferred Items"
                    else:
                        proposed = "Actions"
                elif ui_tab == "describe":
                    proposed = "Descriptors"
                else:
                    proposed = "Uncategorized"
                return (
                    "error",
                    proposed,
                    f"cat={cat!r} (default_tab={cat_default_tab!r}) doesn't match ui_tab={ui_tab!r}; "
                    f"proposed {proposed!r} via anchor/keyword heuristic",
                )

    # --- Rule 3: location/preposition in wrong bucket (even if tab matches) ---
    if pos == "location/preposition" and cat not in {"Function/Core", "Places", "Descriptors"}:
        ct_lower = ct.lower()
        if ct_lower in KNOWN_DIRECTIONAL:
            proposed = "Descriptors"
        else:
            proposed = "Descriptors" if ui_tab in ("more", "describe") else "Places"
        return "error", proposed, f"POS={pos!r} with cat={cat!r}; directional/spatial word"

    # --- Bucket 2: category and POS are consistent, tab is a deliberate override ---
    if cat in cat_config and ui_tab:
        default_tab = cat_config[cat]["default_tab"]
        if ui_tab != default_tab:
            return (
                "override",
                cat,
                f"category={cat!r} default_tab={default_tab!r} but current ui_tab={ui_tab!r}",
            )

    return "consistent", "", ""


def _secondary_tabs_for_core(bucket, current_cat, proposed_cat, cat_config):
    """
    For a symbol currently in the core tab, return the secondary tab it should
    also appear in, based on the target category's default tab.
    Returns empty string if the target category already defaults to core.
    """
    if bucket == "error" and proposed_cat:
        target_cat = proposed_cat
    else:
        target_cat = current_cat

    target_default = cat_config.get(target_cat, {}).get("default_tab", "")
    return target_default if target_default and target_default != "core" else ""


def generate_audit(cat_config):
    rows_out = []
    buckets = Counter()
    anchor_membership = _load_anchor_membership()
    term_to_id = _load_vocab_ids()

    with open(CANONICAL_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ct = row.get("canonical_term", "").strip()
            if not ct:
                continue

            bucket, proposed, rationale = classify(row, cat_config, anchor_membership, term_to_id)
            buckets[bucket] += 1

            if bucket == "consistent":
                continue

            ui_tab = row.get("ui_tab", "").strip()
            current_cat = row.get("category", "").strip()

            # Auto-fill secondary_tabs for all core-tab words (policy: stay in core + duplicate)
            if ui_tab == "core":
                secondary = _secondary_tabs_for_core(bucket, current_cat, proposed, cat_config)
            else:
                secondary = ""

            rows_out.append({
                "canonical_term": ct,
                "tier": row.get("priority_tier", ""),
                "type": row.get("type", ""),
                "current_category": current_cat,
                "part_of_speech": row.get("part_of_speech", "").strip(),
                "phrase_pos": row.get("phrase_pos", "").strip(),
                "ui_tab": ui_tab,
                "bucket": bucket,
                "proposed_category": proposed,
                "rationale": rationale,
                "secondary_tabs": secondary,
                "approved": "",
            })

    fieldnames = [
        "canonical_term", "tier", "type", "current_category",
        "part_of_speech", "phrase_pos", "ui_tab",
        "bucket", "proposed_category", "rationale",
        "secondary_tabs", "approved",
    ]
    with open(AUDIT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows_out)

    total = sum(buckets.values())
    print(f"Audit written to {AUDIT_PATH}")
    print(f"  Total symbols:  {total}")
    print(f"  error:          {buckets['error']:4d}  (auto-fix ready, needs approval)")
    print(f"  override:       {buckets['override']:4d}  (intentional tab override, confirm)")
    print(f"  review:         {buckets['review']:4d}  (ambiguous, fill in proposed_category)")
    print(f"  consistent:     {buckets['consistent']:4d}  (no action needed, omitted from CSV)")
    print()
    print("Column guide:")
    print("  proposed_category  — fill in for 'review' rows; pre-filled for 'error' rows")
    print("  secondary_tabs     — auto-filled for core-tab words (policy: stay in core + duplicate).")
    print("                       Clear if you change a review word to Social/Negation/Repair")
    print("                       (those default to core anyway, so no duplication needed).")
    print("  approved           — set Y to apply; leave blank or N to skip")
    print()
    print("When done: python3 scripts/audit_categories.py --apply")
    return rows_out


def apply_audit():
    if not AUDIT_PATH.exists():
        print(f"ERROR: {AUDIT_PATH} not found. Run without --apply first.")
        sys.exit(1)

    # Load approved changes from audit CSV
    # changes: canonical_term -> (proposed_category, secondary_tabs)
    changes: dict[str, tuple[str, str]] = {}
    skipped = []
    with open(AUDIT_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ct = row.get("canonical_term", "").strip()
            approved = row.get("approved", "").strip().upper()
            proposed = row.get("proposed_category", "").strip()
            secondary = row.get("secondary_tabs", "").strip()
            bucket = row.get("bucket", "").strip()
            if approved == "Y":
                # Override rows: category unchanged, but secondary_tabs may still be set
                if bucket == "override" and not secondary:
                    continue
                if bucket != "override" and not proposed:
                    print(f"  WARNING: {ct!r} approved=Y but proposed_category is blank — skipping")
                    skipped.append(ct)
                    continue
                changes[ct] = (proposed, secondary)
            else:
                skipped.append(ct)

    if not changes:
        print("No approved changes to apply.")
        return

    # Read canonical CSV; add secondary_tabs column if missing
    rows_out = []
    applied_cat = []
    applied_secondary = []
    with open(CANONICAL_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if "secondary_tabs" not in fieldnames:
            fieldnames.append("secondary_tabs")
        for row in reader:
            ct = row.get("canonical_term", "").strip()
            if ct in changes:
                proposed_cat, secondary = changes[ct]
                if proposed_cat:
                    old_cat = row.get("category", "").strip()
                    row["category"] = proposed_cat
                    applied_cat.append((ct, old_cat, proposed_cat))
                if secondary:
                    row["secondary_tabs"] = secondary
                    applied_secondary.append((ct, secondary))
            rows_out.append(row)

    with open(CANONICAL_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows_out)

    if applied_cat:
        print(f"Applied {len(applied_cat)} category changes to {CANONICAL_PATH}:")
        for ct, old, new in applied_cat:
            print(f"  {ct:35s}  {old!r:35s} → {new!r}")
    if applied_secondary:
        print(f"\nApplied {len(applied_secondary)} secondary_tabs values:")
        for ct, tabs in applied_secondary:
            print(f"  {ct:35s}  secondary_tabs={tabs!r}")
    if not applied_cat and not applied_secondary:
        print("No approved changes to apply.")
    if skipped:
        print(f"\nSkipped {len(skipped)} rows (not approved or blank proposed_category).")


def main():
    # Import here to avoid circular issues when running as __main__
    import sys
    sys.path.insert(0, str(REPO / "scripts"))
    from category_utils import load_category_config

    cat_config = load_category_config()

    if "--apply" in sys.argv:
        apply_audit()
    else:
        generate_audit(cat_config)


if __name__ == "__main__":
    main()
