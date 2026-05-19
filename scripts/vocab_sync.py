#!/usr/bin/env python3
"""
Bidirectional sync between vocabulary.json and the canonical CSV.

Commands:
  export   — vocabulary.json → CSV (team-reviewable flat file)
  diff     — show what changed between CSV and vocabulary.json
  import   — CSV → vocabulary.json (apply team edits back to the app)

Usage:
  python3 scripts/vocab_sync.py export                  # write CSV from JSON
  python3 scripts/vocab_sync.py diff                    # show differences
  python3 scripts/vocab_sync.py import                  # dry-run import
  python3 scripts/vocab_sync.py import --apply          # write changes to vocabulary.json

The CSV is the team-facing artifact (Joannalyn, Gabby review here).
vocabulary.json is the app-facing artifact (what the app loads).
"""

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VOCAB_PATH = REPO / "vocabulary.json"
CSV_PATH = REPO / "data" / "canonical_vocabulary.csv"

CSV_COLUMNS = [
    "canonical_term", "display_label", "type", "category", "source",
    "source_detail", "priority_tier", "core_or_fringe", "part_of_speech",
    "phrase_pos", "ui_tab", "secondary_tabs", "intent_tags", "scenario_tags",
    "allowed_for_generation", "allowed_for_grid", "requires_personalization",
    "synonyms_or_variants", "phrase_templates", "notes",
]

TIER_TO_INT = {
    "Tier 1 - Phase I MVP": 1,
    "Tier 2 - Faison expansion": 2,
    "Tier 3 - Reference expansion": 3,
}
INT_TO_TIER = {v: k for k, v in TIER_TO_INT.items()}

SYNC_FIELDS = ["display_label", "part_of_speech", "phrase_pos", "ui_tab", "category", "secondary_tabs"]

# CSV column name → JSON field name when they differ
CSV_TO_JSON_FIELD = {
    "category": "category_xls",
    "secondary_tabs": "additional_tabs",
}


def normalize_quotes(s: str) -> str:
    if not isinstance(s, str):
        return s
    return s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')


def load_vocab():
    with open(VOCAB_PATH) as f:
        return json.load(f)


def load_csv():
    rows = {}
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ct = row.get("canonical_term", "").strip()
            if ct:
                rows[ct] = row
    return rows


def sym_to_csv_row(sym):
    tier = sym.get("priority_tier", 3)
    sources = sym.get("sources", [])
    return {
        "canonical_term": normalize_quotes(sym.get("canonical_term", "")),
        "display_label": normalize_quotes(sym.get("display_label", "")),
        "type": sym.get("type", "word"),
        "category": sym.get("category_xls", ""),
        "source": "; ".join(sources) if isinstance(sources, list) else str(sources or ""),
        "source_detail": "",
        "priority_tier": INT_TO_TIER.get(tier, f"Tier {tier}"),
        "core_or_fringe": sym.get("core_or_fringe", ""),
        "part_of_speech": sym.get("part_of_speech", ""),
        "phrase_pos": sym.get("phrase_pos", ""),
        "ui_tab": sym.get("ui_tab", ""),
        "intent_tags": "; ".join(sym.get("intent_tags", [])) if isinstance(sym.get("intent_tags"), list) else "",
        "scenario_tags": "; ".join(sym.get("scenario_tags", [])) if isinstance(sym.get("scenario_tags"), list) else "",
        "allowed_for_generation": "Yes" if sym.get("allowed_for_generation") else "No",
        "allowed_for_grid": "Yes" if sym.get("allowed_for_grid") else "No",
        "requires_personalization": "Yes" if sym.get("requires_personalization") else "No",
        "synonyms_or_variants": (
            "; ".join(sym["synonyms_or_variants"]) if isinstance(sym.get("synonyms_or_variants"), list)
            else normalize_quotes(sym.get("synonyms_or_variants") or "")
        ),
        "phrase_templates": (
            "; ".join(sym["phrase_templates"]) if isinstance(sym.get("phrase_templates"), list)
            else (sym.get("phrase_templates") or "")
        ),
        "notes": sym.get("notes") or "",
        "secondary_tabs": "; ".join(sym["additional_tabs"]) if isinstance(sym.get("additional_tabs"), list) else (sym.get("additional_tabs") or ""),
    }


def cmd_export():
    vocab = load_vocab()
    syms = vocab["symbols"]

    rows = [sym_to_csv_row(s) for s in syms]
    rows.sort(key=lambda r: (
        TIER_TO_INT.get(r["priority_tier"], 99),
        r["canonical_term"].lower(),
    ))

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} symbols to {CSV_PATH}")


def cmd_diff():
    vocab = load_vocab()
    csv_rows = load_csv()

    live_by_term = {
        normalize_quotes(s.get("canonical_term", "").strip()): s
        for s in vocab["symbols"]
        if s.get("canonical_term")
    }

    csv_terms = set(csv_rows.keys())
    live_terms = set(live_by_term.keys())

    in_csv_only = csv_terms - live_terms
    in_live_only = live_terms - csv_terms
    shared = csv_terms & live_terms

    if in_csv_only:
        print(f"In CSV only ({len(in_csv_only)}):")
        for ct in sorted(in_csv_only):
            print(f"  + {ct}")
        print()

    if in_live_only:
        print(f"In vocabulary.json only ({len(in_live_only)}):")
        for ct in sorted(in_live_only):
            print(f"  - {ct}")
        print()

    diffs = []
    for ct in sorted(shared):
        csv_row = csv_rows[ct]
        sym = live_by_term[ct]
        field_diffs = []

        for field in SYNC_FIELDS:
            json_field = CSV_TO_JSON_FIELD.get(field, field)

            if field == "secondary_tabs":
                csv_raw = normalize_quotes(csv_row.get(field, "").strip())
                csv_list = [t.strip() for t in csv_raw.split(";") if t.strip()] if csv_raw else []
                live_val = sym.get(json_field, [])
                if not isinstance(live_val, list):
                    live_val = [live_val] if live_val else []
                if csv_list != live_val:
                    field_diffs.append((field, str(csv_list), str(live_val)))
                continue

            csv_val = normalize_quotes(csv_row.get(field, "").strip())
            live_val = sym.get(json_field, "")
            live_val = normalize_quotes(str(live_val)).strip() if live_val else ""

            if csv_val != live_val:
                field_diffs.append((field, csv_val, live_val))

        if field_diffs:
            diffs.append((ct, field_diffs))

    if diffs:
        print(f"Field differences ({len(diffs)} symbols):")
        for ct, fd in diffs:
            print(f"  {ct}:")
            for field, csv_val, live_val in fd:
                print(f"    {field}: CSV=\"{csv_val}\" vs JSON=\"{live_val}\"")
        print()
    else:
        print("No field differences on synced fields.")

    print(f"Summary: {len(in_csv_only)} CSV-only, {len(in_live_only)} JSON-only, {len(diffs)} field diffs")


def cmd_import(apply=False):
    vocab = load_vocab()
    csv_rows = load_csv()

    live_by_term = {}
    for s in vocab["symbols"]:
        ct = normalize_quotes(s.get("canonical_term", "").strip())
        if ct:
            live_by_term[ct] = s

    changes = []
    for ct, csv_row in sorted(csv_rows.items()):
        sym = live_by_term.get(ct)
        if not sym:
            continue

        for field in SYNC_FIELDS:
            json_field = CSV_TO_JSON_FIELD.get(field, field)
            csv_raw = normalize_quotes(csv_row.get(field, "").strip())

            # secondary_tabs is stored as "tab1; tab2" in CSV, list in JSON
            if field == "secondary_tabs":
                csv_list = [t.strip() for t in csv_raw.split(";") if t.strip()] if csv_raw else []
                live_val = sym.get(json_field, [])
                if not isinstance(live_val, list):
                    live_val = [live_val] if live_val else []
                if csv_list != live_val:
                    changes.append((ct, sym["id"], field, str(live_val), str(csv_list)))
                    if apply:
                        sym[json_field] = csv_list
                continue

            csv_val = csv_raw
            live_val = sym.get(json_field, "")
            live_val = normalize_quotes(str(live_val)).strip() if live_val else ""

            if csv_val != live_val:
                changes.append((ct, sym["id"], field, live_val, csv_val))
                if apply:
                    sym[json_field] = csv_val

    if changes:
        print(f"Changes to apply ({len(changes)}):")
        for ct, sid, field, old, new in changes:
            print(f"  {sid:30s} {field}: \"{old}\" → \"{new}\"")
    else:
        print("No changes to apply — CSV and vocabulary.json are in sync.")

    if apply and changes:
        with open(VOCAB_PATH, "w") as f:
            json.dump(vocab, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\nvocabulary.json updated with {len(changes)} changes.")
    elif changes:
        print(f"\nDRY RUN — pass --apply to write {len(changes)} changes.")


def main():
    if len(sys.argv) < 2:
        print("Usage: vocab_sync.py {export|diff|import} [--apply]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "export":
        cmd_export()
    elif cmd == "diff":
        cmd_diff()
    elif cmd == "import":
        cmd_import(apply="--apply" in sys.argv)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
