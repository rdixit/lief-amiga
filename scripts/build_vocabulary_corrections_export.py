#!/usr/bin/env python3
"""
Rebuild data/vocabulary_category_corrections.csv from vocabulary.json joined to the
canonical expansion-packet CSV. One row per symbol where tab or POS differs from the
spreadsheet-derived baseline, plus rows for vocab-only additions.

Run from repo root: python3 scripts/build_vocabulary_corrections_export.py

Default canonical path matches the project's Google Drive export; override with CANONICAL_CSV env.
"""

import csv
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VOCAB_PATH = REPO / "vocabulary.json"
OUT_PATH = REPO / "data" / "vocabulary_category_corrections.csv"
DEFAULT_CANONICAL = Path(
    os.environ.get(
        "CANONICAL_CSV",
        "/Users/mpesavento/Library/CloudStorage/GoogleDrive-mjpesavento@gmail.com/"
        "My Drive/work/Lief-AMIGA-AAC/data/"
        "AMIGA_AAC_Vocabulary_Expansion_Packet_4.5.2026_canonical_vocabulary.csv",
    )
)

CAT_TO_TAB = {
    "Actions": "actions",
    "Social": "core",
    "Feelings": "feelings",
    "People/Pronouns/Possessives": "people",
    "Places": "things",
    "Preferred Items": "things",
    "Body Parts": "things",
    "Food/Drink": "things",
    "Clothing": "things",
    "Vehicles": "things",
    "Descriptors": "more",
    "Negation/Repair": "more",
    "Function/Core": "more",
    "Question Words": "more",
    "Regulation/Safety": "core",
    "Uncategorized": "more",
}


def main():
    canonical = {}
    with open(DEFAULT_CANONICAL, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ct = row["canonical_term"].strip()
            if ct:
                canonical[ct] = row

    with open(VOCAB_PATH, encoding="utf-8") as f:
        vocab = json.load(f)

    rows_out = []

    used_csv_terms = set()

    for sym in vocab["symbols"]:
        cid = sym.get("id")
        ct = (sym.get("canonical_term") or "").strip()
        if not cid:
            continue

        # Vocab additions (canonical_term not present in spreadsheet export).
        if not ct or ct not in canonical:
            if ct not in canonical and sym.get(
                "id"
            ) in (
                "feel",
                "food",
                "school",
                "thank_you",
                "he_she",
            ):
                rows_out.append(
                    {
                        "symbol_id": cid,
                        "canonical_term": ct or cid.replace("_", " "),
                        "display_label": sym.get("display_label", ""),
                        "priority_tier": sym.get("priority_tier", ""),
                        "spreadsheet_category": "",
                        "spreadsheet_part_of_speech": "",
                        "inferred_ui_tab_from_spreadsheet_category": "",
                        "corrected_ui_tab": sym.get("ui_tab", ""),
                        "corrected_part_of_speech": sym.get(
                            "part_of_speech",
                            "",
                        ),
                        "change_kind": "vocab_only_addition",
                        "notes": "Restored or added for Phase I AAC grid; add this row to the canonical spreadsheet.",
                    }
                )
            continue

        used_csv_terms.add(ct)
        c_row = canonical[ct]
        src_cat = c_row["category"].strip()
        src_pos = c_row["part_of_speech"].strip()
        inferred = CAT_TO_TAB.get(src_cat)
        ui = sym.get("ui_tab")
        pos = sym.get("part_of_speech", "")

        tab_diff = inferred and inferred != ui
        pos_diff = src_pos != pos

        if not tab_diff and not pos_diff:
            continue

        parts = []
        if tab_diff:
            parts.append(f"tab {inferred} → {ui}")
        if pos_diff:
            parts.append(f"POS '{src_pos}' → '{pos}'")

        rows_out.append(
            {
                "symbol_id": cid,
                "canonical_term": ct,
                "display_label": sym.get("display_label", ""),
                "priority_tier": sym.get("priority_tier", ""),
                "spreadsheet_category": src_cat,
                "spreadsheet_part_of_speech": src_pos,
                "inferred_ui_tab_from_spreadsheet_category": inferred or "",
                "corrected_ui_tab": ui or "",
                "spreadsheet_part_of_speech_was": src_pos,
                "corrected_part_of_speech": pos or "",
                "change_kind": "tab_and_pos"
                if (tab_diff and pos_diff)
                else ("tab" if tab_diff else "pos"),
                "notes": "; ".join(parts),
            }
        )

    # Spreadsheet rows with no vocab symbol keyed by canonical_term (data drift).
    csv_orphans = sorted(set(canonical.keys()) - used_csv_terms)
    orphan_notes = ""
    if csv_orphans:
        orphan_notes = (
            "| CSV canonical_term rows not matched via vocabulary canonical_term: "
            + ", ".join(csv_orphans)
        )

    rows_out.sort(
        key=lambda r: (
            r["change_kind"] == "vocab_only_addition",
            r["symbol_id"] or "",
        )
    )

    fieldnames = [
        "symbol_id",
        "canonical_term",
        "display_label",
        "priority_tier",
        "spreadsheet_category",
        "spreadsheet_part_of_speech",
        "inferred_ui_tab_from_spreadsheet_category",
        "corrected_ui_tab",
        "spreadsheet_part_of_speech_was",
        "corrected_part_of_speech",
        "change_kind",
        "notes",
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows_out:
            w.writerow(r)

    print(f"Wrote {len(rows_out)} correction rows → {OUT_PATH}")
    print(f"Spreadsheet canonical terms not linked from vocabulary.json ({len(csv_orphans)}): {csv_orphans}")
    if orphan_notes:
        marker = OUT_PATH.with_name("vocabulary_correction_orphans_note.txt")
        marker.write_text(orphan_notes + "\n", encoding="utf-8")
        print(f"Wrote orphan note → {marker}")
    else:
        # Remove stale note file if exists
        marker = OUT_PATH.with_name("vocabulary_correction_orphans_note.txt")
        if marker.exists():
            marker.unlink()


if __name__ == "__main__":
    main()
