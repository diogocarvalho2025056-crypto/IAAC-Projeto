import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


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

print("\n--- ANÁLISE BIVARIADA ---")

features = [
    "AvgSectionEntropy",
    "ImportedDLLs",
    "ImportedFunctions",
    "SizeOfCode",
    "SizeOfImage",
    "OverlaySize"
]

for coluna in features:
    print("\n---", coluna, "POR CLASSE ---")

    print(
        df.groupby("Malicious")[coluna].describe()
    )

print("\n--- MÉDIAS POR CLASSE ---")

for coluna in features:
    medias = df.groupby("Malicious")[coluna].mean()

    print("\n", coluna)
    print("Benigno:", medias[0])
    print("Malware:", medias[1])

for coluna in features:
    benigno = df[df["Malicious"] == 0][coluna]
    malware = df[df["Malicious"] == 1][coluna]

    plt.figure()

    plt.boxplot(
        [benigno, malware],
        tick_labels=["Benigno", "Malware"]
    )

    plt.title(coluna + " por Classe")
    plt.xlabel("Classe")
    plt.ylabel(coluna)

    plt.show()

plt.figure()

df[df["Malicious"] == 0]["AvgSectionEntropy"].hist(
    bins=30,
    alpha=0.5,
    label="Benigno"
)

df[df["Malicious"] == 1]["AvgSectionEntropy"].hist(
    bins=30,
    alpha=0.5,
    label="Malware"
)

plt.title("Distribuição de AvgSectionEntropy por Classe")
plt.xlabel("AvgSectionEntropy")
plt.ylabel("Frequência")
plt.legend()

plt.show()

comparacao = df.groupby("Malicious")[features].mean().T

comparacao.columns = ["Benigno", "Malware"]

print("\n--- COMPARAÇÃO DAS MÉDIAS ---")
print(comparacao)

print("\n--- COMPARAÇÃO DAS MEDIANAS ---")

comparacao_mediana = df.groupby("Malicious")[features].median().T

comparacao_mediana.columns = ["Benigno", "Malware"]

print(comparacao_mediana)

print("\n--- CORRELAÇÃO DE PEARSON COM MALICIOUS ---")

pearson = df.drop(columns=["File"]).corr(method="pearson")

print(
    pearson["Malicious"]
    .sort_values(ascending=False)
)

print("\n--- CORRELAÇÃO DE SPEARMAN COM MALICIOUS ---")

spearman = df.drop(columns=["File"]).corr(method="spearman")

print(
    spearman["Malicious"]
    .sort_values(ascending=False)
)

dados_numericos = df.drop(columns=["File"])

correlacao = dados_numericos.corr(method="pearson")

plt.figure(figsize=(16, 12))

sns.heatmap(
    correlacao,
    cmap="coolwarm",
    center=0
)

plt.title("Matriz de Correlação de Pearson")
plt.tight_layout()
plt.show()

correlacao_spearman = dados_numericos.corr(method="spearman")

plt.figure(figsize=(16, 12))

sns.heatmap(
    correlacao_spearman,
    cmap="coolwarm",
    center=0
)

plt.title("Matriz de Correlação de Spearman")
plt.tight_layout()
plt.show()

corr_target = (
    correlacao["Malicious"]
    .drop("Malicious")
    .dropna()
    .sort_values()
)

plt.figure(figsize=(10, 8))

corr_target.plot(kind="barh")

plt.title("Correlação de Pearson com a variável Malicious")
plt.xlabel("Coeficiente de correlação")
plt.ylabel("Feature")

plt.tight_layout()
plt.show()

corr_target_spearman = (
    correlacao_spearman["Malicious"]
    .drop("Malicious")
    .dropna()
    .sort_values()
)

plt.figure(figsize=(10, 8))

corr_target_spearman.plot(kind="barh")

plt.title("Correlação de Spearman com a variável Malicious")
plt.xlabel("Coeficiente de correlação")
plt.ylabel("Feature")

plt.tight_layout()
plt.show()


print("\n--- PARES DE FEATURES ALTAMENTE CORRELACIONADAS ---")

correlacao_abs = correlacao.abs()

for i in range(len(correlacao_abs.columns)):
    for j in range(i):
        valor = correlacao_abs.iloc[i, j]

        if valor >= 0.80:
            coluna1 = correlacao_abs.columns[i]
            coluna2 = correlacao_abs.columns[j]

            print(
                coluna1,
                "<->",
                coluna2,
                ":",
                round(valor, 3)
            )

print("\n--- PARES COM SPEARMAN >= 0.80 ---")

spearman_abs = correlacao_spearman.abs()

for i in range(len(spearman_abs.columns)):
    for j in range(i):
        valor = spearman_abs.iloc[i, j]

        if valor >= 0.80:
            coluna1 = spearman_abs.columns[i]
            coluna2 = spearman_abs.columns[j]

            print(
                coluna1,
                "<->",
                coluna2,
                ":",
                round(valor, 3)
            )

print("\n--- OUTLIERS PELO MÉTODO IQR ---")

for coluna in features:

    Q1 = df[coluna].quantile(0.25)
    Q3 = df[coluna].quantile(0.75)

    IQR = Q3 - Q1

    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    outliers = df[
        (df[coluna] < limite_inferior) |
        (df[coluna] > limite_superior)
    ]

    print(
        coluna,
        ":",
        len(outliers),
        "outliers"
    )

print("\n--- PERCENTAGEM DE OUTLIERS ---")

for coluna in features:

    Q1 = df[coluna].quantile(0.25)
    Q3 = df[coluna].quantile(0.75)

    IQR = Q3 - Q1

    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    outliers = df[
        (df[coluna] < limite_inferior) |
        (df[coluna] > limite_superior)
    ]

    percentagem = len(outliers) / len(df) * 100

    print(
        coluna,
        ":",
        round(percentagem, 2),
        "%"
    )