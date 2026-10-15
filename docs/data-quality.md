# Data quality report

## Fixed in the clean version

| # | Problem | Where | Fix |
|---|---|---|---|
| 1 | Non-breaking spaces (U+00A0) inside names, invisible but breaking exact matches (`Caixas para amplificadores`, `Equipamentos de proteção para motocicletas`…) | 14 category names (24 lines of Google's pt-BR file) | Replaced by normal spaces |
| 2 | Trailing spaces (`Fivelas  `, `Cortinas para box de banheiro `) | 9 names | Trimmed |
| 3 | Double space: `Formas para quesadillas e  tortillas` | 1 name | Collapsed |
| 4 | Typo in Google's translation: `Adesivos e imâs para artesanato` (the child category is spelled correctly, `Ímãs`) | 1 name, 6 paths | `Adesivos e ímãs para artesanato` |
| 5 | The author's SQL Server table had no Google id, no parent id, and an id padded with spaces (`"1         "`) | 22,907 rows | Official `google_id` and `parent_id`; the old id kept as integer `legacy_id` |
| 6 | The pt-BR file looks broken when opened in some Windows tools: it is UTF-8 without BOM | file | `data/` files are UTF-8 and read correctly by pandas, DuckDB, Kaggle and GitHub; for Excel, use *Data → From Text/CSV* and choose UTF-8 |

The original Google files and the author's table are kept unchanged in `raw/`.

## Checked and correct

- The pt-BR and en-US files have the same version (2021-09-21) and the same 5,595 ids, and every category sits at the same depth in both.
- All 5,595 paths of the author's table match an official category after cleaning. The table had been loaded from the same version, in a different order.
- There are no duplicate paths and no orphan categories.

## Known limitations

- **Version 2021-09-21 is the latest Google published.** Merchant Center still accepts it, but categories for newer products may be missing.
- **The Portuguese translation is Google's.** Apart from the typo above, some terms read as literal translations (`Adultos` for *Mature*, `Ferragens` for *Hardware*). They are kept, because Merchant Center matches these exact strings.
- **`slug_pt` is derived here.** It is not part of Google's taxonomy.
