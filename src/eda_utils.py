import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def resumo_dataset(df):
    print("--- DIMENSÃO ---")
    print(df.shape)

    print("\n--- TIPOS DE DADOS ---")
    df.info()

    print("\n--- VALORES EM FALTA ---")
    print(df.isnull().sum())

    print("\n--- DUPLICADOS ---")
    print(df.duplicated().sum())


def distribuicao_target(df, target):
    print("--- DISTRIBUIÇÃO DAS CLASSES ---")
    print(df[target].value_counts())

    print("\n--- DISTRIBUIÇÃO PERCENTUAL ---")
    print(df[target].value_counts(normalize=True) * 100)


def estatistica_descritiva(df):
    print(df.describe())


def valores_unicos(df):
    print(df.nunique())


def variaveis_constantes(df):
    constantes = []

    for coluna in df.columns:
        if df[coluna].nunique() == 1:
            constantes.append(coluna)

    return constantes


def analise_univariada(df, features):
    for coluna in features:
        print("\n---", coluna, "---")

        print("Média:", df[coluna].mean())
        print("Mediana:", df[coluna].median())
        print("Desvio-padrão:", df[coluna].std())
        print("Skewness:", df[coluna].skew())
        print("Kurtosis:", df[coluna].kurt())


def histogramas(df, features, bins=30):
    for coluna in features:
        plt.figure()

        df[coluna].hist(bins=bins)

        plt.title("Distribuição de " + coluna)
        plt.xlabel(coluna)
        plt.ylabel("Frequência")

        plt.tight_layout()
        plt.show()


def comparacao_medias(df, target, features):
    comparacao = df.groupby(target)[features].mean().T

    return comparacao


def comparacao_medianas(df, target, features):
    comparacao = df.groupby(target)[features].median().T

    return comparacao


def boxplots_por_classe(df, target, features, nomes_classes):
    classes = sorted(df[target].unique())

    for coluna in features:
        dados = []

        for classe in classes:
            dados.append(
                df[df[target] == classe][coluna]
            )

        plt.figure()

        plt.boxplot(
            dados,
            tick_labels=nomes_classes
        )

        plt.title(coluna + " por Classe")
        plt.xlabel("Classe")
        plt.ylabel(coluna)

        plt.tight_layout()
        plt.show()


def correlacao_pearson(df, coluna_texto=None):
    dados = df.copy()

    if coluna_texto is not None:
        dados = dados.drop(columns=[coluna_texto])

    return dados.corr(method="pearson")


def correlacao_spearman(df, coluna_texto=None):
    dados = df.copy()

    if coluna_texto is not None:
        dados = dados.drop(columns=[coluna_texto])

    return dados.corr(method="spearman")


def heatmap_correlacao(correlacao, titulo):
    plt.figure(figsize=(16, 12))

    sns.heatmap(
        correlacao,
        cmap="coolwarm",
        center=0
    )

    plt.title(titulo)
    plt.tight_layout()
    plt.show()


def correlacao_com_target(correlacao, target):
    return (
        correlacao[target]
        .drop(target)
        .dropna()
        .sort_values()
    )


def grafico_correlacao_target(correlacao_target, titulo):
    plt.figure(figsize=(10, 8))

    correlacao_target.plot(kind="barh")

    plt.title(titulo)
    plt.xlabel("Coeficiente de correlação")
    plt.ylabel("Feature")

    plt.tight_layout()
    plt.show()


def pares_alta_correlacao(correlacao, limite=0.80):
    correlacao_abs = correlacao.abs()

    resultados = []

    for i in range(len(correlacao_abs.columns)):
        for j in range(i):
            valor = correlacao_abs.iloc[i, j]

            if valor >= limite:
                coluna1 = correlacao_abs.columns[i]
                coluna2 = correlacao_abs.columns[j]

                resultados.append(
                    (coluna1, coluna2, valor)
                )

    return resultados


def detectar_outliers_iqr(df, features):
    resultados = []

    for coluna in features:
        q1 = df[coluna].quantile(0.25)
        q3 = df[coluna].quantile(0.75)

        iqr = q3 - q1

        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr

        outliers = df[
            (df[coluna] < limite_inferior)
            |
            (df[coluna] > limite_superior)
        ]

        quantidade = len(outliers)
        percentagem = quantidade / len(df) * 100

        resultados.append(
            {
                "Feature": coluna,
                "Outliers": quantidade,
                "Percentagem": round(percentagem, 2)
            }
        )

    return pd.DataFrame(resultados)