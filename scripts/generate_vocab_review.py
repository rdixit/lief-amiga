#!/usr/bin/env python3
"""
Generate data/vocab_review.csv: a curated, human-reviewable subset of the
sanity-check findings in data/union_table_issues.csv.

Filters out symbols on the INTENTIONAL_OVERRIDES and AMBIGUOUS lists below so
the review file only surfaces genuinely new mismatches that need a decision.

If the legacy data/_archive/category_audit.csv file is still present, any of
its unapplied secondary_tabs proposals are also included. Once that file is
retired the script just skips that step.

Usage: python3 scripts/generate_vocab_review.py
"""

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CANONICAL_PATH = REPO / "data" / "canonical_vocabulary.csv"
AUDIT_PATH = REPO / "data" / "_archive" / "category_audit.csv"
ISSUES_PATH = REPO / "data" / "union_table_issues.csv"
UNION_PATH = REPO / "data" / "vocabulary_union_table.csv"
OUT_PATH = REPO / "data" / "vocab_review.csv"

sys.path.insert(0, str(REPO / "scripts"))
from category_utils import load_category_config

POS_TO_CATEGORY = {
    "verb/action": "Actions",
    "pronoun/person": "People/Pronouns/Possessives",
    "negation/repair": "Negation/Repair",
    "question word": "Question Words",
    "descriptor/adjective": "Descriptors",
}

INTENTIONAL_OVERRIDES = {
    # Negations / auxiliary verbs intentionally placed in 'more' (grammar) tab
    "arent", "cant", "couldnt", "havent", "not", "wont",
    "doesnt", "dont", "done", "gonna", "hum", "ready",
    # Phrases placed for accessibility / contextual reasons; POS-cat
    # tension is known and accepted (would require phrase_pos changes
    # or sanity_check exceptions to silence)
    "i_found_something", "books",
    "i_need_the_bathroom", "too_loud", "too_loud_i_need_a_break",
    "i_want_a_jacket", "i_want_apple", "i_want_food",
    "thats_funny", "one_more_minute",
    # 'named' = descriptor (e.g. "a person named Faison") kept in
    # people tab for naming context; tab=people vs cat=Descriptors
    # is intentional.
    "named",
}

AMBIGUOUS = {"slide", "swing", "not_that"}

FIELDNAMES = [
    "canonical_term",
    "issue_source",
    "priority_tier",
    "current_category",
    "proposed_category",
    "current_ui_tab",
    "proposed_ui_tab",
    "current_secondary_tabs",
    "proposed_secondary_tabs",
    "current_pos",
    "proposed_pos",
    "audit_pos",
    "phrase_pos",
    "current_anchors",
    "proposed_anchors",
    "issues",
    "rationale",
    "action",
    "notes",
]


def load_canonical():
    rows = {}
    with open(CANONICAL_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ct = row.get("canonical_term", "").strip()
            if ct:
                rows[ct] = row
    return rows


def load_audit():
    """Load legacy category_audit.csv if it still exists; otherwise return {}."""
    if not AUDIT_PATH.exists():
        return {}
    rows = {}
    with open(AUDIT_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ct = row.get("canonical_term", "").strip()
            if ct:
                rows[ct] = row
    return rows


def load_union():
    rows = {}
    with open(UNION_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sid = row.get("symbol_id", "").strip()
            if sid:
                rows[sid] = row
    return rows


def load_issues():
    rows = {}
    with open(ISSUES_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sid = row.get("symbol_id", "").strip()
            if sid:
                rows[sid] = row
    return rows


def sid_to_canonical_term(union_rows, canonical_rows):
    """Build symbol_id -> canonical_term mapping using display_label fallback."""
    mapping = {}
    canon_by_lower = {ct.lower(): ct for ct in canonical_rows}
    for sid, urow in union_rows.items():
        dl = urow.get("display_label", "").strip()
        if dl.lower() in canon_by_lower:
            mapping[sid] = canon_by_lower[dl.lower()]
        else:
            ct_guess = sid.replace("_", " ")
            if ct_guess in canonical_rows:
                mapping[sid] = ct_guess
            elif ct_guess.lower() in canon_by_lower:
                mapping[sid] = canon_by_lower[ct_guess.lower()]
    return mapping


def main():
    canonical = load_canonical()
    audit = load_audit()
    union = load_union()
    issues = load_issues()
    sid_to_ct = sid_to_canonical_term(union, canonical)

    review = {}

    # 1. Secondary tabs proposals from audit
    for ct, arow in audit.items():
        proposed_sec = arow.get("secondary_tabs", "").strip()
        if not proposed_sec:
            continue
        crow = canonical.get(ct, {})
        if not crow:
            continue

        # Skip rows where the proposal has already been applied to canonical
        current_sec = (crow.get("secondary_tabs") or "").strip()
        if current_sec == proposed_sec:
            continue

        review[ct] = {
            "canonical_term": ct,
            "issue_source": "secondary_tabs",
            "priority_tier": crow.get("priority_tier", ""),
            "current_category": crow.get("category", ""),
            "proposed_category": "",
            "current_ui_tab": crow.get("ui_tab", ""),
            "proposed_ui_tab": "",
            "current_secondary_tabs": crow.get("secondary_tabs", ""),
            "proposed_secondary_tabs": proposed_sec,
            "current_pos": crow.get("part_of_speech", ""),
            "proposed_pos": "",
            "audit_pos": arow.get("part_of_speech", ""),
            "phrase_pos": crow.get("phrase_pos", ""),
            "current_anchors": "",
            "proposed_anchors": "",
            "issues": "",
            "rationale": arow.get("rationale", ""),
            "action": "",
            "notes": "",
        }
        # Fill anchors from union table
        for sid, uct in sid_to_ct.items():
            if uct == ct:
                review[ct]["current_anchors"] = union[sid].get("meaning_room_anchors", "")
                break

    # 2. Genuine issues from sanity check
    for sid, irow in issues.items():
        if sid in INTENTIONAL_OVERRIDES or sid in AMBIGUOUS:
            continue

        ct = sid_to_ct.get(sid, "")
        if not ct:
            ct = irow.get("display_label", sid).strip()
            if ct not in canonical:
                ct_lower = {k.lower(): k for k in canonical}
                ct = ct_lower.get(ct.lower(), ct)

        crow = canonical.get(ct, {})
        arow = audit.get(ct, {})

        if ct in review:
            review[ct]["issue_source"] = "both"
            review[ct]["issues"] = irow.get("issues", "")
            if not review[ct]["proposed_category"] and arow.get("proposed_category", ""):
                review[ct]["proposed_category"] = arow.get("proposed_category", "")
        else:
            review[ct] = {
                "canonical_term": ct,
                "issue_source": "sanity_check",
                "priority_tier": crow.get("priority_tier", irow.get("priority_tier", "")),
                "current_category": crow.get("category", irow.get("category_xls", "")),
                "proposed_category": arow.get("proposed_category", ""),
                "current_ui_tab": crow.get("ui_tab", irow.get("ui_tab", "")),
                "proposed_ui_tab": "",
                "current_secondary_tabs": crow.get("secondary_tabs", ""),
                "proposed_secondary_tabs": "",
                "current_pos": crow.get("part_of_speech", irow.get("current_pos", "")),
                "proposed_pos": "",
                "audit_pos": arow.get("part_of_speech", ""),
                "phrase_pos": crow.get("phrase_pos", irow.get("phrase_pos", "")),
                "current_anchors": irow.get("meaning_room_anchors", ""),
                "proposed_anchors": "",
                "issues": irow.get("issues", ""),
                "rationale": arow.get("rationale", ""),
                "action": "",
                "notes": "",
            }

    # 3. Infer proposed values from issues + category_config
    config = load_category_config()
    cat_to_tab = {cat: v["default_tab"] for cat, v in config.items()}
    cat_to_anchors = {cat: v["default_anchors"] for cat, v in config.items()}

    for ct, r in review.items():
        issues = r.get("issues", "")
        cur_cat = r["current_category"]
        cur_tab = r["current_ui_tab"]
        cur_pos = r["current_pos"]
        cur_anchors = r["current_anchors"]
        phrase_pos = r["phrase_pos"]
        effective_pos = phrase_pos if r.get("priority_tier", "") and phrase_pos else cur_pos

        # Infer proposed_category from POS if not already set
        if not r["proposed_category"] and "expects category" in issues:
            inferred = POS_TO_CATEGORY.get(effective_pos, "")
            if inferred and inferred != cur_cat:
                r["proposed_category"] = inferred

        # Infer proposed_category for location/preposition Uncategorized
        if not r["proposed_category"] and cur_pos == "location/preposition" and cur_cat == "Uncategorized":
            r["proposed_category"] = "Function/Core"

        # Determine the "target category" for tab/anchor inference
        target_cat = r["proposed_category"] or cur_cat

        # Infer proposed_ui_tab from target category's default
        if "TAB mismatch" in issues and not r["proposed_ui_tab"]:
            default_tab = cat_to_tab.get(target_cat, "")
            if default_tab and default_tab != cur_tab:
                r["proposed_ui_tab"] = default_tab

        # Infer proposed_anchors from target category's defaults
        # Use primary anchor only (first in the list), not the full
        # duplication set (e.g. actions;toys;outside)
        if "ANCHOR mismatch" in issues and not r["proposed_anchors"]:
            default_anchors = cat_to_anchors.get(target_cat, [])
            if default_anchors:
                primary_anchor = default_anchors[0]
                cur_anchor_set = set(a.strip() for a in cur_anchors.split(";") if a.strip())
                if primary_anchor not in cur_anchor_set:
                    r["proposed_anchors"] = primary_anchor

        # If we changed category, also check if tab and anchors need updating
        if r["proposed_category"] and r["proposed_category"] != cur_cat:
            new_default_tab = cat_to_tab.get(r["proposed_category"], "")
            new_default_anchors = cat_to_anchors.get(r["proposed_category"], [])

            if new_default_tab and new_default_tab != cur_tab and not r["proposed_ui_tab"]:
                if cur_tab != "core":
                    r["proposed_ui_tab"] = new_default_tab

            if new_default_anchors and not r["proposed_anchors"]:
                primary_anchor = new_default_anchors[0]
                cur_anchor_set = set(a.strip() for a in cur_anchors.split(";") if a.strip())
                if primary_anchor not in cur_anchor_set:
                    r["proposed_anchors"] = primary_anchor

    tier_order = {
        "Tier 1 - Phase I MVP": 1,
        "Tier 2 - Faison expansion": 2,
        "Tier 3 - Reference expansion": 3,
    }
    rows = sorted(
        review.values(),
        key=lambda r: (
            tier_order.get(r["priority_tier"], 99),
            r["issue_source"],
            r["canonical_term"].lower(),
        ),
    )

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)

    source_counts = {}
    for r in rows:
        s = r["issue_source"]
        source_counts[s] = source_counts.get(s, 0) + 1

    print(f"Review file written to {OUT_PATH}")
    print(f"  Total rows: {len(rows)}")
    for src, cnt in sorted(source_counts.items()):
        print(f"    {src}: {cnt}")


if __name__ == "__main__":
    main()
