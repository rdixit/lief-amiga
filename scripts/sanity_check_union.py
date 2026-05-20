#!/usr/bin/env python3
"""
Sanity-check the edited vocabulary_union_table.csv against category_config.csv.
Outputs data/union_table_issues.csv with all questionable rows and a reason flag.

Usage: python3 scripts/sanity_check_union.py
"""

import csv
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UNION_PATH = REPO / "data" / "vocabulary_union_table.csv"
OUT_PATH = REPO / "data" / "union_table_issues.csv"

sys.path.insert(0, str(REPO / "scripts"))
from category_utils import load_category_config

POS_REQUIRED_CAT = {
    "verb/action": {"Actions", "Function/Core"},
    "pronoun/person": {"People/Pronouns/Possessives"},
    "negation/repair": {"Negation/Repair"},
    "question word": {"Question Words"},
    "descriptor/adjective": {"Descriptors", "Feelings"},
}

NOUN_VALID_TABS = {"things", "people", "food", "core", "more"}
VERB_VALID_TABS = {"actions", "core", "more"}


def main():
    config = load_category_config()
    cat_to_tab = {cat: v["default_tab"] for cat, v in config.items()}
    cat_to_anchors = {cat: set(v["default_anchors"]) for cat, v in config.items()}

    issues = []
    seen_ids = {}
    row_count = 0

    with open(UNION_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row_count += 1
            sid = row.get("symbol_id", "").strip()
            cat = row.get("category_xls", "").strip()
            ui_tab_raw = row.get("ui_tab", "").strip()
            pos = row.get("current_pos", "").strip()
            phrase_pos = row.get("phrase_pos", "").strip()
            anchors_raw = row.get("meaning_room_anchors", "").strip()
            tier = row.get("priority_tier", "").strip()
            sym_type = row.get("type", "").strip()
            display = row.get("display_label", "").strip()

            tabs = [t.strip() for t in ui_tab_raw.split(";") if t.strip()]
            primary_tab = tabs[0] if tabs else ""
            anchors = [a.strip() for a in anchors_raw.split(";") if a.strip()]
            effective_pos = phrase_pos if sym_type == "phrase" and phrase_pos else pos

            flags = []

            # 1. Duplicate symbol_id
            if sid in seen_ids:
                flags.append(f"DUPLICATE symbol_id (also at row {seen_ids[sid]})")
            seen_ids[sid] = row_count

            # 2. Multi-value category (not supported)
            if ";" in cat:
                flags.append(f"MULTI-VALUE category_xls={cat!r} — system only supports single category")

            # 3. Unknown category
            if cat and cat not in config and ";" not in cat:
                flags.append(f"UNKNOWN category={cat!r} — not in category_config.csv")

            # 4. POS vs category mismatch
            if effective_pos in POS_REQUIRED_CAT:
                valid = POS_REQUIRED_CAT[effective_pos]
                if cat and ";" not in cat and cat not in valid:
                    flags.append(f"POS={effective_pos!r} expects category in {sorted(valid)} but got {cat!r}")

            # 5. Category vs primary tab mismatch
            if cat and primary_tab and cat in cat_to_tab:
                expected_tab = cat_to_tab[cat]
                all_tabs = set(tabs)
                if expected_tab not in all_tabs and primary_tab != expected_tab:
                    # Check if it's a known core-override pattern
                    if primary_tab == "core":
                        pass  # intentional core accessibility override
                    elif expected_tab == "food" and primary_tab == "things":
                        pass  # pre-Phase-2 food→things is ok
                    elif expected_tab == "describe" and primary_tab in ("more", "feelings"):
                        pass  # pre-Phase-2 describe→more/feelings is ok
                    else:
                        flags.append(f"TAB mismatch: cat={cat!r} expects tab={expected_tab!r} but got {primary_tab!r}")

            # 6. Anchor vs category mismatch (T1-T2 only)
            if tier in ("1", "2") and anchors and cat in cat_to_anchors:
                expected_anchors = cat_to_anchors[cat]
                symbol_anchors = set(anchors)
                # At least one anchor should overlap with expected
                if expected_anchors and not symbol_anchors.intersection(expected_anchors):
                    # Allow verb duplication (actions verbs in contextual anchors)
                    if cat == "Actions" and effective_pos == "verb/action":
                        pass
                    elif cat == "Social" and "other_people" in symbol_anchors:
                        pass
                    elif cat == "Social" and "actions" in symbol_anchors:
                        pass
                    else:
                        flags.append(
                            f"ANCHOR mismatch: cat={cat!r} expects anchor in {sorted(expected_anchors)} "
                            f"but has {sorted(symbol_anchors)}"
                        )

            # 7. Noun-like POS but in actions tab (suspicious)
            if pos == "noun" and primary_tab == "actions" and sym_type == "word":
                flags.append(f"NOUN in actions tab — should this be Preferred Items/Places/etc?")

            # 8. verb/action POS but in things/people tab for words (not phrases)
            if pos == "verb/action" and primary_tab in ("things", "people") and sym_type == "word":
                flags.append(f"VERB in {primary_tab!r} tab — POS might be wrong (should be noun?)")

            # 9. Blank category
            if not cat:
                flags.append("BLANK category_xls")

            # 10. Blank ui_tab
            if not primary_tab:
                flags.append("BLANK ui_tab")

            # 11. Blank POS
            if not pos:
                flags.append("BLANK current_pos")

            # 12. location/preposition POS with wrong category
            if pos == "location/preposition" and cat not in {"Function/Core", "Places", "Descriptors"}:
                flags.append(f"location/preposition POS with cat={cat!r} — should be Function/Core, Places, or Descriptors")

            # 13. Phrase type but POS is not 'phrase'
            if sym_type == "phrase" and pos != "phrase":
                flags.append(f"type=phrase but POS={pos!r} (expected 'phrase')")

            if flags:
                issues.append({
                    "symbol_id": sid,
                    "display_label": display,
                    "priority_tier": tier,
                    "type": sym_type,
                    "category_xls": cat,
                    "current_pos": pos,
                    "phrase_pos": phrase_pos,
                    "ui_tab": ui_tab_raw,
                    "meaning_room_anchors": anchors_raw,
                    "issues": " | ".join(flags),
                })

    fieldnames = [
        "symbol_id", "display_label", "priority_tier", "type",
        "category_xls", "current_pos", "phrase_pos",
        "ui_tab", "meaning_room_anchors", "issues",
    ]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(issues)

    # Summary
    issue_types = Counter()
    for row in issues:
        for flag in row["issues"].split(" | "):
            key = flag.split(":")[0].split("=")[0].split("(")[0].strip()
            issue_types[key] += 1

    print(f"Sanity check complete: {len(issues)} symbols with issues out of {row_count}")
    print(f"Output: {OUT_PATH}")
    print()
    print("Issue breakdown:")
    for itype, count in issue_types.most_common():
        print(f"  {count:4d}  {itype}")


if __name__ == "__main__":
    main()
