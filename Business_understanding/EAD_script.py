import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

pasta_projeto = Path(__file__).parent.parent

ficheiro_csv = pasta_projeto / "dataset" / "Malware_and_benign_recognition.csv"

df = pd.read_csv(ficheiro_csv)

print("--- PRIMEIRAS LINHAS ---")
print(df.head())

print("\n--- DIMENSÃO DO DATASET ---")
print(df.shape)

print("\n--- COLUNAS ---")
print(df.columns)

print("\n--- INFORMAÇÃO DO DATASET ---")
df.info()

print("\n--- VALORES EM FALTA ---")
print(df.isnull().sum())

print("\nTotal de valores em falta:")
print(df.isnull().sum().sum())

print("\n--- REGISTOS DUPLICADOS ---")
print(df.duplicated().sum())

print("\n--- DISTRIBUIÇÃO DAS CLASSES ---")
print(df["Malicious"].value_counts())

print("\n--- DISTRIBUIÇÃO PERCENTUAL ---")
print(df["Malicious"].value_counts(normalize=True) * 100)

print("\n--- ESTATÍSTICA DESCRITIVA ---")
print(df.describe())

print("\n--- NÚMERO DE VALORES ÚNICOS POR COLUNA ---")
print(df.nunique())

print("\n--- VARIÁVEIS CONSTANTES ---")

for coluna in df.columns:
    if df[coluna].nunique() == 1:
        print(coluna)

print("\n--- VERIFICAÇÃO DE REDUNDÂNCIA ---")

print(
    "NumberOfSections = SectionCount:",
    (df["NumberOfSections"] == df["SectionCount"]).all()
)

features = [
    "AvgSectionEntropy",
    "ImportedDLLs",
    "ImportedFunctions",
    "SizeOfCode",
    "SizeOfImage",
    "OverlaySize"
]

for coluna in features:
    print("\n---", coluna, "---")
    print(df[coluna].describe())

    for coluna in features:
        print("\n---", coluna, "---")
        print("Média:", df[coluna].mean())
        print("Mediana:", df[coluna].median())
        print("Desvio-padrão:", df[coluna].std())
        print("Skewness:", df[coluna].skew())
        print("Kurtosis:", df[coluna].kurt())

for coluna in features:
    plt.figure()
    df[coluna].hist(bins=30)

    plt.title("Distribuição de " + coluna)
    plt.xlabel(coluna)
    plt.ylabel("Frequência")

    plt.show()