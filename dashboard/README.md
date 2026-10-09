# Dashboard — Mapa do Crime (Baixada Santista)

Dashboard de criminalidade de 9 cidades da Baixada Santista (2017 a 2024): Bertioga, Cubatão, Guarujá, Itanhaém, Mongaguá, Peruíbe, Praia Grande, Santos e São Vicente.

Esta pasta tem duas versões do mesmo dashboard, feitas com os mesmos dados.

## Versões

| Versão | Pasta | Ferramenta | Como abrir |
|---|---|---|---|
| **Original** | `original/` | Power BI | Abrir o arquivo `.pbix` no Power BI Desktop |
| **Web** | `versao-web/` | HTML, CSS e JavaScript | Abrir o `index.html` no navegador |

### Original (Power BI)

Foi a versão produzida originalmente no trabalho. Por problemas técnicos, ela chegou a ser perdida e depois foi recuperada. Tem duas páginas: **por quantidade de crimes** e **por taxa de 100 mil habitantes**.

### Versão web

Enquanto a original estava perdida, foi feita esta segunda versão, para não deixar o trabalho incompleto. Ela recria o dashboard com os mesmos dados e funciona direto no navegador, sem precisar do Power BI.

## O que os dois dashboards mostram

- As duas medidas: quantidade de crimes e taxa por 100 mil habitantes (soma das taxas mensais).
- Filtros por natureza do crime, cidade, mês e ano.
- Gráfico de linhas por cidade e ano, gráfico de pizza (rosca na versão web) por ano e mapa por cidade.
- A versão web inclui ainda um gráfico de barras por natureza do crime e uma tabela de dados.

## Como abrir a versão web

Abra o `index.html` no navegador. Os dados já estão dentro do arquivo. É preciso estar com internet para carregar as bibliotecas e o mapa de fundo.

Para publicar no GitHub Pages: em **Settings → Pages**, escolha a branch `main` e a pasta do repositório que contém o `index.html`.

## Tecnologias

- Original: Power BI
- Versão web: [Chart.js](https://www.chartjs.org/) (gráficos) e [Leaflet](https://leafletjs.com/) (mapa)

## Fontes

- Dados de criminalidade e população: tabelas `Crimes` e `População` do relatório em Power BI.
- Contorno dos municípios (versão web): Malha Municipal Digital 2025, [IBGE](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html).
- Mapa de fundo (versão web): Esri.
