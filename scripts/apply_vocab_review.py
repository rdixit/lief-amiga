#!/usr/bin/env python3
"""
Apply marked rows from data/vocab_review.csv to:
  1. data/canonical_vocabulary.csv  (category, ui_tab, secondary_tabs, part_of_speech)
  2. meaning_room.json               (anchor membership)

Rules:
  - Rows with action ∈ {"apply", "modify"} are actionable.
  - Rows with action == "skip" are ignored.
  - For each actionable row, each proposed_* column triggers a change only when:
      (a) the proposed value is non-empty, AND
      (b) it differs from the *current canonical state* (not the row's "current_*"
          column, which can drift from canonical).

Anchor edits use vocabulary.json to resolve canonical_term → symbol_id, then
overwrite that symbol's membership: it is removed from all anchors it currently
belongs to and added to each anchor in proposed_anchors (semicolon-separated).

Usage:
  python3 scripts/apply_vocab_review.py            # dry run
  python3 scripts/apply_vocab_review.py --apply    # write changes
"""

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REVIEW_PATH = REPO / "data" / "vocab_review.csv"
CANONICAL_PATH = REPO / "data" / "canonical_vocabulary.csv"
VOCAB_PATH = REPO / "vocabulary.json"
ROOM_PATH = REPO / "meaning_room.json"

ACTIONABLE = {"apply", "modify"}

# vocab_review column → canonical CSV column
FIELD_MAP = {
    "proposed_category": "category",
    "proposed_ui_tab": "ui_tab",
    "proposed_secondary_tabs": "secondary_tabs",
    "proposed_pos": "part_of_speech",
}


def load_review():
    with open(REVIEW_PATH, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_canonical():
    rows = []
    by_term = {}
    with open(CANONICAL_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for row in reader:
            rows.append(row)
            ct = row.get("canonical_term", "").strip()
            if ct:
                by_term[ct] = row
    if "secondary_tabs" not in fieldnames:
        fieldnames.append("secondary_tabs")
    return fieldnames, rows, by_term


def load_term_to_symbol_id():
    with open(VOCAB_PATH) as f:
        vocab = json.load(f)
    mapping = {}
    for s in vocab["symbols"]:
        ct = s.get("canonical_term", "").strip()
        if ct:
            mapping[ct] = s["id"]
    return mapping


def normalize_anchor_str(s):
    return [a.strip() for a in s.split(";") if a.strip()]


def diff_changes(review, canonical_by_term, term_to_sid):
    """
    Returns (csv_changes, anchor_changes, warnings):
      csv_changes: list of (canonical_term, field, old, new)
      anchor_changes: list of (canonical_term, symbol_id, old_anchors_set, new_anchors_set)
      warnings: list of strings
    """
    csv_changes = []
    anchor_changes = []
    warnings = []

    for r in review:
        action = (r.get("action") or "").strip().lower()
        if action not in ACTIONABLE:
            continue

        ct = (r.get("canonical_term") or "").strip()
        if not ct:
            continue
        crow = canonical_by_term.get(ct)
        if not crow:
            warnings.append(f"[skip] canonical_term not found in canonical CSV: {ct!r}")
            continue

        for proposed_col, canonical_col in FIELD_MAP.items():
            new_val = (r.get(proposed_col) or "").strip()
            if not new_val:
                continue
            old_val = (crow.get(canonical_col) or "").strip()
            if new_val != old_val:
                csv_changes.append((ct, canonical_col, old_val, new_val))

        proposed_anchors_raw = (r.get("proposed_anchors") or "").strip()
        if proposed_anchors_raw:
            sid = term_to_sid.get(ct)
            if not sid:
                warnings.append(
                    f"[anchor skip] no symbol_id for canonical_term {ct!r} "
                    f"(not in vocabulary.json yet) — anchor change deferred"
                )
                continue
            current_anchors_raw = (r.get("current_anchors") or "").strip()
            old_set = set(normalize_anchor_str(current_anchors_raw))
            new_set = set(normalize_anchor_str(proposed_anchors_raw))
            if old_set != new_set:
                anchor_changes.append((ct, sid, old_set, new_set))

    return csv_changes, anchor_changes, warnings


def apply_csv(csv_changes, canonical_by_term, fieldnames, rows):
    for ct, field, _old, new in csv_changes:
        if ct in canonical_by_term:
            canonical_by_term[ct][field] = new
    with open(CANONICAL_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def apply_anchors(anchor_changes):
    """
    Overwrite each affected symbol's anchor membership: remove from old_set anchors,
    add to new_set anchors. Only mutate anchors mentioned in either set.
    """
    if not anchor_changes:
        return
    with open(ROOM_PATH) as f:
        room = json.load(f)

    anchor_by_id = {a["id"]: a for a in room["anchors"]}

    for _ct, sid, old_set, new_set in anchor_changes:
        for aid in old_set - new_set:
            anchor = anchor_by_id.get(aid)
            if anchor and sid in anchor["symbol_ids"]:
                anchor["symbol_ids"] = [s for s in anchor["symbol_ids"] if s != sid]
        for aid in new_set - old_set:
            anchor = anchor_by_id.get(aid)
            if anchor is None:
                print(f"  WARNING: anchor {aid!r} not found in meaning_room.json "
                      f"(symbol {sid} not added)")
                continue
            if sid not in anchor["symbol_ids"]:
                anchor["symbol_ids"].append(sid)

    with open(ROOM_PATH, "w") as f:
        json.dump(room, f, indent=2, ensure_ascii=False)
        f.write("\n")


def print_summary(csv_changes, anchor_changes, warnings):
    if csv_changes:
        print(f"\nCanonical CSV changes ({len(csv_changes)}):")
        by_field: dict[str, list] = {}
        for ct, field, old, new in csv_changes:
            by_field.setdefault(field, []).append((ct, old, new))
        for field in sorted(by_field):
            items = by_field[field]
            print(f"\n  {field} ({len(items)} changes):")
            for ct, old, new in items:
                print(f"    {ct:32s}  {old!r:30s} -> {new!r}")
    else:
        print("\nNo canonical CSV changes.")

    if anchor_changes:
        print(f"\nAnchor membership changes ({len(anchor_changes)} symbols):")
        for ct, sid, old_set, new_set in anchor_changes:
            removed = sorted(old_set - new_set)
            added = sorted(new_set - old_set)
            parts = []
            if removed:
                parts.append(f"-{{{', '.join(removed)}}}")
            if added:
                parts.append(f"+{{{', '.join(added)}}}")
            print(f"    {ct:32s}  ({sid})  {' '.join(parts)}")
    else:
        print("\nNo anchor changes.")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")


def main():
    apply = "--apply" in sys.argv

    if not REVIEW_PATH.exists():
        print(f"ERROR: {REVIEW_PATH} not found")
        return 1

    review = load_review()
    fieldnames, rows, canonical_by_term = load_canonical()
    term_to_sid = load_term_to_symbol_id()

    action_counts: dict[str, int] = {}
    for r in review:
        a = (r.get("action") or "").strip().lower() or "(empty)"
        action_counts[a] = action_counts.get(a, 0) + 1
    print("Review row action breakdown:")
    for a, n in sorted(action_counts.items()):
        print(f"  {a}: {n}")

    csv_changes, anchor_changes, warnings = diff_changes(
        review, canonical_by_term, term_to_sid
    )

    print_summary(csv_changes, anchor_changes, warnings)

    if not (csv_changes or anchor_changes):
        print("\nNothing to do.")
        return 0

    if apply:
        if csv_changes:
            apply_csv(csv_changes, canonical_by_term, fieldnames, rows)
            print(f"\nWrote {len(csv_changes)} field changes to {CANONICAL_PATH}")
        if anchor_changes:
            apply_anchors(anchor_changes)
            print(f"Updated anchor membership for {len(anchor_changes)} symbols "
                  f"in {ROOM_PATH}")
        print(
            "\nNext steps:\n"
            "  1) python3 scripts/vocab_sync.py import --apply    "
            "# canonical CSV -> vocabulary.json\n"
            "  2) python3 scripts/build_union_table.py            "
            "# rebuild union table\n"
            "  3) python3 scripts/sanity_check_union.py           "
            "# check remaining issues\n"
            "  4) python3 scripts/backprop_union_table.py         "
            "# dry-run: union -> canonical should be empty"
        )
    else:
        total = len(csv_changes) + len(anchor_changes)
        print(f"\nDRY RUN — {total} total changes. Pass --apply to write.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
