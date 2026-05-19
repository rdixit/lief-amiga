#!/usr/bin/env python3
"""
Shared helpers for reading data/category_config.csv.

All scripts that need category → tab or category → anchor mappings
should import from here instead of hardcoding the dicts.
"""

import csv
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO / "data" / "category_config.csv"


def load_category_config(path=None):
    """
    Return {category: {default_tab, default_anchors, subtab_label, notes}}.

    default_anchors is a list (multi-value field separated by '; ' in the CSV).
    """
    config = {}
    config_path = Path(path) if path else CONFIG_PATH
    with open(config_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cat = row["category"].strip()
            if not cat:
                continue
            anchors_raw = row.get("default_anchors", "").strip()
            anchors = [a.strip() for a in anchors_raw.split(";") if a.strip()]
            config[cat] = {
                "default_tab": row.get("default_tab", "").strip(),
                "default_anchors": anchors,
                "subtab_label": row.get("subtab_label", "").strip(),
                "notes": row.get("notes", "").strip(),
            }
    return config


def cat_to_tab(config=None):
    """Return {category_name: default_tab} derived from the config."""
    if config is None:
        config = load_category_config()
    return {cat: vals["default_tab"] for cat, vals in config.items()}


def anchor_to_expected_tabs(config=None):
    """
    Return {anchor_id: set_of_expected_tabs} derived from category → anchor mappings.

    Used by build_union_table.py for tab-anchor mismatch validation.
    """
    if config is None:
        config = load_category_config()
    mapping: dict[str, set] = {}
    for vals in config.values():
        tab = vals["default_tab"]
        for anchor in vals["default_anchors"]:
            mapping.setdefault(anchor, set()).add(tab)
    return mapping
