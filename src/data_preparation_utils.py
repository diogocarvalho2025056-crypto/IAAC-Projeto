"""
Funções utilitárias para a fase de Data Preparation
do projeto Phishing Website Detector.
"""

import pandas as pd
from pathlib import Path

# Pasta base do projeto (um nível acima de src/)
PASTA_PROJETO = Path(__file__).parent.parent


def carregar_dataset(nome_ficheiro="phishing.csv"):
    """Carrega o dataset a partir da pasta dataset/ do projeto."""
    caminho = PASTA_PROJETO / "dataset" / nome_ficheiro
    df = pd.read_csv(caminho)
    print(f"Dataset carregado: {df.shape[0]} registos × {df.shape[1]} colunas")
    return df


def remover_coluna(df, coluna):
    """Remove uma coluna do dataset, se existir."""
    if coluna in df.columns:
        df = df.drop(columns=[coluna])
        print(f"Coluna '{coluna}' removida. Novas dimensões: {df.shape}")
    else:
        print(f"Coluna '{coluna}' não encontrada.")
    return df


def verificar_valores_em_falta(df):
    """Verifica e imprime o total de valores em falta."""
    missing = df.isnull().sum()
    total = missing.sum()
    print(f"Total de valores em falta: {total}")
    if total > 0:
        print(missing[missing > 0])
    return total


def verificar_duplicados(df):
    """Verifica e imprime o número de registos duplicados."""
    n_dup = df.duplicated().sum()
    print(f"Registos duplicados: {n_dup}")
    return n_dup


def identificar_perfis_contraditorios(df, target="class"):
    """
    Identifica perfis (combinações de features) que aparecem
    associados a rótulos diferentes (legítimo e phishing).
    """
    features = df.drop(columns=[target])
    perfis = df.groupby(list(features.columns))
    contagem = perfis[target].nunique()

    perfis_conflito = contagem[contagem > 1]
    n_perfis = len(perfis_conflito)

    # Registos envolvidos
    mascaras = []
    for nome_grupo, _ in perfis_conflito.items():
        mascara = (features == pd.Series(nome_grupo, index=features.columns)).all(axis=1)
        mascaras.append(mascara)
    if mascaras:
        mascara_total = pd.concat(mascaras, axis=1).any(axis=1)
        n_registos = mascara_total.sum()
    else:
        mascara_total = pd.Series(False, index=df.index)
        n_registos = 0

    print(f"Perfis com rótulos contraditórios: {n_perfis}")
    print(f"Registos envolvidos em perfis contraditórios: {n_registos}")
    return n_perfis, n_registos, mascara_total


def remover_perfis_contraditorios(df, target="class"):
    """Remove registos envolvidos em perfis contraditórios."""
    _, _, mascara = identificar_perfis_contraditorios(df, target)
    df_limpo = df[~mascara].copy()
    print(f"Registos removidos: {len(df) - len(df_limpo)}")
    print(f"Dimensão após remoção: {df_limpo.shape}")
    return df_limpo


def remover_duplicados(df):
    """Remove registos duplicados completos."""
    n_antes = len(df)
    df = df.drop_duplicates().copy()
    n_depois = len(df)
    print(f"Duplicados removidos: {n_antes - n_depois}")
    print(f"Dimensão após remoção: {df.shape}")
    return df


def separar_features_target(df, target="class"):
    """Separa as variáveis de entrada (X) da variável alvo (y)."""
    X = df.drop(columns=[target])
    y = df[target]
    print(f"X: {X.shape}")
    print(f"y: {y.shape}")
    return X, y


def dividir_treino_teste(X, y, test_size=0.2, random_state=42):
    """Divisão estratificada entre treino e teste."""
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"Treino: X_train={X_train.shape}, y_train={y_train.shape}")
    print(f"Teste:  X_test={X_test.shape}, y_test={y_test.shape}")
    print(f"\nDistribuição treino:\n{(y_train.value_counts(normalize=True)*100).round(2)}")
    print(f"\nDistribuição teste:\n{(y_test.value_counts(normalize=True)*100).round(2)}")
    return X_train, X_test, y_train, y_test


def guardar_dataset_preparado(df, nome_ficheiro="phishing_prepared.csv"):
    """Guarda o dataset preparado na pasta dataset/."""
    caminho = PASTA_PROJETO / "dataset" / nome_ficheiro
    df.to_csv(caminho, index=False)
    print(f"Dataset preparado guardado em: {caminho}")
    print(f"Dimensão final: {df.shape}")


def resumo_preparacao(df_original, df_preparado, target="class"):
    """Imprime um resumo comparativo antes/depois da preparação."""
    print("=" * 60)
    print("RESUMO DA DATA PREPARATION")
    print("=" * 60)
    print(f"\nDataset original: {df_original.shape[0]} registos × {df_original.shape[1]} colunas")
    print(f"Dataset preparado: {df_preparado.shape[0]} registos × {df_preparado.shape[1]} colunas")
    print(f"Registos removidos: {df_original.shape[0] - df_preparado.shape[0]}")
    print(f"\nDistribuição original:")
    print(df_original[target].value_counts())
    print(f"\nDistribuição preparada:")
    print(df_preparado[target].value_counts())
    print(f"\nValores em falta: {df_preparado.isnull().sum().sum()}")
    print(f"Duplicados: {df_preparado.duplicated().sum()}")
