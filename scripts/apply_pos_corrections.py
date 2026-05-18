#!/usr/bin/env python3
"""
Apply POS corrections from data/_archive/pos_corrections.csv to vocabulary.json.

Usage:
  python3 scripts/apply_pos_corrections.py          # dry-run (print changes)
  python3 scripts/apply_pos_corrections.py --apply   # write changes to vocabulary.json
"""

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VOCAB_PATH = REPO / "vocabulary.json"
CORRECTIONS_PATH = REPO / "data" / "_archive" / "pos_corrections.csv"

COMPOUND_NOUNS = {"play_doh", "toygame", "tummystomach", "waterjuice"}


def main():
    apply = "--apply" in sys.argv

    with open(CORRECTIONS_PATH, newline="") as f:
        corrections = {row["symbol_id"]: row for row in csv.DictReader(f)}

    with open(VOCAB_PATH) as f:
        vocab = json.load(f)

    sym_index = {s["id"]: s for s in vocab["symbols"]}

    stats = {"pos_changed": 0, "phrase_pos_added": 0, "type_fixed": 0, "not_found": 0}
    changes = []

    for sid, corr in sorted(corrections.items()):
        sym = sym_index.get(sid)
        if not sym:
            stats["not_found"] += 1
            changes.append(f"  MISSING {sid}")
            continue

        old_pos = sym.get("part_of_speech", "")
        new_pos = corr["corrected_pos"]
        phrase_pos = corr["phrase_pos"]

        if old_pos != new_pos:
            sym["part_of_speech"] = new_pos
            stats["pos_changed"] += 1
            changes.append(
                f"  T{sym.get('priority_tier','?')} {sid:30s} POS: {old_pos:25s} -> {new_pos}"
            )

        if phrase_pos:
            sym["phrase_pos"] = phrase_pos
            stats["phrase_pos_added"] += 1

        if sid in COMPOUND_NOUNS:
            old_type = sym.get("type", "")
            old_is_phrase = sym.get("is_phrase", False)
            if old_type == "phrase" or old_is_phrase:
                sym["type"] = "word"
                sym["is_phrase"] = False
                sym.pop("phrase_pos", None)
                stats["type_fixed"] += 1
                changes.append(
                    f"  T{sym.get('priority_tier','?')} {sid:30s} type: phrase -> word"
                )

    print(f"POS corrections loaded: {len(corrections)}")
    print(f"POS changed:       {stats['pos_changed']}")
    print(f"phrase_pos added:   {stats['phrase_pos_added']}")
    print(f"type phrase->word:  {stats['type_fixed']}")
    print(f"Not found:          {stats['not_found']}")
    print()

    for tier in [1, 2, 3]:
        tier_changes = [
            c for c in changes if f"T{tier}" in c
        ]
        if tier_changes:
            print(f"Tier {tier} ({len(tier_changes)} changes):")
            for c in tier_changes:
                print(c)
            print()

    if apply:
        with open(VOCAB_PATH, "w") as f:
            json.dump(vocab, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("vocabulary.json UPDATED.")
    else:
        print("DRY RUN — pass --apply to write changes.")


if __name__ == "__main__":
    main()
