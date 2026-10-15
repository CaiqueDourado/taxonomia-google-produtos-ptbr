# Taxonomia de produtos do Google (pt-BR + en)

[![validate](https://github.com/CaiqueDourado/taxonomia-google-produtos-ptbr/actions/workflows/validate.yml/badge.svg)](https://github.com/CaiqueDourado/taxonomia-google-produtos-ptbr/actions/workflows/validate.yml)
[![Dados: CC BY 4.0 + Google](https://img.shields.io/badge/dados-CC%20BY%204.0%20%2B%20Google-lightgrey.svg)](LICENSE-DATA.md)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-blue.svg)](LICENSE)
[![Kaggle](https://img.shields.io/badge/Kaggle-dataset-20BEFF.svg)](https://www.kaggle.com/datasets/caiquedourado/taxonomia-google-produtos-ptbr)

**A taxonomia de produtos do Google (Merchant Center) em português e inglês**, com id oficial, categoria pai, nível e caminho completo. São 5.595 categorias em três formatos: tabela, tabela de fechamento e árvore JSON.

[Read in English](README.md)

| Arquivo | Linhas | O que é |
|---|---|---|
| `categorias` (CSV · Parquet · JSON) | 5.595 | Uma linha por categoria: ids, pai, nível, folha, nomes e caminhos PT/EN, primeiro nível, slug |
| `hierarquia` (CSV · Parquet) | 22.907 | Tabela de fechamento: cada par (categoria, ancestral) |
| `arvore.json` | 1 árvore | `{id, name_pt, name_en, children}` aninhado |

Versão **2021-09-21** (a mais recente publicada pelo Google) · 21 categorias de primeiro nível · até 7 níveis · 4.719 folhas.

## Prévia

| google_id | parent_id | level | is_leaf | name_pt | name_en | slug_pt |
|---|---|---|---|---|---|---|
| 536 | | 1 | False | Casa e jardim | Home & Garden | casa-e-jardim |
| 696 | 536 | 2 | False | Decoração | Decor | casa-e-jardim/decoracao |
| 588 | 592 | 4 | True | Velas | Candles | casa-e-jardim/decoracao/fragrancias-domesticas/velas |
| 3329 | 2425 | 4 | True | Lâmpadas de LED | LED Light Bulbs | casa-e-jardim/iluminacao/lampadas/lampadas-de-led |

## Como usar

```python
import pandas as pd

base = "https://raw.githubusercontent.com/CaiqueDourado/taxonomia-google-produtos-ptbr/main/data/"
cat = pd.read_csv(base + "categorias.csv", dtype={"parent_id": "Int64"})
hier = pd.read_csv(base + "hierarquia.csv")

# Todas as categorias finais dentro de "Casa e jardim > Decoração" (google_id 696)
folhas = hier[hier.ancestor_id == 696].merge(cat, on="google_id").query("is_leaf")
```

Usos típicos:

- **Feeds:** preencher `google_product_category` em feeds do Google Shopping no Brasil.
- **Tradução:** mapear categorias de loja entre português e inglês.
- **Páginas:** montar páginas de categoria, menus e breadcrumbs.
- **Machine learning:** treinar classificadores de produto com rótulos bilíngues.

## Como foi construída

O Google publica a taxonomia como um arquivo de texto por idioma ([documentação](https://support.google.com/merchants/answer/6324436)). O autor carregou o arquivo em português no SQL Server, anos atrás, para classificar produtos coletados de lojas brasileiras. A tabela tinha uma linha por nível de cada caminho, sem o id do Google e sem o pai.

Este repositório volta aos arquivos oficiais em português e inglês. Ele:

- reconstrói a hierarquia com os ids oficiais;
- limpa os nomes;
- casa os 5.595 caminhos da tabela antiga (`legacy_id`);
- publica a árvore nos três formatos que as pessoas de fato consultam.

Detalhes e exemplos de SQL estão em [methodology.md](docs/methodology.md). Coluna por coluna: [dicionário de dados](docs/data-dictionary.pt-BR.md).

## Qualidade

O arquivo pt-BR do Google tem alguns problemas:

- espaços inseparáveis dentro de 14 nomes;
- espaços sobrando no fim de 9 nomes;
- um espaço duplo;
- um erro de digitação (`imâs` em vez de `ímãs`).

Isso quebra comparações exatas. Tudo foi corrigido e é testado. O relatório completo está em [data-quality.md](docs/data-quality.md).

Uma observação: o arquivo do Google parece "sem acentos" em algumas ferramentas do Windows porque é UTF-8 sem BOM. No Excel, use *Dados → De Texto/CSV* e escolha UTF-8.

## Licença

Nomes e ids das categorias © Google; tudo o que foi derivado aqui é CC BY 4.0. Veja [LICENSE-DATA.md](LICENSE-DATA.md). Código: [MIT](LICENSE).

## Autor

**Caique Dourado**: 20 anos construindo crawlers, pipelines de dados e SEO programático para o e-commerce brasileiro em .NET e SQL Server. Veja também o [BrCommerceKit](https://github.com/CaiqueDourado/BrCommerceKit), que detecta plataformas de loja e lê feeds do Google Shopping.
