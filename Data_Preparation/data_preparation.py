"""
Script de Data Preparation - Phishing Website Detector
======================================================

Este script executa todas as etapas de preparação dos dados descritas
no documento "Data Preparation — Phishing Website Detector.docx".

Etapas:
  1. Carregamento do dataset original
  2. Remoção da coluna Index (não preditiva)
  3. Verificação de valores em falta
  4. Verificação de duplicados após remoção do Index
  5. Identificação e remoção de perfis contraditórios
  6. Remoção de duplicados completos
  7. Separação entre features (X) e target (y)
  8. Divisão estratificada treino/teste (80/20)
  9. Análise de outliers (apenas diagnóstico - sem remoção)
 10. Análise de features altamente correlacionadas
 11. Avaliação da necessidade de scaling
 12. Guardar dataset preparado

Execução:
  python data_preparation.py
"""

import sys
from pathlib import Path

# Adicionar a pasta src ao path para importar utilitários
PASTA_PROJETO = Path(__file__).parent.parent
sys.path.insert(0, str(PASTA_PROJETO / "src"))

from data_preparation_utils import (
    carregar_dataset,
    remover_coluna,
    verificar_valores_em_falta,
    verificar_duplicados,
    identificar_perfis_contraditorios,
    remover_perfis_contraditorios,
    remover_duplicados,
    separar_features_target,
    dividir_treino_teste,
    guardar_dataset_preparado,
    resumo_preparacao,
)


def analisar_outliers(df, target="class"):
    """
    Análise de outliers usando o método IQR.
    No caso deste dataset, as features são categóricas ordinais (-1, 0, 1),
    pelo que os 'outliers' identificados correspondem simplesmente aos
    valores menos frequentes e NÃO devem ser removidos.
    """
    import pandas as pd

    print("\n" + "=" * 60)
    print("ANÁLISE DE OUTLIERS (IQR) - APENAS DIAGNÓSTICO")
    print("=" * 60)
    print("\nNota: As features são categóricas ordinais (-1, 0, 1).")
    print("Os 'outliers' identificados são valores legítimos e NÃO serão removidos.\n")

    features = df.drop(columns=[target])
    total_outliers = 0

    for coluna in features.columns:
        Q1 = df[coluna].quantile(0.25)
        Q3 = df[coluna].quantile(0.75)
        IQR = Q3 - Q1
        lim_inf = Q1 - 1.5 * IQR
        lim_sup = Q3 + 1.5 * IQR
        n_outliers = ((df[coluna] < lim_inf) | (df[coluna] > lim_sup)).sum()

        if n_outliers > 0:
            print(f"  {coluna}: {n_outliers} valores fora dos limites IQR")
            total_outliers += n_outliers

    print(f"\nTotal de valores sinalizados: {total_outliers}")
    print("Decisão: NENHUMA remoção efetuada (valores são categorias legítimas)")


def analisar_correlacao_features(df, threshold=0.80, target="class"):
    """Identifica pares de features altamente correlacionadas."""
    print("\n" + "=" * 60)
    print(f"FEATURES ALTAMENTE CORRELACIONADAS (|r| >= {threshold})")
    print("=" * 60)

    corr = df.drop(columns=[target]).corr(method="pearson").abs()
    pares = []

    for i in range(len(corr.columns)):
        for j in range(i):
            valor = corr.iloc[i, j]
            if valor >= threshold:
                pares.append((corr.columns[i], corr.columns[j], round(valor, 4)))

    if pares:
        print(f"\n{'Feature 1':<25} {'Feature 2':<25} {'Correlação'}")
        print("-" * 70)
        for f1, f2, v in pares:
            print(f"{f1:<25} {f2:<25} {v}")
        print(f"\nDecisão: Variáveis mantidas. A remoção será avaliada")
        print("posteriormente com base no desempenho dos modelos.")
    else:
        print("Nenhum par encontrado acima do limiar.")


def avaliar_scaling(df, target="class"):
    """Avalia a necessidade de scaling/standardização."""
    print("\n" + "=" * 60)
    print("AVALIAÇÃO DE SCALING / STANDARDIZAÇÃO")
    print("=" * 60)

    features = df.drop(columns=[target])
    min_vals = features.min()
    max_vals = features.max()

    print(f"\nValores mínimos por feature:")
    print(f"  Mínimo global: {min_vals.min()}")
    print(f"  Máximo global: {max_vals.max()}")

    nao_padrao = [(c, sorted(features[c].unique())) for c in features.columns
                  if sorted(features[c].unique()) != [-1, 0, 1]]

    if nao_padrao:
        print("\nFeatures com valores fora do padrão [-1, 0, 1]:")
        for col, vals in nao_padrao:
            print(f"  {col}: {vals}")

    print(f"\nDecisão: Scaling NÃO aplicado.")
    print("Todas as features já se encontram numa escala comparável [-1, 0, 1].")
    print("O StandardScaler seria redundante para este dataset.")


def main():
    print("=" * 60)
    print("DATA PREPARATION - PHISHING WEBSITE DETECTOR")
    print("=" * 60)

    # 1. Carregar dataset original
    print("\n--- 1. CARREGAMENTO DO DATASET ---")
    df = carregar_dataset("phishing.csv")

    # Guardar referência ao dataset original
    df_original = df.copy()

    # 2. Remover coluna Index
    print("\n--- 2. REMOÇÃO DA COLUNA INDEX ---")
    df = remover_coluna(df, "Index")

    # 3. Verificar valores em falta
    print("\n--- 3. VERIFICAÇÃO DE VALORES EM FALTA ---")
    verificar_valores_em_falta(df)

    # 4. Verificar duplicados após remoção do Index
    print("\n--- 4. VERIFICAÇÃO DE DUPLICADOS ---")
    n_dup = verificar_duplicados(df)
    print(f"  (Duplicados surgem porque o Index tornava registos únicos)")

    # 5. Identificar e remover perfis contraditórios
    print("\n--- 5. ANÁLISE E REMOÇÃO DE PERFIS CONTRADITÓRIOS ---")
    df = remover_perfis_contraditorios(df, target="class")

    # 6. Remover duplicados completos
    print("\n--- 6. REMOÇÃO DE DUPLICADOS ---")
    df = remover_duplicados(df)

    # 7. Verificar qualidade após limpeza
    print("\n--- 7. VERIFICAÇÃO DE QUALIDADE APÓS LIMPEZA ---")
    verificar_valores_em_falta(df)
    verificar_duplicados(df)

    # 8. Análise de outliers (apenas diagnóstico)
    print("\n--- 8. ANÁLISE DE OUTLIERS ---")
    analisar_outliers(df, target="class")

    # 9. Análise de features correlacionadas
    print("\n--- 9. FEATURES ALTAMENTE CORRELACIONADAS ---")
    analisar_correlacao_features(df, threshold=0.80, target="class")

    # 10. Avaliação de scaling
    print("\n--- 10. AVALIAÇÃO DE SCALING ---")
    avaliar_scaling(df, target="class")

    # 11. Guardar dataset preparado
    print("\n--- 11. GUARDAR DATASET PREPARADO ---")
    guardar_dataset_preparado(df, "phishing_prepared.csv")

    # 12. Separação features/target e divisão treino/teste
    print("\n--- 12. SEPARAÇÃO FEATURES / TARGET ---")
    X, y = separar_features_target(df, target="class")

    print("\n--- 13. DIVISÃO TREINO / TESTE ---")
    X_train, X_test, y_train, y_test = dividir_treino_teste(X, y, test_size=0.2, random_state=42)

    # Resumo final
    print("\n" + "=" * 60)
    resumo_preparacao(df_original, df, target="class")

    print("\nData Preparation concluída com sucesso.")


if __name__ == "__main__":
    main()
