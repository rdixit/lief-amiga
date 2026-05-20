#!/usr/bin/env python3
"""Assign unanchored symbols to their semantically correct anchors.

Uses category_config defaults with semantic overrides for Actions verbs
and a perspective-based split for People/Pronouns.

Usage:
    python3 scripts/assign_t3_anchors.py          # dry-run (shows deltas)
    python3 scripts/assign_t3_anchors.py --apply  # writes meaning_room.json
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MR_PATH = ROOT / "meaning_room.json"
UNION_PATH = ROOT / "data" / "vocabulary_union_table.csv"
CONFIG_PATH = ROOT / "data" / "category_config.csv"

# Semantic overrides for Actions-category verbs
ACTIONS_OVERRIDES = {
    "food_drink": ["bite", "eating"],
    "outside": ["ride", "jumped", "jumping"],
    "toys": ["catch"],
    "cognition": ["remember", "hear"],
}

# People/Pronouns perspective split
SELF_PRONOUNS = {
    "ill", "im", "it", "its", "our", "ours", "us",
    "we", "we_ll", "we_re", "youll", "youre", "yours",
}
OTHER_PRONOUNS = {
    "people", "shes", "somebody", "someone",
    "they", "theyll", "theyre",
}


def load_category_config():
    config = {}
    with open(CONFIG_PATH) as f:
        for row in csv.DictReader(f):
            anchors = [a.strip() for a in row["default_anchors"].split(";") if a.strip()]
            config[row["category"]] = anchors
    return config


def main():
    apply = "--apply" in sys.argv

    mr = json.load(open(MR_PATH))
    ut = list(csv.DictReader(open(UNION_PATH)))
    config = load_category_config()

    anchor_ids = {a["id"] for a in mr["anchors"]}
    existing_members = {}
    for a in mr["anchors"]:
        existing_members[a["id"]] = set(a.get("symbol_ids", []))

    all_anchored = set()
    for members in existing_members.values():
        all_anchored.update(members)

    # Build override lookup for Actions
    action_override_map = {}
    for anchor, syms in ACTIONS_OVERRIDES.items():
        for s in syms:
            action_override_map[s] = anchor

    # Find unanchored symbols
    unanchored = [r for r in ut if r["symbol_id"] not in all_anchored]
    print(f"Unanchored symbols: {len(unanchored)}")

    # Route each symbol
    assignments = defaultdict(list)
    skipped = []

    for row in unanchored:
        sid = row["symbol_id"]
        cat = row["category_xls"]

        if cat == "Actions":
            if sid in action_override_map:
                target = action_override_map[sid]
            else:
                target = "actions"
            assignments[target].append(sid)

        elif cat == "People/Pronouns/Possessives":
            if sid in SELF_PRONOUNS:
                assignments["self"].append(sid)
            elif sid in OTHER_PRONOUNS:
                assignments["other_people"].append(sid)
            else:
                assignments["self"].append(sid)

        elif cat == "Question Words":
            assignments["cognition"].append(sid)

        elif cat == "Social":
            assignments["other_people"].append(sid)

        else:
            targets = config.get(cat, [])
            if not targets:
                skipped.append((sid, cat, "no default_anchors in config"))
                continue
            for t in targets:
                if t in anchor_ids:
                    assignments[t].append(sid)
                else:
                    skipped.append((sid, cat, f"anchor '{t}' not found"))

    # Print summary
    print("\n--- Assignment summary ---")
    for anchor in sorted(assignments.keys()):
        before = len(existing_members.get(anchor, set()))
        added = len(assignments[anchor])
        print(f"  {anchor:25s}: +{added:3d} (was {before}, now {before + added})")

    if skipped:
        print(f"\n--- Skipped ({len(skipped)}) ---")
        for sid, cat, reason in skipped:
            print(f"  {sid}: {reason}")

    total_assigned = sum(len(v) for v in assignments.values())
    print(f"\nTotal assigned: {total_assigned}")
    print(f"Total skipped:  {len(skipped)}")

    if not apply:
        print("\nDry run — use --apply to write changes.")
        return

    # Apply to meaning_room.json
    for anchor in mr["anchors"]:
        if anchor["id"] in assignments:
            current = anchor.get("symbol_ids", [])
            anchor["symbol_ids"] = current + sorted(assignments[anchor["id"]])

    with open(MR_PATH, "w") as f:
        json.dump(mr, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\nChanges written to meaning_room.json")


if __name__ == "__main__":
    main()
