"""Build one category as a nested JSON record (docs/example-category.json), for the README and Kaggle.

    python scripts/make_json.py          # 6070, Casa e jardim > ... > Panelas e assadeiras
    python scripts/make_json.py 2425     # any google_id

Joins the three shapes of the data: the row in data/categorias.json, its ancestors and descendants from
data/hierarquia.csv (closure table) and its whole subtree as it appears in data/arvore.json. Only the
standard library is needed.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DEFAULT = 6070


def find(node: dict, google_id: int) -> dict | None:
    if node.get("id") == google_id:
        return node
    for child in node.get("children", []):
        hit = find(child, google_id)
        if hit is not None:
            return hit
    return None


def subtree(node: dict, cats: dict) -> dict:
    """A node of arvore.json with the leaf flag from categorias; children only where there are any."""
    out = {"google_id": node["id"], "name_pt": node["name_pt"], "name_en": node["name_en"],
           "is_leaf": cats[node["id"]]["is_leaf"]}
    if node.get("children"):
        out["children"] = [subtree(ch, cats) for ch in node["children"]]
    return out


def build(google_id: int) -> dict:
    cats = {c["google_id"]: c for c in json.loads((DATA / "categorias.json").read_text(encoding="utf-8"))}
    with (DATA / "hierarquia.csv").open(encoding="utf-8", newline="") as f:
        pairs = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(f)]
    tree = json.loads((DATA / "arvore.json").read_text(encoding="utf-8"))
    c = cats[google_id]
    node = find(tree, google_id)

    ancestors = sorted((p for p in pairs if p["google_id"] == google_id and p["distance"] > 0),
                       key=lambda p: p["ancestor_level"])
    descendants = [cats[p["google_id"]] for p in pairs if p["ancestor_id"] == google_id and p["distance"] > 0]
    parent = cats[c["parent_id"]] if c["parent_id"] is not None else None

    def brief(cat: dict) -> dict:
        return {"google_id": cat["google_id"], "level": cat["level"], "name_pt": cat["name_pt"], "name_en": cat["name_en"]}

    return {
        "google_id": c["google_id"],
        "names": {"pt": c["name_pt"], "en": c["name_en"]},
        "path": {"pt": c["path_pt"], "en": c["path_en"]},
        "level": c["level"],
        "is_leaf": c["is_leaf"],
        "slug_pt": c["slug_pt"],
        "legacy_id": c["legacy_id"],
        "top_level": {"google_id": c["top_level_id"], "name_pt": c["top_level_pt"], "name_en": c["top_level_en"]},
        "parent": brief(parent) if parent else None,
        "ancestors": [brief(cats[p["ancestor_id"]]) for p in ancestors],
        "descendants": {"total": len(descendants), "leaves": sum(d["is_leaf"] for d in descendants)},
        "child_count": c["child_count"],
        "children": [subtree(ch, cats) for ch in (node or {}).get("children", [])],
    }


def main() -> None:
    google_id = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    out = ROOT / "docs" / "example-category.json"
    out.write_text(json.dumps(build(google_id), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
