"""
Script de Model Building - Phishing Website Detector
====================================================

Este script executa todas as etapas de modelação do projeto:
  1. Carregamento do dataset preparado
  2. Separação features/target e divisão treino/teste
  3. Treino de 4 modelos: Logistic Regression, Decision Tree, Random Forest, XGBoost
  4. Cross-validation (5-fold)
  5. Avaliação no conjunto de teste (Accuracy, Precision, Recall, F1, matriz de confusão)
  6. Comparação treino vs teste (overfitting)
  7. Análise de feature importance
  8. Geração de gráficos comparativos (matrizes de confusão, curvas ROC, PR)
  9. Guardar modelos treinados

Modelos:
  - Logistic Regression (baseline)
  - Decision Tree
  - Random Forest
  - XGBoost (obrigatório)

Referências:
  - GeeksforGeeks — Machine Learning Tutorial
    Module 6: Supervised Learning → Ensemble Learning → XGBoost
    Module 7: Model Evaluation → Confusion Matrix, Precision, Recall, F1-Score, AUC-ROC
    https://www.geeksforgeeks.org/machine-learning/machine-learning-tutorial/

Execução:
  python modeling.py
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Adicionar a pasta src ao path
PASTA_PROJETO = Path(__file__).parent.parent
sys.path.insert(0, str(PASTA_PROJETO / "src"))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from model_utils import (
    carregar_dataset_preparado,
    separar_features_target,
    dividir_treino_teste,
    criar_logistic_regression,
    criar_decision_tree,
    criar_random_forest,
    criar_xgboost,
    treinar_modelo,
    prever,
    prever_probabilidades,
    avaliar_modelo,
    cross_validation,
    comparar_treino_teste,
    comparar_modelos,
    importancia_features,
    grafico_matriz_confusao,
    grafico_comparacao,
    grafico_curvas_roc,
    grafico_curvas_pr,
    grafico_feature_importance,
    guardar_modelo,
)


def main():
    print("=" * 60)
    print("MODEL BUILDING - PHISHING WEBSITE DETECTOR")
    print("=" * 60)

    # --------------------------------------------------
    # 1. CARREGAR DATASET PREPARADO
    # --------------------------------------------------
    print("\n--- 1. CARREGAR DATASET PREPARADO ---")
    df = carregar_dataset_preparado("phishing_prepared.csv")

    # --------------------------------------------------
    # 2. SEPARAR FEATURES E TARGET
    # --------------------------------------------------
    print("\n--- 2. SEPARAR FEATURES E TARGET ---")
    X, y = separar_features_target(df, "class")

    # Mapear classes: -1 -> 0 (phishing), 1 -> 1 (legítimo)
    # Necessário para compatibilidade com XGBoost
    y = y.map({-1: 0, 1: 1})

    # --------------------------------------------------
    # 3. DIVIDIR TREINO E TESTE
    # --------------------------------------------------
    print("\n--- 3. DIVIDIR TREINO E TESTE ---")
    X_train, X_test, y_train, y_test = dividir_treino_teste(X, y)

    nomes_features = X.columns.tolist()

    # --------------------------------------------------
    # 4. CRIAR MODELOS
    # --------------------------------------------------
    print("\n--- 4. CRIAR MODELOS ---")

    logistic_regression = criar_logistic_regression()
    decision_tree = criar_decision_tree()
    random_forest = criar_random_forest()
    xgboost = criar_xgboost()

    modelos = [
        ("Logistic Regression", logistic_regression),
        ("Decision Tree", decision_tree),
        ("Random Forest", random_forest),
        ("XGBoost", xgboost),
    ]

    for nome, modelo in modelos:
        print(f"  • {nome}: {modelo.__class__.__name__}")

    # --------------------------------------------------
    # 5. TREINAR MODELOS
    # --------------------------------------------------
    print("\n--- 5. TREINAR MODELOS ---")

    for nome, modelo in modelos:
        treinar_modelo(modelo, X_train, y_train)
        print(f"  • {nome} treinado.")

    # --------------------------------------------------
    # 6. FAZER PREVISÕES
    # --------------------------------------------------
    print("\n--- 6. FAZER PREVISÕES ---")

    resultados = []
    modelos_resultados = []

    for nome, modelo in modelos:
        y_pred = prever(modelo, X_test)
        y_pred_proba = prever_probabilidades(modelo, X_test)

        resultado, matriz, relatorio = avaliar_modelo(
            nome, y_test, y_pred, y_pred_proba,
            nomes_classes=["Phishing (0)", "Legítimo (1)"]
        )

        resultado["y_pred"] = y_pred
        resultado["y_pred_proba"] = y_pred_proba
        resultado["matriz"] = matriz

        resultados.append(resultado)
        modelos_resultados.append(resultado)

    # --------------------------------------------------
    # 7. CROSS-VALIDATION
    # --------------------------------------------------
    print("\n--- 7. CROSS-VALIDATION (5-fold) ---")

    for nome, modelo in modelos:
        print(f"\n  {nome}:")
        cv_resultados = cross_validation(modelo, X_train, y_train, cv_folds=5)

    # --------------------------------------------------
    # 8. COMPARAÇÃO TREINO VS TESTE (overfitting)
    # --------------------------------------------------
    print("\n--- 8. COMPARAÇÃO TREINO VS TESTE ---")

    for nome, modelo in modelos:
        print(f"\n  {nome}:")
        comparar_treino_teste(modelo, X_train, y_train, X_test, y_test)

    # --------------------------------------------------
    # 9. COMPARAR MODELOS
    # --------------------------------------------------
    print("\n--- 9. COMPARAÇÃO DOS MODELOS ---")

    # Remover colunas não-numéricas para a tabela comparativa
    resultados_tabela = []
    for r in resultados:
        linha = {k: v for k, v in r.items() if k not in ["y_pred", "y_pred_proba", "matriz"]}
        resultados_tabela.append(linha)

    tabela = comparar_modelos(resultados_tabela)
    print(tabela.to_string(index=False))

    # Guardar tabela em CSV
    pasta_models = PASTA_PROJETO / "models"
    pasta_models.mkdir(exist_ok=True)
    caminho_csv = pasta_models / "comparacao_modelos.csv"
    tabela.to_csv(caminho_csv, index=False, encoding="utf-8-sig")
    print(f"\nTabela guardada em: {caminho_csv}")

    # --------------------------------------------------
    # 10. IMPORTÂNCIA DAS FEATURES
    # --------------------------------------------------
    print("\n--- 10. IMPORTÂNCIA DAS FEATURES ---")

    pasta_graficos = pasta_models / "graficos"
    pasta_graficos.mkdir(exist_ok=True)

    for nome, modelo in modelos:
        importancias = importancia_features(modelo, nomes_features)

        if importancias is not None:
            print(f"\n--- TOP 10 FEATURES — {nome} ---")
            print(importancias.head(10).to_string(index=False))

            # Guardar gráfico
            fig = grafico_feature_importance(importancias, nome, top_n=15)
            fig.savefig(
                pasta_graficos / f"feature_importance_{nome.lower().replace(' ', '_')}.png",
                dpi=150, bbox_inches="tight"
            )
            plt.close(fig)

    # --------------------------------------------------
    # 11. GRÁFICOS COMPARATIVOS
    # --------------------------------------------------
    print("\n--- 11. GRÁFICOS COMPARATIVOS ---")

    # Matrizes de confusão (subplots)
    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    for ax, resultado in zip(axes.flat, resultados):
        grafico_matriz_confusao(resultado["matriz"], resultado["Modelo"], ax=ax)
    plt.suptitle("Matrizes de Confusão — Comparação de Modelos", fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.96], h_pad=3.0)
    fig.savefig(pasta_graficos / "matrizes_confusao.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  • Matrizes de confusão guardadas")

    # Gráficos de comparação de métricas
    for metrica in ["Accuracy", "Precision", "Recall", "F1-score"]:
        fig = grafico_comparacao(resultados_tabela, metrica=metrica)
        fig.savefig(
            pasta_graficos / f"comparacao_{metrica.lower()}.png",
            dpi=150, bbox_inches="tight"
        )
        plt.close(fig)
    print("  • Gráficos de comparação guardados")

    # Curvas ROC
    fig = grafico_curvas_roc(modelos_resultados, y_test)
    fig.savefig(pasta_graficos / "curvas_roc.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  • Curvas ROC guardadas")

    # Curvas Precision-Recall
    fig = grafico_curvas_pr(modelos_resultados, y_test)
    fig.savefig(pasta_graficos / "curvas_precision_recall.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  • Curvas Precision-Recall guardadas")

    # --------------------------------------------------
    # 12. GUARDAR MODELOS TREINADOS
    # --------------------------------------------------
    print("\n--- 12. GUARDAR MODELOS ---")

    for nome, modelo in modelos:
        guardar_modelo(modelo, nome)

    # --------------------------------------------------
    # RESUMO FINAL
    # --------------------------------------------------
    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    print(f"\n{tabela.to_string(index=False)}")

    melhor = tabela.loc[tabela["F1-score"].idxmax()]
    print(f"\nMelhor modelo (F1-score): {melhor['Modelo']} ({melhor['F1-score']:.4f})")
    print("\nModel Building concluído com sucesso.")


if __name__ == "__main__":
    main()
