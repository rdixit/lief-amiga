#!/usr/bin/env python3
"""
Backpropagate edits from data/vocabulary_union_table.csv into:
  1. data/canonical_vocabulary.csv  (category, ui_tab, secondary_tabs, part_of_speech, phrase_pos)
  2. meaning_room.json              (anchor membership)

The union table is the "validation sweep" artifact — the user edits it in Excel,
exports to CSV, then runs this script to fan changes out to the canonical stores.

Multi-value ui_tab (e.g. "actions;things") is split:
  - first value  → ui_tab (primary)
  - remaining    → secondary_tabs (semicolon-separated)

Usage:
  python3 scripts/backprop_union_table.py                # dry run — show all changes
  python3 scripts/backprop_union_table.py --apply        # write changes to canonical CSV + meaning_room.json
"""

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UNION_PATH = REPO / "data" / "vocabulary_union_table.csv"
CANONICAL_PATH = REPO / "data" / "canonical_vocabulary.csv"
VOCAB_PATH = REPO / "vocabulary.json"
ROOM_PATH = REPO / "meaning_room.json"

# Fields we backprop from the union table into the canonical CSV.
# Union table column → canonical CSV column
BACKPROP_FIELDS = {
    "category_xls": "category",
    "current_pos": "part_of_speech",
    "phrase_pos": "phrase_pos",
}


def load_id_to_term():
    """Return {symbol_id: canonical_term} from vocabulary.json."""
    with open(VOCAB_PATH) as f:
        vocab = json.load(f)
    return {s["id"]: s.get("canonical_term", "").strip() for s in vocab["symbols"]}


def load_union_table():
    """Return {symbol_id: row_dict} from the union table CSV. First occurrence wins."""
    rows = {}
    with open(UNION_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sid = row.get("symbol_id", "").strip()
            if sid and sid not in rows:
                rows[sid] = row
    return rows


def load_canonical():
    """Return (fieldnames, {canonical_term: row_dict}) from canonical CSV."""
    rows = {}
    with open(CANONICAL_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for row in reader:
            ct = row.get("canonical_term", "").strip()
            if ct:
                rows[ct] = row
    return fieldnames, rows


def split_ui_tab(raw_tab):
    """Split 'actions;things' → ('actions', 'things') or ('actions', '')."""
    parts = [p.strip() for p in raw_tab.split(";") if p.strip()]
    primary = parts[0] if parts else ""
    secondary = "; ".join(parts[1:]) if len(parts) > 1 else ""
    return primary, secondary


def diff_canonical(union_rows, canonical_rows, id_to_term):
    """
    Compare union table edits against canonical CSV.
    Returns list of (canonical_term, field, old_val, new_val) tuples.
    """
    changes = []

    for sid, urow in union_rows.items():
        ct = id_to_term.get(sid)
        if not ct or ct not in canonical_rows:
            continue

        crow = canonical_rows[ct]

        # Backprop simple fields
        for ucol, ccol in BACKPROP_FIELDS.items():
            new_val = urow.get(ucol, "").strip()
            old_val = crow.get(ccol, "").strip()
            if new_val and new_val != old_val:
                changes.append((ct, ccol, old_val, new_val))

        # Backprop ui_tab (split multi-value)
        raw_tab = urow.get("ui_tab", "").strip()
        if raw_tab:
            primary, secondary = split_ui_tab(raw_tab)
            old_primary = crow.get("ui_tab", "").strip()
            old_secondary = crow.get("secondary_tabs", "").strip()

            if primary and primary != old_primary:
                changes.append((ct, "ui_tab", old_primary, primary))
            if secondary != old_secondary:
                changes.append((ct, "secondary_tabs", old_secondary, secondary))

    return changes


def diff_anchors(union_rows):
    """
    Compare union table anchor edits against meaning_room.json.
    Returns (anchors_to_add, anchors_to_remove) where each is
    list of (anchor_id, symbol_id) tuples.
    """
    with open(ROOM_PATH) as f:
        room = json.load(f)

    current = {}  # anchor_id → set of symbol_ids
    for a in room["anchors"]:
        current[a["id"]] = set(a["symbol_ids"])

    desired = {}  # anchor_id → set of symbol_ids
    for anchor_id in current:
        desired[anchor_id] = set()

    for sid, urow in union_rows.items():
        raw_anchors = urow.get("meaning_room_anchors", "").strip()
        if not raw_anchors:
            continue
        for aid in raw_anchors.split(";"):
            aid = aid.strip()
            if aid:
                desired.setdefault(aid, set()).add(sid)

    # Also keep existing membership for symbols NOT in the union table
    all_union_sids = set(union_rows.keys())
    for aid, sids in current.items():
        for sid in sids:
            if sid not in all_union_sids:
                desired.setdefault(aid, set()).add(sid)

    to_add = []
    to_remove = []
    for aid in sorted(set(list(current.keys()) + list(desired.keys()))):
        cur = current.get(aid, set())
        des = desired.get(aid, set())
        for sid in sorted(des - cur):
            to_add.append((aid, sid))
        for sid in sorted(cur - des):
            to_remove.append((aid, sid))

    return to_add, to_remove


def apply_canonical(changes, canonical_rows, fieldnames):
    """Write changes to canonical CSV."""
    if "secondary_tabs" not in fieldnames:
        fieldnames.append("secondary_tabs")

    for ct, field, old_val, new_val in changes:
        if ct in canonical_rows:
            canonical_rows[ct][field] = new_val

    # Write in canonical_term sorted order
    all_rows = []
    with open(CANONICAL_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ct = row.get("canonical_term", "").strip()
            if ct in canonical_rows:
                all_rows.append(canonical_rows[ct])
            else:
                all_rows.append(row)

    with open(CANONICAL_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)


def apply_anchors(to_add, to_remove):
    """Update meaning_room.json with anchor membership changes."""
    with open(ROOM_PATH) as f:
        room = json.load(f)

    add_map = {}
    for aid, sid in to_add:
        add_map.setdefault(aid, set()).add(sid)
    remove_map = {}
    for aid, sid in to_remove:
        remove_map.setdefault(aid, set()).add(sid)

    for anchor in room["anchors"]:
        aid = anchor["id"]
        sids = list(anchor["symbol_ids"])
        if aid in remove_map:
            sids = [s for s in sids if s not in remove_map[aid]]
        if aid in add_map:
            existing = set(sids)
            for s in sorted(add_map[aid]):
                if s not in existing:
                    sids.append(s)
        anchor["symbol_ids"] = sids

    with open(ROOM_PATH, "w") as f:
        json.dump(room, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    apply = "--apply" in sys.argv

    id_to_term = load_id_to_term()
    union_rows = load_union_table()
    fieldnames, canonical_rows = load_canonical()

    # --- Canonical CSV changes ---
    changes = diff_canonical(union_rows, canonical_rows, id_to_term)

    if changes:
        print(f"Canonical CSV changes ({len(changes)}):")
        by_field = {}
        for ct, field, old, new in changes:
            by_field.setdefault(field, []).append((ct, old, new))
        for field in sorted(by_field):
            items = by_field[field]
            print(f"\n  {field} ({len(items)} changes):")
            for ct, old, new in items[:20]:
                print(f"    {ct:35s}  {old!r:30s} → {new!r}")
            if len(items) > 20:
                print(f"    ... and {len(items) - 20} more")
    else:
        print("No canonical CSV changes detected.")

    # --- Anchor changes ---
    to_add, to_remove = diff_anchors(union_rows)

    if to_add or to_remove:
        print(f"\nMeaning room anchor changes:")
        if to_add:
            print(f"  Add ({len(to_add)}):")
            for aid, sid in to_add[:20]:
                print(f"    {aid:25s} ← {sid}")
            if len(to_add) > 20:
                print(f"    ... and {len(to_add) - 20} more")
        if to_remove:
            print(f"  Remove ({len(to_remove)}):")
            for aid, sid in to_remove[:20]:
                print(f"    {aid:25s} ✕ {sid}")
            if len(to_remove) > 20:
                print(f"    ... and {len(to_remove) - 20} more")
    else:
        print("\nNo anchor changes detected.")

    # --- Apply ---
    if apply:
        if changes:
            apply_canonical(changes, canonical_rows, fieldnames)
            print(f"\nWrote {len(changes)} changes to {CANONICAL_PATH}")
        if to_add or to_remove:
            apply_anchors(to_add, to_remove)
            print(f"Updated anchors in {ROOM_PATH} (+{len(to_add)} / -{len(to_remove)})")
        if changes or to_add or to_remove:
            print(f"\nNext: run 'python3 scripts/vocab_sync.py import --apply' to push to vocabulary.json")
    else:
        total = len(changes) + len(to_add) + len(to_remove)
        if total:
            print(f"\nDRY RUN — {total} total changes. Pass --apply to write.")
        else:
            print("\nNothing to do — union table matches canonical stores.")


if __name__ == "__main__":
    main()
