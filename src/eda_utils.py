"""
Funções utilitárias para a Análise Exploratória de Dados (EDA)
do projeto Phishing Website Detector.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Pasta base do projeto (um nível acima de src/)
PASTA_PROJETO = Path(__file__).parent.parent


def carregar_dataset(nome_ficheiro="phishing.csv"):
    """Carrega o dataset a partir da pasta dataset/ do projeto."""
    caminho = PASTA_PROJETO / "dataset" / nome_ficheiro
    df = pd.read_csv(caminho)
    print(f"Dataset carregado: {df.shape[0]} registos × {df.shape[1]} colunas")
    return df


def resumo_geral(df):
    """Imprime um resumo geral do dataset."""
    print("=" * 60)
    print("RESUMO GERAL DO DATASET")
    print("=" * 60)
    print(f"\nDimensão: {df.shape[0]} registos × {df.shape[1]} colunas")
    print(f"\nColunas: {list(df.columns)}")
    print("\n--- TIPOS DE DADOS ---")
    print(df.dtypes)
    print("\n--- VALORES EM FALTA ---")
    missing = df.isnull().sum()
    print(missing[missing > 0] if missing.sum() > 0 else "Nenhum valor em falta")
    print(f"\nTotal de valores em falta: {missing.sum()}")
    print(f"\n--- REGISTOS DUPLICADOS ---")
    print(df.duplicated().sum())
    print("\n--- ESTATÍSTICA DESCRITIVA ---")
    print(df.describe())


def distribuicao_classes(df, target="class"):
    """Mostra a distribuição das classes."""
    print("=" * 60)
    print("DISTRIBUIÇÃO DAS CLASSES")
    print("=" * 60)
    print("\nContagem absoluta:")
    print(df[target].value_counts())
    print("\nDistribuição percentual:")
    print((df[target].value_counts(normalize=True) * 100).round(2))


def valores_unicos(df, drop_cols=None, target="class"):
    """Mostra o número de valores únicos por coluna."""
    cols = df.columns if drop_cols is None else df.drop(columns=drop_cols).columns
    print("=" * 60)
    print("NÚMERO DE VALORES ÚNICOS POR COLUNA")
    print("=" * 60)
    print(df[cols].nunique())


def variaveis_constantes(df, drop_cols=None):
    """Identifica variáveis constantes (apenas 1 valor único)."""
    cols = df.columns if drop_cols is None else df.drop(columns=drop_cols).columns
    constantes = [c for c in cols if df[c].nunique() == 1]
    print("=" * 60)
    print("VARIÁVEIS CONSTANTES")
    print("=" * 60)
    print(constantes if constantes else "Nenhuma variável constante encontrada")
    return constantes


def verificar_padrao_valores(df, target="class", drop_cols=None):
    """Verifica features que não seguem o padrão -1/0/1."""
    if drop_cols is None:
        drop_cols = []
    if target not in drop_cols:
        drop_cols = drop_cols + [target]

    print("=" * 60)
    print("FEATURES COM VALORES FORA DO PADRÃO (-1, 0, 1)")
    print("=" * 60)
    for coluna in df.drop(columns=drop_cols).columns:
        valores = sorted(df[coluna].unique())
        if valores != [-1, 0, 1]:
            print(f"  {coluna}: {valores}")


def distribuicao_features_categoricas(df, features=None, target="class", drop_cols=None):
    """Imprime a distribuição percentual de cada feature."""
    if features is None:
        drop = drop_cols + [target] if drop_cols else [target]
        features = df.drop(columns=drop).columns.tolist()

    print("=" * 60)
    print("DISTRIBUIÇÃO PERCENTUAL DE CADA FEATURE")
    print("=" * 60)
    for coluna in features:
        print(f"\n--- {coluna} ---")
        print((df[coluna].value_counts(normalize=True).sort_index() * 100).round(2))


def graficos_barras_features(df, features=None, target="class", drop_cols=None):
    """Gera gráficos de barras para cada feature."""
    if features is None:
        drop = drop_cols + [target] if drop_cols else [target]
        features = df.drop(columns=drop).columns.tolist()

    for coluna in features:
        plt.figure(figsize=(6, 4))
        df[coluna].value_counts().sort_index().plot(kind="bar", color="#20808D")
        plt.title(f"Distribuição de {coluna}")
        plt.xlabel(coluna)
        plt.ylabel("Frequência")
        plt.tight_layout()
        plt.show()


def analise_bivariada(df, features=None, target="class"):
    """Análise bivariada: feature por classe."""
    if features is None:
        features = df.drop(columns=[target]).columns.tolist()

    print("=" * 60)
    print("ANÁLISE BIVARIADA: FEATURE POR CLASSE")
    print("=" * 60)
    for coluna in features:
        print(f"\n--- {coluna} POR CLASSE ---")
        print(pd.crosstab(df[coluna], df[target], normalize="columns") * 100)


def graficos_bivariados(df, features=None, target="class"):
    """Gera gráficos de barras agrupados por classe."""
    if features is None:
        features = df.drop(columns=[target]).columns.tolist()

    for coluna in features:
        plt.figure(figsize=(6, 4))
        ct = pd.crosstab(df[coluna], df[target])
        ct.columns = ["Phishing (-1)", "Legítimo (1)"]
        ct.plot(kind="bar", ax=plt.gca(), color=["#A13544", "#437A22"])
        plt.title(f"{coluna} por Classe")
        plt.xlabel(coluna)
        plt.ylabel("Nº de registos")
        plt.tight_layout()
        plt.show()


def correlacao_pearson(df, target="class", drop_cols=None):
    """Calcula e mostra a correlação de Pearson com a variável alvo."""
    if drop_cols is None:
        drop_cols = []
    dados = df.drop(columns=drop_cols)
    corr = dados.corr(method="pearson")
    print("=" * 60)
    print("CORRELAÇÃO DE PEARSON COM A VARIÁVEL ALVO")
    print("=" * 60)
    print(corr[target].sort_values(ascending=False).round(4))
    return corr


def correlacao_spearman(df, target="class", drop_cols=None):
    """Calcula e mostra a correlação de Spearman com a variável alvo."""
    if drop_cols is None:
        drop_cols = []
    dados = df.drop(columns=drop_cols)
    corr = dados.corr(method="spearman")
    print("=" * 60)
    print("CORRELAÇÃO DE SPEARMAN COM A VARIÁVEL ALVO")
    print("=" * 60)
    print(corr[target].sort_values(ascending=False).round(4))
    return corr


def matriz_correlacao(df, method="pearson", target="class", drop_cols=None):
    """Gera um heatmap da matriz de correlação."""
    if drop_cols is None:
        drop_cols = []
    dados = df.drop(columns=drop_cols)
    corr = dados.corr(method=method)

    plt.figure(figsize=(16, 12))
    sns.heatmap(corr, cmap="coolwarm", center=0, square=True, linewidths=0.5)
    plt.title(f"Matriz de Correlação de {method.capitalize()}")
    plt.tight_layout()
    plt.show()
    return corr


def grafico_correlacao_alvo(df, method="pearson", target="class", drop_cols=None):
    """Gera um gráfico de barras horizontais da correlação com o target."""
    if drop_cols is None:
        drop_cols = []
    dados = df.drop(columns=drop_cols)
    corr = dados.corr(method=method)
    corr_target = corr[target].drop(target).dropna().sort_values()

    plt.figure(figsize=(10, 8))
    corr_target.plot(kind="barh", color="#20808D")
    plt.title(f"Correlação de {method.capitalize()} com a variável {target}")
    plt.xlabel("Coeficiente de correlação")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.show()
    return corr_target


def pares_altamente_correlacionados(df, threshold=0.80, method="pearson", target="class", drop_cols=None):
    """Identifica pares de features com correlação acima do limiar."""
    if drop_cols is None:
        drop_cols = []
    dados = df.drop(columns=drop_cols)
    corr = dados.corr(method=method).abs()

    print("=" * 60)
    print(f"PARES DE FEATURES COM |CORRELAÇÃO| >= {threshold} ({method})")
    print("=" * 60)
    encontrados = False
    for i in range(len(corr.columns)):
        for j in range(i):
            valor = corr.iloc[i, j]
            if valor >= threshold:
                print(f"  {corr.columns[i]} <-> {corr.columns[j]}: {round(valor, 4)}")
                encontrados = True
    if not encontrados:
        print("  Nenhum par encontrado acima do limiar.")


def desequilibrio_categorias(df, target="class", drop_cols=None):
    """Analisa o desequilíbrio de categorias em cada feature."""
    if drop_cols is None:
        drop_cols = []
    if target not in drop_cols:
        drop_cols = drop_cols + [target]

    print("=" * 60)
    print("DESEQUILÍBRIO DE CATEGORIAS POR FEATURE")
    print("=" * 60)
    for coluna in df.drop(columns=drop_cols).columns:
        proporcoes = df[coluna].value_counts(normalize=True)
        cat_dominante = proporcoes.idxmax()
        pct_dominante = proporcoes.max() * 100
        print(f"  {coluna}: categoria dominante = {cat_dominante} ({round(pct_dominante, 1)}% dos registos)")
