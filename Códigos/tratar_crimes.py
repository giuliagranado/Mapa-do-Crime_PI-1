# -*- coding: utf-8 -*-
"""
Pipeline otimizado para consolidar, filtrar e agregar dados criminais.

Executa um fluxo de trabalho de ponta a ponta:
1. Converte múltiplos arquivos Excel para um único CSV intermediário, já com os
   nomes de colunas padronizados.
2. Filtra o CSV consolidado com base nos critérios definidos.
3. Agrupa os dados para contar a quantidade de ocorrências por local/crime.
4. Salva um relatório agregado e formatado em um novo arquivo Excel.
"""

import pandas as pd
import time
import os
import concurrent.futures
from typing import Dict, List
from tqdm import tqdm

# ==============================================================================
# SEÇÃO DE CONFIGURAÇÃO
# ==============================================================================

# Arquivos de entrada e saída.
ARQUIVOS_EXCEL_ORIGINAIS = ["SPDadosCriminais_2022.xlsx", "SPDadosCriminais_2023.xlsx", "SPDadosCriminais_2024.xlsx", "SPDadosCriminais_2025.xlsx"]
ARQUIVO_EXCEL_FINAL_FORMATADO = "Relatorio_Criminal_Agregado.xlsx"
ARQUIVO_CSV_INTERMEDIARIO = "temp_dados_completos.csv"

# Mapeamento para padronizar os nomes das colunas na leitura.
# Chave: Nome original no arquivo | Valor: Nome novo no script.
MAPEAMENTO_COLUNAS: Dict[str, str] = {
    "NATUREZA_APURADA": "natureza do crime", "CIDADE": "cidade",
    "ANO_ESTATISTICA": "ano", "MES_ESTATISTICA": "mês", "BAIRRO": "bairro",
    "NOME_DELEGACIA": "delegacia", "RUBRICA": "artigo do crime", 
    "LATITUDE": "latitude", "LONGITUDE": "longitude"
}

# Critérios para a filtragem dos dados. Para desativar um filtro,
# basta deixar a lista vazia (ex: "ano": []).
FILTROS: Dict[str, List] = {
    "ano": [2022, 2023, 2024, 2025],
    "cidade": ["SANTOS", "CUBATÃO", "PRAIA GRANDE", "SÃO VICENTE", "GUARUJÁ", "BERTIOGA", "MONGAGUÁ", "ITANHAÉM", "PERUÍBE"],
}

# Colunas que definem a granularidade do relatório final.
# A contagem de crimes será feita para cada combinação única destas colunas.
COLUNAS_PARA_AGRUPAR: List[str] = [
    "natureza do crime", "cidade", "bairro", "artigo do crime", "delegacia",
    "mês", "ano", "latitude", "longitude",
]

# Dicionário para corrigir variações nos nomes das cidades.
# Chave: Nome incorreto | Valor: Nome padronizado.
MAPA_DE_CIDADES: Dict[str, str] = {
    'S.VICENTE': 'SÃO VICENTE', 'S VICENTE': 'SÃO VICENTE',
    'P. GRANDE': 'PRAIA GRANDE', 'PRAIAGRANDE': 'PRAIA GRANDE',
    'CUBATAO': 'CUBATÃO',
}

# ==============================================================================
# FUNÇÕES DO PIPELINE
# ==============================================================================

def _processar_arquivo(caminho: str) -> pd.DataFrame:
    """
    Lê um único arquivo Excel e suas abas. Executada em paralelo para otimização.
    Também padroniza o nome da coluna de cidade para 'CIDADE'.
    """
    try:
        planilhas = pd.read_excel(caminho, engine='openpyxl', sheet_name=None)
        df = pd.concat(planilhas.values(), ignore_index=True) if planilhas else pd.DataFrame()

        # Padroniza o nome da coluna para consistência entre arquivos de layout diferente.
        if 'NOME_MUNICIPIO' in df.columns:
            df.rename(columns={'NOME_MUNICIPIO': 'CIDADE'}, inplace=True)
        
        return df
    except FileNotFoundError:
        tqdm.write(f"AVISO: O arquivo '{caminho}' não foi encontrado.")
        return pd.DataFrame()
    except Exception as e:
        tqdm.write(f"ERRO: Não foi possível processar '{caminho}'. Erro: {e}")
        return pd.DataFrame()

def converter_excel_para_csv(caminhos_excel: List[str], caminho_csv: str):
    """
    Orquestra a leitura paralela de múltiplos arquivos Excel, consolida,
    padroniza os nomes das colunas e salva em um único arquivo CSV.
    """
    print(f"Criando arquivo CSV intermediário a partir de {len(caminhos_excel)} arquivo(s)...")
    inicio = time.time()
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        resultados = list(tqdm(executor.map(_processar_arquivo, caminhos_excel), 
                               total=len(caminhos_excel), 
                               desc="Consolidando arquivos Excel"))
    
    dfs_para_consolidar = [df for df in resultados if not df.empty]
    if not dfs_para_consolidar:
        print("Nenhum arquivo Excel válido foi processado. Encerrando.")
        return
    
    df_consolidado = pd.concat(dfs_para_consolidar, ignore_index=True)
    
    # Centraliza a renomeação de colunas aqui, antes de salvar o CSV.
    df_consolidado.rename(columns=MAPEAMENTO_COLUNAS, inplace=True)
    
    df_consolidado.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    
    fim = time.time()
    print(f"Consolidação para CSV concluída em {round(fim - inicio, 2)} segundos.")

def filtrar_csv(caminho_csv: str) -> pd.DataFrame:
    """
    Carrega o arquivo CSV (já com colunas padronizadas) e aplica uma série de
    tratamentos e filtros para limpar e preparar os dados para a agregação.
    """
    print(f"Iniciando filtragem do arquivo '{caminho_csv}'...")
    inicio = time.time()
    
    # Lê apenas as colunas necessárias (já com os nomes novos) para economizar memória.
    colunas_necessarias = list(MAPEAMENTO_COLUNAS.values())
    df = pd.read_csv(
        caminho_csv, usecols=colunas_necessarias,
        encoding='utf-8-sig', low_memory=False
    )
    
    # Tratamento e conversão de tipos para garantir consistência.
    df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
    df.dropna(subset=['ano'], inplace=True)
    df['ano'] = df['ano'].astype(int)
    
    df['cidade'] = df['cidade'].astype(str).str.strip().str.upper().replace(MAPA_DE_CIDADES)
    
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    for col in ["natureza do crime", "bairro", "artigo do crime", "delegacia", "mês"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Aplicação dos filtros definidos na seção de configuração.
    if FILTROS["ano"]:
        df = df[df['ano'].isin(FILTROS['ano'])]
    if FILTROS["cidade"]:
        df = df[df['cidade'].isin(FILTROS['cidade'])]
    
    fim = time.time()
    print(f"Filtragem e tratamento concluídos em {round(fim - inicio, 2)} segundos.")
    
    if df.empty:
        print("AVISO: Nenhum dado restou após a aplicação dos filtros.")
    
    return df

def agregar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe o DataFrame filtrado, agrupa pelas colunas definidas e conta as
    ocorrências, criando a coluna 'Quantidade'.
    """
    print("Iniciando agregação dos dados...")
    if df.empty:
        return df

    df_agregado = df.groupby(COLUNAS_PARA_AGRUPAR, observed=False).size().to_frame('Quantidade').reset_index()
    
    print("Agregação concluída.")
    return df_agregado

def formatar_excel_final(df_final: pd.DataFrame, caminho_excel: str):
    """
    Salva o DataFrame agregado em um arquivo Excel com formatação básica,
    como ajuste de largura das colunas e congelamento de painéis.
    """
    if df_final.empty:
        print("AVISO: Nenhum dado para gerar o Excel final.")
        return

    print(f"Formatando o arquivo Excel final com {len(df_final)} linhas...")
    with pd.ExcelWriter(caminho_excel, engine='openpyxl') as writer:
        df_final.to_excel(writer, sheet_name="Relatório Agregado", index=False)
        worksheet = writer.sheets["Relatório Agregado"]
        
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value)) for cell in column_cells if cell.value)
            worksheet.column_dimensions[column_cells[0].column_letter].width = max_length + 2
        
        worksheet.freeze_panes = 'A2'
        worksheet.auto_filter.ref = worksheet.dimensions
    
    print(f"Planilha Excel salva com sucesso em: '{caminho_excel}'")

# ==============================================================================
# BLOCO DE EXECUÇÃO PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    tempo_total_inicio = time.time()
    
    # Passo 1: Se o CSV intermediário não existir, cria-o a partir dos arquivos Excel.
    # Caso contrário, reutiliza o arquivo existente para acelerar a execução.
    if not os.path.exists(ARQUIVO_CSV_INTERMEDIARIO):
        converter_excel_para_csv(ARQUIVOS_EXCEL_ORIGINAIS, ARQUIVO_CSV_INTERMEDIARIO)
    else:
        print(f"Reutilizando arquivo CSV intermediário existente: '{ARQUIVO_CSV_INTERMEDIARIO}'.")

    # Passo 2: Carrega e filtra os dados.
    df_filtrado = filtrar_csv(ARQUIVO_CSV_INTERMEDIARIO)
    
    # Passo 3: Agrupa os dados filtrados para contagem.
    df_agregado = agregar_dados(df_filtrado)
    
    # Passo 4: Salva o resultado final no formato Excel.
    formatar_excel_final(df_agregado, ARQUIVO_EXCEL_FINAL_FORMATADO)
    
    print("-" * 50)
    print("PIPELINE EXECUTADO COM SUCESSO!")
    tempo_total_fim = time.time()
    print(f"Tempo total de execução: {round(tempo_total_fim - tempo_total_inicio, 2)} segundos.")