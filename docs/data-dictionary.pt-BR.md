# Dicionário de dados: Taxonomia de produtos do Google em português e inglês: ids, pais, caminhos, tabela de fechamento e árvore

Gerado por `scripts/docs.py` a partir de `schema/columns.json`. Tipos, nulos e exemplos vêm dos arquivos em `data/`.

## `categorias.csv`

Uma linha por categoria (5.595): id oficial do Google, id do pai, nível, folha, nomes e caminhos em português e inglês, ancestral de primeiro nível, slug.

| Coluna | Tipo | Nulos | Exemplo | Descrição | Padrão | Origem |
|---|---|---|---|---|---|---|
| `google_id` | integer | 0,0% | `3809` | Id oficial da Google Product Taxonomy, o valor aceito pelo Merchant Center em google_product_category. Chave primária. | Google | Google |
| `parent_id` | integer | 0,4% | `2920` | google_id da categoria pai; vazio nas 21 categorias de primeiro nível. | — | derivado |
| `level` | integer | 0,0% | `4` | Profundidade na árvore, de 1 (primeiro nível) a 7. | — | derivado |
| `is_leaf` | boolean | 0,0% | `True` | Verdadeiro quando a categoria não tem filhas (4.719 de 5.595). | — | derivado |
| `child_count` | integer | 0,0% | `0` | Quantidade de filhas diretas. | — | derivado |
| `name_pt` | string | 0,0% | `Garrafas de água` | Nome da categoria em português do Brasil (limpo). | Google | Google, cleaned |
| `name_en` | string | 0,0% | `Water Bottles` | Nome da categoria em inglês (en-US). | Google | Google |
| `path_pt` | string | 0,0% | `Casa e jardim > Produtos de cozinha e…` | Caminho completo em português, níveis separados por " > ". | Google | Google, cleaned |
| `path_en` | string | 0,0% | `Home & Garden > Kitchen & Dining > Fo…` | Caminho completo em inglês, níveis separados por " > ". | Google | Google |
| `top_level_id` | integer | 0,0% | `536` | google_id do ancestral de primeiro nível. | — | derivado |
| `top_level_pt` | string | 0,0% | `Casa e jardim` | Nome do ancestral de primeiro nível em português. | — | derivado |
| `top_level_en` | string | 0,0% | `Home & Garden` | Nome do ancestral de primeiro nível em inglês. | — | derivado |
| `slug_pt` | string | 0,0% | `casa-e-jardim/produtos-de-cozinha-e-a…` | Caminho de URL a partir do caminho em português (casa-e-jardim/decoracao/fragrancias-domesticas/velas). Único. | — | derivado |
| `legacy_id` | integer | 0,0% | `3282` | Id da tabela SQL Server do autor (idTaxonomiaRaw), mantido para cruzar com bases antigas. | — | Caique Dourado |

## `hierarquia.csv`

Tabela de fechamento: uma linha por par (categoria, ancestral), 22.907 linhas. Responde "todos os descendentes de X" com um único join.

| Coluna | Tipo | Nulos | Exemplo | Descrição | Padrão | Origem |
|---|---|---|---|---|---|---|
| `google_id` | integer | 0,0% | `5134` | Categoria. | — | derivado |
| `ancestor_id` | integer | 0,0% | `638` | Um ancestral da categoria, ou a própria categoria (distância 0). | — | derivado |
| `ancestor_level` | integer | 0,0% | `2` | Nível do ancestral (1 = primeiro nível). | — | derivado |
| `distance` | integer | 0,0% | `2` | Quantidade de passos da categoria até o ancestral. | — | derivado |

## Convenções

- Codificação UTF-8 sem BOM, separador vírgula, cabeçalho na primeira linha, quebra de linha `\n`.
- Caminhos usam ` > ` entre os níveis, como nos arquivos do Google. Booleanos são `True` / `False`.
- `google_id` é a chave das duas tabelas e de `arvore.json`.
