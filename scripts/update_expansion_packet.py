#!/usr/bin/env python3
"""
Update the canonical expansion packet CSV to match current vocabulary.json state.

Applies:
  - POS corrections (from live vocabulary.json)
  - New symbols (12 additions: 5 orphan restores + 7 feelings expansion)
  - Removes 3 annotation rows that aren't real vocabulary
  - Adds phrase_pos column
  - Adds ui_tab column
  - Cleans up trailing blank rows and extra commas
  - Normalizes curly quotes to straight apostrophes

Usage:
  python3 scripts/update_expansion_packet.py          # dry-run
  python3 scripts/update_expansion_packet.py --apply   # write updated CSV
"""

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VOCAB_PATH = REPO / "vocabulary.json"
EXPANSION_PATH = Path(
    "/Users/mpesavento/src/lief-amiga/data/"
    "AMIGA_AAC_Vocabulary_Expansion_Packet_4.5.2026_canonical_vocabulary.csv"
)
OUT_PATH = REPO / "data" / "AMIGA_AAC_Vocabulary_Expansion_Packet_4.5.2026_canonical_vocabulary_updated.csv"

ANNOTATION_PREFIXES = [
    "could be specific to use quiet space",
    "preferred items (will vary",
    "snacks (will vary",
]

CANONICAL_COLUMNS = [
    "canonical_term", "display_label", "type", "category", "source",
    "source_detail", "priority_tier", "core_or_fringe", "part_of_speech",
    "phrase_pos", "ui_tab", "intent_tags", "scenario_tags",
    "allowed_for_generation", "allowed_for_grid", "requires_personalization",
    "synonyms_or_variants", "phrase_templates", "notes",
]

TIER_MAP = {
    1: "Tier 1 - Phase I MVP",
    2: "Tier 2 - Faison expansion",
    3: "Tier 3 - Reference expansion",
}


def is_annotation(term: str) -> bool:
    return any(term.lower().startswith(p.lower()) for p in ANNOTATION_PREFIXES)


def normalize_quotes(s: str) -> str:
    return s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')


def main():
    apply = "--apply" in sys.argv

    with open(VOCAB_PATH) as f:
        vocab = json.load(f)
    live_syms = {s.get("canonical_term", "").strip(): s for s in vocab["symbols"] if s.get("canonical_term")}

    # Read original expansion packet
    orig_rows = []
    with open(EXPANSION_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ct = row.get("canonical_term", "").strip()
            if ct:
                orig_rows.append(row)

    print(f"Original expansion packet: {len(orig_rows)} rows")

    # Remove annotations
    removed = []
    kept = []
    for row in orig_rows:
        ct = row["canonical_term"].strip()
        if is_annotation(ct):
            removed.append(ct)
        else:
            kept.append(row)
    print(f"Removed annotations: {len(removed)}")
    for r in removed:
        print(f"  - {r[:60]}...")

    # Update existing rows from live vocab
    updated_terms = set()
    pos_changes = 0
    tab_additions = 0
    quote_fixes = 0

    for row in kept:
        ct = row["canonical_term"].strip()
        sym = live_syms.get(ct)
        if not sym:
            continue
        updated_terms.add(ct)

        # Update POS
        live_pos = sym.get("part_of_speech", "")
        if row.get("part_of_speech", "").strip() != live_pos:
            row["part_of_speech"] = live_pos
            pos_changes += 1

        # Add phrase_pos
        row["phrase_pos"] = sym.get("phrase_pos", "")

        # Add ui_tab
        row["ui_tab"] = sym.get("ui_tab", "")
        tab_additions += 1

        # Update type
        row["type"] = sym.get("type", row.get("type", ""))

        # Normalize quotes in display_label
        old_label = row.get("display_label", "")
        new_label = normalize_quotes(old_label)
        if old_label != new_label:
            row["display_label"] = new_label
            quote_fixes += 1

        # Normalize quotes in canonical_term
        old_ct = row.get("canonical_term", "")
        new_ct = normalize_quotes(old_ct)
        if old_ct != new_ct:
            row["canonical_term"] = new_ct
            quote_fixes += 1

    print(f"Updated existing rows: {len(updated_terms)} (POS changes: {pos_changes}, quote fixes: {quote_fixes})")

    # Add new symbols not in expansion packet
    new_rows = []
    for ct, sym in sorted(live_syms.items()):
        if ct in updated_terms:
            continue
        tier = sym.get("priority_tier", 3)
        new_row = {
            "canonical_term": normalize_quotes(ct),
            "display_label": normalize_quotes(sym.get("display_label", "")),
            "type": sym.get("type", "word"),
            "category": sym.get("category_xls", ""),
            "source": "; ".join(sym.get("sources", [])) if sym.get("sources") else "Added post-export",
            "source_detail": "",
            "priority_tier": TIER_MAP.get(tier, f"Tier {tier}"),
            "core_or_fringe": sym.get("core_or_fringe", ""),
            "part_of_speech": sym.get("part_of_speech", ""),
            "phrase_pos": sym.get("phrase_pos", ""),
            "ui_tab": sym.get("ui_tab", ""),
            "intent_tags": "; ".join(sym.get("intent_tags", [])) if sym.get("intent_tags") else "",
            "scenario_tags": "; ".join(sym.get("scenario_tags", [])) if sym.get("scenario_tags") else "",
            "allowed_for_generation": "Yes" if sym.get("allowed_for_generation") else "No",
            "allowed_for_grid": "Yes" if sym.get("allowed_for_grid") else "No",
            "requires_personalization": "Yes" if sym.get("requires_personalization") else "No",
            "synonyms_or_variants": normalize_quotes(
                "; ".join(sym["synonyms_or_variants"]) if isinstance(sym.get("synonyms_or_variants"), list)
                else (sym.get("synonyms_or_variants") or "")
            ),
            "phrase_templates": "; ".join(sym.get("phrase_templates", [])) if sym.get("phrase_templates") else "",
            "notes": sym.get("notes", "") or "",
        }
        new_rows.append(new_row)
        kept.append(new_row)

    print(f"Added new symbols: {len(new_rows)}")
    for r in new_rows:
        print(f"  + {r['canonical_term']} ({r['priority_tier']})")

    # Sort: by tier, then alphabetical
    tier_order = {"Tier 1 - Phase I MVP": 1, "Tier 2 - Faison expansion": 2, "Tier 3 - Reference expansion": 3}
    kept.sort(key=lambda r: (
        tier_order.get(r.get("priority_tier", "").strip(), 99),
        r.get("canonical_term", "").strip().lower(),
    ))

    print(f"\nFinal row count: {len(kept)}")

    if apply:
        with open(OUT_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CANONICAL_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(kept)
        print(f"Written to {OUT_PATH}")
    else:
        print(f"DRY RUN — pass --apply to write to {OUT_PATH}")


if __name__ == "__main__":
    main()
