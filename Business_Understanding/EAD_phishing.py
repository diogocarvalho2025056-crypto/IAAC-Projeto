import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


pasta_projeto = Path(__file__).parent.parent

ficheiro_csv = pasta_projeto / "dataset" / "phishing.csv"

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
print(df["class"].value_counts())

print("\n--- DISTRIBUIÇÃO PERCENTUAL ---")
print(df["class"].value_counts(normalize=True) * 100)

print("\n--- ESTATÍSTICA DESCRITIVA ---")
print(df.describe())

print("\n--- NÚMERO DE VALORES ÚNICOS POR COLUNA ---")
print(df.nunique())

print("\n--- VARIÁVEIS CONSTANTES ---")

for coluna in df.columns:
    if df[coluna].nunique() == 1:
        print(coluna)

print("\n--- FEATURES COM APENAS 2 VALORES (fora do padrão -1/0/1) ---")

for coluna in df.drop(columns=["Index", "class"]).columns:
    valores = sorted(df[coluna].unique())
    if valores != [-1, 0, 1]:
        print(coluna, ":", valores)

print("\n--- VERIFICAÇÃO DE REDUNDÂNCIA (HTTPS vs HTTPSDomainURL) ---")

print(
    "HTTPS = HTTPSDomainURL:",
    (df["HTTPS"] == df["HTTPSDomainURL"]).all()
)

# Features a analisar em detalhe: as que a análise inicial (Pearson) apontou
# como mais associadas à classe, mais duas com correlação muito baixa para
# comparação
features = [
    "HTTPS",
    "AnchorURL",
    "PrefixSuffix-",
    "WebsiteTraffic",
    "Favicon",
    "UsingPopupWindow"
]

for coluna in features:
    print("\n---", coluna, "---")
    print(df[coluna].value_counts(normalize=True).sort_index() * 100)

print("\n--- DISTRIBUIÇÃO DE CATEGORIAS POR FEATURE (gráficos de barras) ---")

for coluna in features:
    plt.figure()
    df[coluna].value_counts().sort_index().plot(kind="bar")

    plt.title("Distribuição de " + coluna)
    plt.xlabel(coluna)
    plt.ylabel("Frequência")

    plt.show()

print("\n--- ANÁLISE BIVARIADA: FEATURE POR CLASSE ---")

for coluna in features:
    print("\n---", coluna, "POR CLASSE ---")

    print(
        pd.crosstab(df[coluna], df["class"], normalize="columns") * 100
    )

print("\n--- GRÁFICOS DE BARRAS AGRUPADOS POR CLASSE ---")

for coluna in features:
    plt.figure()

    ct = pd.crosstab(df[coluna], df["class"])
    ct.columns = ["Phishing (-1)", "Legítimo (1)"]
    ct.plot(kind="bar")

    plt.title(coluna + " por Classe")
    plt.xlabel(coluna)
    plt.ylabel("Nº de registos")

    plt.tight_layout()
    plt.show()

print("\n--- CORRELAÇÃO DE PEARSON COM CLASS ---")

pearson = df.drop(columns=["Index"]).corr(method="pearson")

print(
    pearson["class"]
    .sort_values(ascending=False)
)

print("\n--- CORRELAÇÃO DE SPEARMAN COM CLASS ---")

spearman = df.drop(columns=["Index"]).corr(method="spearman")

print(
    spearman["class"]
    .sort_values(ascending=False)
)

dados_numericos = df.drop(columns=["Index"])

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
    correlacao["class"]
    .drop("class")
    .dropna()
    .sort_values()
)

plt.figure(figsize=(10, 8))

corr_target.plot(kind="barh")

plt.title("Correlação de Pearson com a variável class")
plt.xlabel("Coeficiente de correlação")
plt.ylabel("Feature")

plt.tight_layout()
plt.show()

corr_target_spearman = (
    correlacao_spearman["class"]
    .drop("class")
    .dropna()
    .sort_values()
)

plt.figure(figsize=(10, 8))

corr_target_spearman.plot(kind="barh")

plt.title("Correlação de Spearman com a variável class")
plt.xlabel("Coeficiente de correlação")
plt.ylabel("Feature")

plt.tight_layout()
plt.show()


print("\n--- PARES DE FEATURES ALTAMENTE CORRELACIONADAS (Pearson >= 0.80) ---")

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

# Nota: o método de outliers por IQR (usado no script original) não é
# adequado aqui, porque as features do phishing.csv são categóricas
# ordinais (-1/0/1), e não variáveis contínuas como entropia ou tamanho
# em bytes. Em vez de outliers, o que importa verificar é o desequilíbrio
# de categorias dentro de cada feature.

print("\n--- DESEQUILÍBRIO DE CATEGORIAS POR FEATURE ---")

for coluna in df.drop(columns=["Index", "class"]).columns:
    proporcoes = df[coluna].value_counts(normalize=True)
    categoria_dominante = proporcoes.idxmax()
    percentagem_dominante = proporcoes.max() * 100

    print(
        coluna,
        ": categoria dominante =", categoria_dominante,
        "(", round(percentagem_dominante, 1), "% dos registos )"
    )
