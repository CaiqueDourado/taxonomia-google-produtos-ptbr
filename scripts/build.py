"""Build the clean Google Product Taxonomy (pt-BR + en-US) from raw/.

Usage:  python scripts/build.py

Inputs (untouched in raw/):
  taxonomy-with-ids.pt-BR.txt, taxonomy-with-ids.en-US.txt  official Google files, version 2021-09-21
  taxonomias.csv                                            the author's SQL Server table (one row per path level)

Outputs (data/):
  categorias.{csv,parquet,json}   one row per category: ids, parent, level, names and paths in both languages
  hierarquia.{csv,parquet}        closure table: one row per (category, ancestor), 22,907 rows
  arvore.json                     nested tree, ready for a category picker
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "data"
SEP = " > "

# Typos in Google's pt-BR file, fixed in the clean names (see docs/data-quality.md).
NAME_FIXES = {"Adesivos e imâs para artesanato": "Adesivos e ímãs para artesanato"}


def clean(name: str) -> str:
    """Non-breaking spaces to spaces, collapse runs of spaces, trim, apply known typo fixes."""
    name = re.sub(r"\s+", " ", name.replace(" ", " ")).strip()
    return NAME_FIXES.get(name, name)


def read_google(path: Path) -> tuple[str, dict[int, list[str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    version = lines[0].split(":", 1)[1].strip()
    categories = {}
    for line in lines[1:]:
        if line.strip():
            google_id, full_path = line.split(" - ", 1)
            categories[int(google_id)] = [clean(part) for part in full_path.split(SEP)]
    return version, categories


def read_legacy() -> dict[str, int]:
    """Maps the cleaned pt-BR path to the author's legacy id (idTaxonomiaRaw)."""
    levels: dict[int, list[tuple[int, str]]] = defaultdict(list)
    with (RAW / "taxonomias.csv").open(encoding="utf-8-sig", newline="") as handle:
        for _row_id, legacy_id, name, position, _total in csv.reader(handle, delimiter=";"):
            levels[int(legacy_id)].append((int(position), clean(name)))
    return {SEP.join(name for _, name in sorted(parts)): legacy for legacy, parts in levels.items()}


def slugify(text: str) -> str:
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def main() -> None:
    version_pt, pt = read_google(RAW / "taxonomy-with-ids.pt-BR.txt")
    version_en, en = read_google(RAW / "taxonomy-with-ids.en-US.txt")
    if version_pt != version_en or pt.keys() != en.keys():
        raise SystemExit("pt-BR and en-US files are not the same taxonomy version")
    legacy = read_legacy()

    id_by_path = {SEP.join(parts): google_id for google_id, parts in pt.items()}
    rows = []
    for google_id, parts in pt.items():
        parent_path = SEP.join(parts[:-1])
        rows.append(
            {
                "google_id": google_id,
                "parent_id": id_by_path[parent_path] if len(parts) > 1 else None,
                "level": len(parts),
                "name_pt": parts[-1],
                "name_en": en[google_id][-1],
                "path_pt": SEP.join(parts),
                "path_en": SEP.join(en[google_id]),
                "top_level_id": id_by_path[parts[0]],
                "top_level_pt": parts[0],
                "top_level_en": en[google_id][0],
                "slug_pt": "/".join(slugify(p) for p in parts),
                "legacy_id": legacy[SEP.join(parts)],
            }
        )
    cat = pd.DataFrame(rows)
    children = cat.groupby("parent_id").size()
    cat["child_count"] = cat["google_id"].map(children).fillna(0).astype(int)
    cat["is_leaf"] = cat["child_count"] == 0
    cat["parent_id"] = cat["parent_id"].astype("Int64")
    cat = cat.sort_values("path_pt", key=lambda s: s.map(lambda p: [slugify(x) for x in p.split(SEP)])).reset_index(drop=True)
    cat = cat[
        ["google_id", "parent_id", "level", "is_leaf", "child_count", "name_pt", "name_en", "path_pt", "path_en",
         "top_level_id", "top_level_pt", "top_level_en", "slug_pt", "legacy_id"]
    ]

    # Closure table: every category paired with each of its ancestors (itself included, distance 0).
    parent = dict(zip(cat["google_id"], cat["parent_id"]))
    level = dict(zip(cat["google_id"], cat["level"]))
    closure = []
    for google_id in cat["google_id"]:
        node, distance = google_id, 0
        while node is not pd.NA and node is not None:
            closure.append({"google_id": google_id, "ancestor_id": node, "ancestor_level": level[node], "distance": distance})
            node, distance = parent[node], distance + 1
            node = None if pd.isna(node) else int(node)
    hier = pd.DataFrame(closure).sort_values(["google_id", "ancestor_level"]).reset_index(drop=True)

    # Nested tree.
    kids: dict[object, list[dict]] = defaultdict(list)
    for row in cat.itertuples():
        kids[None if pd.isna(row.parent_id) else int(row.parent_id)].append(
            {"id": int(row.google_id), "name_pt": row.name_pt, "name_en": row.name_en}
        )

    def attach(node: dict) -> dict:
        sub = [attach(child) for child in kids.get(node["id"], [])]
        return {**node, "children": sub} if sub else node

    tree = {"version": version_pt, "source": "Google Product Taxonomy", "children": [attach(n) for n in kids[None]]}

    OUT.mkdir(exist_ok=True)
    cat.to_csv(OUT / "categorias.csv", index=False, encoding="utf-8", lineterminator="\n")
    cat.to_parquet(OUT / "categorias.parquet", index=False)
    records = json.loads(cat.to_json(orient="records", force_ascii=False))
    (OUT / "categorias.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hier.to_csv(OUT / "hierarquia.csv", index=False, encoding="utf-8", lineterminator="\n")
    hier.to_parquet(OUT / "hierarquia.parquet", index=False)
    (OUT / "arvore.json").write_text(json.dumps(tree, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    stats = {
        "dataset": "taxonomia-google-produtos-ptbr",
        "google_taxonomy_version": version_pt,
        "categories": len(cat),
        "leaves": int(cat["is_leaf"].sum()),
        "top_level": int((cat["level"] == 1).sum()),
        "by_level": {int(k): int(v) for k, v in cat["level"].value_counts().sort_index().items()},
        "closure_rows": len(hier),
        "by_top_level": cat["top_level_pt"].value_counts().to_dict(),
    }
    (ROOT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(cat)} categories, {len(hier)} closure rows, version {version_pt} -> data/")


if __name__ == "__main__":
    main()
