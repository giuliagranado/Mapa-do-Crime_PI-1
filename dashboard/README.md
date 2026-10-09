# Painel de Criminalidade na Baixada Santista

Dashboard interativo com dados de criminalidade de 9 cidades da Baixada Santista (2017 a 2024).

## Sobre esta versão

Por problemas técnicos, o primeiro dashboard, produzido originalmente no trabalho, foi perdido. Para não deixar o trabalho incompleto, foi feita esta segunda versão, com os mesmos dados.

## O que o painel mostra

- Duas visões, como no relatório original: **por quantidade de crimes** e **por taxa de 100 mil habitantes**.
- Filtros por natureza do crime, cidade, mês e ano.
- Gráfico de linhas por cidade e ano, gráfico de rosca por ano e gráfico de barras por natureza.
- Mapa por município: quanto mais escuro o roxo, maior o valor.
- Tabela de dados, que abre pelo botão no fim da página.

Cidades: Bertioga, Cubatão, Guarujá, Itanhaém, Mongaguá, Peruíbe, Praia Grande, Santos e São Vicente.

## Como abrir

Abra o arquivo `index.html` no navegador. Os dados já estão dentro do arquivo. É preciso internet para carregar as bibliotecas de gráficos e o mapa de fundo.

## Tecnologias

- HTML, CSS e JavaScript em um único arquivo
- [Chart.js](https://www.chartjs.org/) para os gráficos
- [Leaflet](https://leafletjs.com/) para o mapa

## Fontes

- Dados de criminalidade e população: tabelas do relatório original em Power BI (`Crimes` e `População`). A taxa por 100 mil habitantes é a soma das taxas mensais.
- Contorno dos municípios: Malha Municipal Digital 2025, [IBGE](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html).
- Mapa de fundo: Esri.
