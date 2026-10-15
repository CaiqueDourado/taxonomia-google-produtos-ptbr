"""Validate the taxonomy files in data/. Exits with code 1 on any failure.

Usage:  python scripts/validate.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEP = " > "
failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    cat = pd.read_parquet(ROOT / "data" / "categorias.parquet")
    csv_cat = pd.read_csv(ROOT / "data" / "categorias.csv", keep_default_na=False)
    hier = pd.read_parquet(ROOT / "data" / "hierarquia.parquet")
    tree = json.loads((ROOT / "data" / "arvore.json").read_text(encoding="utf-8"))

    check(len(cat) == 5595, f"expected 5595 categories, got {len(cat)}")
    check(len(csv_cat) == len(cat), "CSV and Parquet differ")
    for column in ("google_id", "legacy_id", "path_pt", "path_en", "slug_pt"):
        check(cat[column].is_unique, f"{column} is not unique")
    check(sorted(cat["legacy_id"]) == list(range(1, 5596)), "legacy_id must cover 1..5595")

    by_id = cat.set_index("google_id")
    roots = cat[cat["parent_id"].isna()]
    check(len(roots) == 21 and (roots["level"] == 1).all(), "expected 21 top-level categories at level 1")

    child = cat.dropna(subset=["parent_id"])
    parents = by_id.loc[child["parent_id"].astype(int)]
    check(child["parent_id"].isin(cat["google_id"]).all(), "parent_id points to a missing category")
    check((child["level"].to_numpy() == parents["level"].to_numpy() + 1).all(), "level is not parent level + 1")
    check((child["path_pt"].to_numpy() == (parents["path_pt"] + SEP).to_numpy() + child["name_pt"].to_numpy()).all(), "path_pt is not parent path + name")
    check((child["path_en"].to_numpy() == (parents["path_en"] + SEP).to_numpy() + child["name_en"].to_numpy()).all(), "path_en is not parent path + name")
    check((cat["path_pt"].str.count(SEP) + 1 == cat["level"]).all(), "path depth differs from level")

    counted = cat["parent_id"].dropna().astype(int).value_counts()
    check((cat["google_id"].map(counted).fillna(0).astype(int) == cat["child_count"]).all(), "child_count is wrong")
    check((cat["is_leaf"] == (cat["child_count"] == 0)).all(), "is_leaf disagrees with child_count")

    check(len(hier) == int(cat["level"].sum()) == 22907, f"closure table should have 22907 rows, has {len(hier)}")
    check((hier.groupby("google_id").size() == by_id["level"].reindex(hier["google_id"].unique())).all(), "closure rows per category differ from level")
    top = hier[hier["ancestor_level"] == 1].set_index("google_id")["ancestor_id"]
    check((cat.set_index("google_id")["top_level_id"] == top.reindex(cat["google_id"]).to_numpy()).all(), "top_level_id differs from closure table")

    def count(nodes: list[dict]) -> int:
        return sum(1 + count(n.get("children", [])) for n in nodes)

    check(count(tree["children"]) == len(cat), "arvore.json does not contain every category once")

    for column in ("name_pt", "name_en", "path_pt", "path_en"):
        bad = cat[cat[column].str.contains(" |  ", regex=True) | (cat[column] != cat[column].str.strip())]
        check(bad.empty, f"{column}: non-breaking or repeated spaces left: {bad[column].tolist()[:3]}")

    for message in failures:
        print("FAIL", message)
    print(f"{len(cat)} categories and {len(hier)} closure rows checked, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
