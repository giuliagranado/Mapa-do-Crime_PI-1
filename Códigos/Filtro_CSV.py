import os
import pandas as pd
import re

# Caminhos
input_folder = r"C:\Users\lab51\Downloads\Brutos\Brutos"
output_file = r"C:\Users\lab51\Downloads\Brutos\Filtrados\Tabela_Final.xlsx"

# Crimes que mantemos (maiusculo sem parenteses)
crimes_mantidos = [
    "HOMICÍDIO DOLOSO",
    "TENTATIVA DE HOMICÍDIO",
    "LESÃO CORPORAL SEGUIDA DE MORTE",
    "LESÃO CORPORAL DOLOSA",
    "LATROCÍNIO",
    "ESTUPRO",
    "ESTUPRO DE VULNERÁVEL",
    "ROUBO - OUTROS"
    "ROUBO DE VEÍCULO",
    "ROUBO A BANCO",
    "ROUBO DE CARGA",
    "FURTO - OUTROS",
    "FURTO DE VEÍCULO"
]

# mapa de meses (aceita MARCO sem cedilha)
meses_map = {
    "JANEIRO": "Jan", "FEVEREIRO": "Fev", "MARÇO": "Mar", "MARCO": "Mar",
    "ABRIL": "Abr", "MAIO": "Mai", "JUNHO": "Jun", "JULHO": "Jul",
    "AGOSTO": "Ago", "SETEMBRO": "Set", "OUTUBRO": "Out", "NOVEMBRO": "Nov", "DEZEMBRO": "Dez"
}
ordem_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

def clean_crime_name(name):
    s = str(name).strip().upper()
    # remove parênteses com qualquer conteúdo
    s = re.sub(r"\s*\(.*?\)", "", s)
    return s.strip()

def abbrevia_mes(m):
    if pd.isna(m):
        return m
    key = str(m).strip().upper()
    return meses_map.get(key, key[:3].capitalize() if len(key) >= 3 else key)

all_rows = []

files = [f for f in os.listdir(input_folder) if f.lower().endswith((".xlsx", ".xls"))]
if not files:
    print("Nenhum arquivo .xlsx/.xls encontrado em:", input_folder)

for file in files:
    file_path = os.path.join(input_folder, file)
    print("Processando:", file)

    # inferir cidade e ano a partir do nome do arquivo
    name_no_ext = os.path.splitext(file)[0]
    # ano: últimos 2 dígitos no nome
    m = re.search(r"(\d{2})$", name_no_ext)
    year = int("20" + m.group(1)) if m else None
    # cidade = resto do nome antes dos dígitos
    city = re.sub(r"\d{2}$", "", name_no_ext).strip()

    # ler com header automático (assume primeira linha cabeçalho)
    try:
        df = pd.read_excel(file_path, engine="openpyxl")
    except Exception as e:
        print(f"  ⚠️ Falha ao ler {file}: {e}. Pulando.")
        continue

    # padroniza colunas (remover espaços)
    df.columns = [str(c).strip() for c in df.columns]

    # identificar a coluna das naturezas (primeira coluna não-mes). 
    # Normalmente é a primeira coluna; garantimos que existe.
    nature_col = df.columns[0]

    # remover colunas de total (se houver alguma com TOTAL no nome)
    cols = [c for c in df.columns if "TOTAL" not in str(c).upper()]
    df = df[cols]

    # limpar nomes de crimes na coluna de natureza
    df[nature_col] = df[nature_col].apply(clean_crime_name)

    # identificar colunas de meses: todas exceto a coluna de natureza
    month_cols = [c for c in df.columns if c != nature_col]
    if not month_cols:
        print(f"  ⚠️ Arquivo {file} não tem colunas de mês detectadas. Pulando.")
        continue

    # substituir "..." por NaN e depois por 0 ao converter
    df = df.replace("...", pd.NA)

    # melt (wide -> long)
    df_long = df.melt(id_vars=[nature_col], value_vars=month_cols, var_name="Mês", value_name="Quantidade")

    # padronizar nomes: natureza uppercase sem parênteses
    df_long["Natureza"] = df_long[nature_col].apply(clean_crime_name)

    # filtrar só crimes mantidos
    df_long = df_long[df_long["Natureza"].isin(crimes_mantidos)].copy()

    # padronizar mês
    df_long["Mês"] = df_long["Mês"].apply(abbrevia_mes)

    # preencher Quantidade (NaN -> 0) e garantir inteiro
    df_long["Quantidade"] = pd.to_numeric(df_long["Quantidade"], errors="coerce").fillna(0).astype(int)

    # adicionar cidade e ano
    df_long["Cidade"] = city
    df_long["Ano"] = year

    # reorganizar colunas na ordem pedida
    df_long = df_long[["Natureza", "Cidade", "Ano", "Mês", "Quantidade"]]

    all_rows.append(df_long)

# concatenar tudo
if not all_rows:
    print("Nenhum dado válido para concatenar.")
else:
    result = pd.concat(all_rows, ignore_index=True)

    # garantir que mês seja categórico na ordem correta
    result["Mês"] = pd.Categorical(result["Mês"], categories=ordem_meses, ordered=True)

    # ordenar
    result = result.sort_values(by=["Cidade", "Ano", "Natureza", "Mês"]).reset_index(drop=True)

    # salvar
    result.to_excel(output_file, index=False)
    print("Consolidado salvo em:", output_file)