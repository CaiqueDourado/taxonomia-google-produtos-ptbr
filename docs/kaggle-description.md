**Taxonomia de produtos do Google** em português do Brasil e inglês, com ids oficiais, categoria pai, nível e caminhos completos. **Google Product Taxonomy** in Brazilian Portuguese and English, with official ids, parent ids, levels and full paths, in three shapes ready to use.

The taxonomy is the category tree Google Merchant Center accepts in `google_product_category`. Google publishes it as one text file per language ([documentation](https://support.google.com/merchants/answer/6324436)); this dataset joins the pt-BR and en-US files, rebuilds the hierarchy and cleans it.

## Files

- `categorias.csv` / `.parquet` / `.json`: 5,595 categories with `google_id`, `parent_id`, `level` (1–7), `is_leaf`, `child_count`, names and paths in Portuguese and English, top-level ancestor and URL slug.
- `hierarquia.csv` / `.parquet`: closure table with 22,907 (category, ancestor) pairs. "All descendants of X" is a single join in any SQL database.
- `arvore.json`: nested tree for menus and category pickers.

## How a category is structured

![Panelas e assadeiras as one nested JSON record](https://raw.githubusercontent.com/CaiqueDourado/taxonomia-google-produtos-ptbr/main/docs/img/category-json.png)

The three files join on `google_id`. Put together for **Panelas e assadeiras** (Cookware & Bakeware, id 6070): its names and path from `categorias`, its two ancestors and its 43 descendants (38 of them leaves) from `hierarquia`, and its 5 children with their own children from `arvore.json`. Full record: [docs/example-category.json](https://github.com/CaiqueDourado/taxonomia-google-produtos-ptbr/blob/main/docs/example-category.json), built by [scripts/make_json.py](https://github.com/CaiqueDourado/taxonomia-google-produtos-ptbr/blob/main/scripts/make_json.py).

## Use cases

- Map product feeds to Google Shopping in Brazil.
- Translate categories between Portuguese and English.
- Build category pages or breadcrumbs.
- Train a product classifier with a bilingual label set.

## Cleaning

The pt-BR file has non-breaking spaces, trailing and double spaces, and one typo (`imâs`). They are fixed, documented and tested.

Version 2021-09-21 (latest published by Google). Category names and ids © Google; structure, cleaning and derived columns by Caique Dourado (CC BY 4.0). Scripts, dictionary and quality report: **https://github.com/CaiqueDourado/taxonomia-google-produtos-ptbr**

This taxonomy was used to classify the products of the Brazilian e-commerce product catalog (114.6 million offers from 7,179 stores): https://www.kaggle.com/datasets/caiquedourado/catalogo-produtos-ecommerce-brasil
