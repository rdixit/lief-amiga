#!/usr/bin/env python3
"""
Build a union table joining vocabulary.json, meaning_room.json, and
pos_corrections.csv (archived) into a single CSV for cross-system collision review.

Usage:  python3 scripts/build_union_table.py

Output: data/vocabulary_union_table.csv
"""

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VOCAB_PATH = REPO / "vocabulary.json"
ROOM_PATH = REPO / "meaning_room.json"
CORRECTIONS_PATH = REPO / "data" / "_archive" / "pos_corrections.csv"
OUT_PATH = REPO / "data" / "vocabulary_union_table.csv"

sys.path.insert(0, str(REPO / "scripts"))
from category_utils import anchor_to_expected_tabs as _load_anchor_tabs

ANCHOR_TO_EXPECTED_TABS = _load_anchor_tabs()


def main():
    with open(VOCAB_PATH) as f:
        vocab = json.load(f)
    with open(ROOM_PATH) as f:
        room = json.load(f)

    corrections = {}
    if CORRECTIONS_PATH.exists():
        with open(CORRECTIONS_PATH, newline="") as f:
            for row in csv.DictReader(f):
                corrections[row["symbol_id"]] = row

    anchor_membership: dict[str, list[str]] = {}
    for a in room["anchors"]:
        for sid in a["symbol_ids"]:
            anchor_membership.setdefault(sid, []).append(a["id"])

    rows = []
    for sym in vocab["symbols"]:
        sid = sym["id"]
        tier = sym.get("priority_tier", 99)
        ui_tab = sym.get("ui_tab", "")
        pos = sym.get("part_of_speech", "")
        sym_type = sym.get("type", "")
        anchors = anchor_membership.get(sid, [])
        corr = corrections.get(sid, {})
        pre_correction_pos = corr.get("current_pos", pos)
        phrase_pos = sym.get("phrase_pos", corr.get("phrase_pos", ""))
        pos_changed = pre_correction_pos != pos

        flags = []

        # 1. tab-anchor mismatch
        for anchor_id in anchors:
            expected_tabs = ANCHOR_TO_EXPECTED_TABS.get(anchor_id, set())
            if expected_tabs and ui_tab not in expected_tabs:
                flags.append(f"tab-anchor-mismatch({anchor_id}→expects:{','.join(sorted(expected_tabs))})")

        # 2. pos-type mismatch: phrase type but POS not phrase
        if sym_type == "phrase" and pos != "phrase":
            flags.append(f"pos-type-mismatch(type=phrase,pos={pos})")

        # 3. orphan T1-T2
        if tier <= 2 and not anchors:
            flags.append("orphan-tier-1-2")

        rows.append({
            "symbol_id": sid,
            "display_label": sym.get("display_label", ""),
            "priority_tier": tier,
            "type": sym_type,
            "category_xls": sym.get("category_xls", ""),
            "ui_tab": ui_tab,
            "meaning_room_anchors": ";".join(anchors),
            "pre_correction_pos": pre_correction_pos,
            "current_pos": pos,
            "phrase_pos": phrase_pos,
            "pos_changed": "Y" if pos_changed else "",
            "collision_flags": "; ".join(flags),
        })

    rows.sort(key=lambda r: (r["priority_tier"], r["ui_tab"], r["symbol_id"]))

    fieldnames = [
        "symbol_id", "display_label", "priority_tier", "type",
        "category_xls", "ui_tab", "meaning_room_anchors",
        "pre_correction_pos", "current_pos", "phrase_pos",
        "pos_changed", "collision_flags",
    ]
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    flagged = sum(1 for r in rows if r["collision_flags"])
    pos_changed = sum(1 for r in rows if r["pos_changed"])
    orphans = sum(1 for r in rows if "orphan" in r["collision_flags"])
    tab_anchor = sum(1 for r in rows if "tab-anchor" in r["collision_flags"])
    pos_type = sum(1 for r in rows if "pos-type" in r["collision_flags"])

    print(f"Union table written to {OUT_PATH}")
    print(f"  Total symbols:       {total}")
    print(f"  POS changed:         {pos_changed}")
    print(f"  Collision flags:     {flagged}")
    print(f"    tab-anchor:        {tab_anchor}")
    print(f"    pos-type:          {pos_type}")
    print(f"    orphan T1-T2:      {orphans}")
    print()

    if flagged:
        print("Flagged symbols:")
        for r in rows:
            if r["collision_flags"]:
                print(f"  T{r['priority_tier']} {r['symbol_id']:30s} tab:{r['ui_tab']:10s} MR:{r['meaning_room_anchors']:30s} | {r['collision_flags']}")


if __name__ == "__main__":
    main()
