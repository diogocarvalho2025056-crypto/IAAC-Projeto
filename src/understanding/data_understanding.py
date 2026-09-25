import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# 1. Definir o caminho correto para a raiz do projeto (subir 2 níveis a partir de src/understanding)
pasta_script = Path(__file__).resolve().parent  # src/understanding
pasta_projeto = pasta_script.parent.parent      # Raiz: ProjetoIAAC

# Tentar encontrar o ficheiro em data/raw/ransom.csv, data/ransom.csv ou ransom.csv na raiz
candidatos_caminho = [
    pasta_projeto / "data" / "raw" / "ransom.csv",
    pasta_projeto / "data" / "ransom.csv",
    pasta_projeto / "ransom.csv"
]

ficheiro_csv = None
for caminho in candidatos_caminho:
    if caminho.exists():
        ficheiro_csv = caminho
        break

if ficheiro_csv is None:
    raise FileNotFoundError("Erro: O ficheiro 'ransom.csv' não foi encontrado nas pastas 'data/raw/', 'data/' ou na raiz.")

print(f" A carregar ficheiro a partir de: {ficheiro_csv}")
df = pd.read_csv(ficheiro_csv)

print("\n--- PRIMEIRAS LINHAS ---")
print(df.head())

print("\n--- DIMENSÃO DO DATASET ---")
print(f"Linhas: {df.shape[0]}, Colunas: {df.shape[1]}")

print("\n--- INFORMAÇÃO DO DATASET ---")
df.info()

print("\n--- VALORES EM FALTA ---")
print(f"Total de valores em falta: {df.isnull().sum().sum()}")

print("\n--- REGISTOS DUPLICADOS ---")
print(f"Total de duplicados: {df.duplicated().sum()}")

# Ajustado para a coluna 'Class' existente no dataset
print("\n--- DISTRIBUIÇÃO DAS CLASSES (Class) ---")
if "Class" in df.columns:
    print(df["Class"].value_counts())
    print("\n--- DISTRIBUIÇÃO PERCENTUAL ---")
    print(df["Class"].value_counts(normalize=True) * 100)

print("\n--- NÚMERO DE VALORES ÚNICOS POR COLUNA ---")
print(df.nunique())

print("\n--- VARIÁVEIS CONSTANTES (Apenas 1 valor único) ---")
constantes = [col for col in df.columns if df[col].nunique() == 1]
if constantes:
    print(constantes)
else:
    print("Nenhuma coluna constante encontrada.")

# Selecionar colunas numéricas reais do dataset PE/Ransom para análise estatística e gráficos
features_numericas = [
    col for col in [
        "registry_total", "network_connections", "processes_monitored", 
        "files_malicious", "dlls_calls", "apis"
    ] if col in df.columns
]

print("\n--- ESTATÍSTICA DESCRITIVA DAS FEATURES COMPORTAMENTAIS ---")
for coluna in features_numericas:
    print(f"\n--- {coluna} ---")
    print(f"Média: {df[coluna].mean():.2f}")
    print(f"Mediana: {df[coluna].median():.2f}")
    print(f"Desvio-padrão: {df[coluna].std():.2f}")
    print(f"Skewness: {df[coluna].skew():.2f}")
    print(f"Kurtosis: {df[coluna].kurt():.2f}")

# Gerar gráficos de histograma para as features selecionadas
for coluna in features_numericas:
    plt.figure(figsize=(8, 4))
    df[coluna].hist(bins=30, color='skyblue', edgecolor='black')
    plt.title(f"Distribuição de {coluna}")
    plt.xlabel(coluna)
    plt.ylabel("Frequência")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()