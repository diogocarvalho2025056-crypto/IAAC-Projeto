import sys
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.model_selection import train_test_split


# --------------------------------------------------
# CONFIGURAR CAMINHO DO PROJETO
# --------------------------------------------------

pasta_projeto = Path(__file__).resolve().parent.parent

if str(pasta_projeto) not in sys.path:
    sys.path.append(str(pasta_projeto))


# --------------------------------------------------
# IMPORTAR FUNÇÕES DO MODEL_UTILS
# --------------------------------------------------

from src.model_utils import (
    criar_decision_tree,
    criar_random_forest,
    criar_xgboost,
    treinar_modelo,
    prever,
    avaliar_modelo,
    comparar_modelos,
    comparar_treino_validacao,
    importancia_features,
    avaliar_cross_validation,
    selecionar_melhor_modelo,
    obter_modelo_selecionado,
    otimizar_xgboost,
    otimizar_xgboost_random,
    otimizar_xgboost_refinado,
    calcular_roc_auc,
    analisar_overfitting
)


# --------------------------------------------------
# 1. CARREGAR DATASET PREPARADO
# --------------------------------------------------

ficheiro_csv = (
    pasta_projeto
    / "dataset"
    / "Malware_prepared.csv"
)

df = pd.read_csv(
    ficheiro_csv
)

print("--- DATASET PREPARADO ---")
print(df.shape)


# --------------------------------------------------
# 2. SEPARAR FEATURES E TARGET
# --------------------------------------------------

X = df.drop(
    columns=["Malicious"]
)

y = df["Malicious"]

print("\n--- FEATURES ---")
print(X.shape)

print("\n--- TARGET ---")
print(y.shape)


# --------------------------------------------------
# 3. DIVIDIR TREINO, VALIDAÇÃO E TESTE
# --------------------------------------------------

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)

print("\n--- DIMENSÕES DOS CONJUNTOS ---")

print("X_train:", X_train.shape)
print("X_val:", X_val.shape)
print("X_test:", X_test.shape)

print("y_train:", y_train.shape)
print("y_val:", y_val.shape)
print("y_test:", y_test.shape)


# --------------------------------------------------
# 4. CRIAR MODELOS BASELINE
# --------------------------------------------------

decision_tree = criar_decision_tree()

random_forest = criar_random_forest()

xgboost = criar_xgboost()


# --------------------------------------------------
# 5. TREINAR MODELOS
# --------------------------------------------------

decision_tree = treinar_modelo(
    decision_tree,
    X_train,
    y_train
)

random_forest = treinar_modelo(
    random_forest,
    X_train,
    y_train
)

xgboost = treinar_modelo(
    xgboost,
    X_train,
    y_train
)


# --------------------------------------------------
# 6. PREVISÕES NA VALIDAÇÃO
# --------------------------------------------------

y_pred_val_dt = prever(
    decision_tree,
    X_val
)

y_pred_val_rf = prever(
    random_forest,
    X_val
)

y_pred_val_xgb = prever(
    xgboost,
    X_val
)


# --------------------------------------------------
# 7. AVALIAR MODELOS NA VALIDAÇÃO
# --------------------------------------------------

print("\n======================================")
print("AVALIAÇÃO NO CONJUNTO DE VALIDAÇÃO")
print("======================================")

resultado_dt, matriz_dt, relatorio_dt = avaliar_modelo(
    "Decision Tree",
    y_val,
    y_pred_val_dt,
    ["Benigno", "Malware"]
)

resultado_rf, matriz_rf, relatorio_rf = avaliar_modelo(
    "Random Forest",
    y_val,
    y_pred_val_rf,
    ["Benigno", "Malware"]
)

resultado_xgb, matriz_xgb, relatorio_xgb = avaliar_modelo(
    "XGBoost",
    y_val,
    y_pred_val_xgb,
    ["Benigno", "Malware"]
)


def mostrar_resultados(
    resultado,
    matriz,
    relatorio
):

    print("\n==============================")
    print(resultado["Modelo"])
    print("==============================")

    print(
        "Accuracy:",
        resultado["Accuracy"]
    )

    print(
        "Precision:",
        resultado["Precision"]
    )

    print(
        "Recall:",
        resultado["Recall"]
    )

    print(
        "F1-score:",
        resultado["F1-score"]
    )

    print("\nMatriz de confusão:")
    print(matriz)

    print("\nRelatório de classificação:")
    print(relatorio)


mostrar_resultados(
    resultado_dt,
    matriz_dt,
    relatorio_dt
)

mostrar_resultados(
    resultado_rf,
    matriz_rf,
    relatorio_rf
)

mostrar_resultados(
    resultado_xgb,
    matriz_xgb,
    relatorio_xgb
)


# --------------------------------------------------
# 8. COMPARAR MODELOS NA VALIDAÇÃO
# --------------------------------------------------

resultados_validacao = [
    resultado_dt,
    resultado_rf,
    resultado_xgb
]

tabela_validacao = comparar_modelos(
    resultados_validacao
)

print(
    "\n--- COMPARAÇÃO DOS MODELOS - VALIDAÇÃO ---"
)

print(
    tabela_validacao
)


# --------------------------------------------------
# 9. TREINO VS VALIDAÇÃO
# --------------------------------------------------

print("\n======================================")
print("ACCURACY TREINO VS VALIDAÇÃO")
print("======================================")

for nome, modelo in [
    ("Decision Tree", decision_tree),
    ("Random Forest", random_forest),
    ("XGBoost", xgboost)
]:

    treino, validacao = comparar_treino_validacao(
        modelo,
        X_train,
        y_train,
        X_val,
        y_val
    )

    print(
        f"\n--- {nome.upper()} ---"
    )

    print(
        "Accuracy treino:",
        treino
    )

    print(
        "Accuracy validação:",
        validacao
    )


# --------------------------------------------------
# 10. IMPORTÂNCIA DAS FEATURES
# --------------------------------------------------

for nome, modelo in [
    ("Decision Tree", decision_tree),
    ("Random Forest", random_forest),
    ("XGBoost", xgboost)
]:

    importancias = importancia_features(
        modelo,
        X.columns
    )

    print(
        f"\n--- TOP 10 FEATURES MAIS IMPORTANTES "
        f"- {nome.upper()} ---"
    )

    print(
        importancias.head(10)
    )


# --------------------------------------------------
# 11. COMPARAR RANDOM FOREST E XGBOOST
# --------------------------------------------------

previsoes_iguais = (
    y_pred_val_rf
    ==
    y_pred_val_xgb
)

print(
    "\n--- RANDOM FOREST VS XGBOOST - VALIDAÇÃO ---"
)

print(
    "Número de previsões iguais:",
    previsoes_iguais.sum()
)

print(
    "Número de previsões diferentes:",
    (~previsoes_iguais).sum()
)

print(
    "Todas as previsões são iguais?",
    previsoes_iguais.all()
)


# --------------------------------------------------
# 12. COMPARAR PROBABILIDADES
# --------------------------------------------------

prob_rf = random_forest.predict_proba(
    X_val
)[:, 1]

prob_xgb = xgboost.predict_proba(
    X_val
)[:, 1]

comparacao_probabilidades = pd.DataFrame({
    "Random Forest": prob_rf,
    "XGBoost": prob_xgb
})

print(
    "\n--- EXEMPLO DE PROBABILIDADES "
    "- VALIDAÇÃO ---"
)

print(
    comparacao_probabilidades.head(10)
)


# --------------------------------------------------
# 13. CROSS-VALIDATION
# --------------------------------------------------

print("\n======================================")
print("CROSS-VALIDATION")
print("======================================")

resultado_cv_dt, recall_dt, f1_dt = avaliar_cross_validation(
    "Decision Tree",
    decision_tree,
    X_train,
    y_train
)

resultado_cv_rf, recall_rf, f1_rf = avaliar_cross_validation(
    "Random Forest",
    random_forest,
    X_train,
    y_train
)

resultado_cv_xgb, recall_xgb, f1_xgb = avaliar_cross_validation(
    "XGBoost",
    xgboost,
    X_train,
    y_train
)


def mostrar_cv(
    resultado,
    recalls,
    f1_scores
):

    print("\n==============================")
    print(resultado["Modelo"])
    print("==============================")

    print(
        "Recall por fold:",
        recalls
    )

    print(
        "Recall médio:",
        resultado["Recall CV"]
    )

    print(
        "Desvio-padrão Recall:",
        resultado["Desvio Recall"]
    )

    print(
        "\nF1-score por fold:",
        f1_scores
    )

    print(
        "F1-score médio:",
        resultado["F1 CV"]
    )

    print(
        "Desvio-padrão F1:",
        resultado["Desvio F1"]
    )


mostrar_cv(
    resultado_cv_dt,
    recall_dt,
    f1_dt
)

mostrar_cv(
    resultado_cv_rf,
    recall_rf,
    f1_rf
)

mostrar_cv(
    resultado_cv_xgb,
    recall_xgb,
    f1_xgb
)


resultados_cv = [
    resultado_cv_dt,
    resultado_cv_rf,
    resultado_cv_xgb
]

tabela_cv = pd.DataFrame(
    resultados_cv
)

print(
    "\n--- COMPARAÇÃO CROSS-VALIDATION ---"
)

print(
    tabela_cv
)


# --------------------------------------------------
# 14. SELECIONAR MELHOR MODELO BASELINE
# --------------------------------------------------

nome_melhor_modelo = selecionar_melhor_modelo(
    resultados_validacao,
    resultados_cv
)

print("\n======================================")
print("MODELO BASELINE SELECIONADO")
print("======================================")

print(
    "Melhor modelo:",
    nome_melhor_modelo
)

melhor_modelo = obter_modelo_selecionado(
    nome_melhor_modelo,
    decision_tree,
    random_forest,
    xgboost
)


# --------------------------------------------------
# 15. RANDOMIZED SEARCH - XGBOOST
# --------------------------------------------------

print("\n======================================")
print("RANDOMIZED SEARCH - XGBOOST")
print("======================================")

random_search = otimizar_xgboost_random(
    X_train,
    y_train
)

print(
    "\nMelhores parâmetros encontrados:"
)

print(
    random_search.best_params_
)

print(
    "\nMelhor Recall médio CV:"
)

print(
    random_search.best_score_
)


# --------------------------------------------------
# 16. GRIDSEARCH ORIGINAL - XGBOOST
# --------------------------------------------------

print("\n======================================")
print("GRIDSEARCH ORIGINAL - XGBOOST")
print("======================================")

grid_search = otimizar_xgboost(
    X_train,
    y_train
)

print(
    "\nMelhores parâmetros encontrados:"
)

print(
    grid_search.best_params_
)

print(
    "\nMelhor Recall médio CV:"
)

print(
    grid_search.best_score_
)


# --------------------------------------------------
# 17. GRIDSEARCH REFINADO - XGBOOST
# --------------------------------------------------

print("\n======================================")
print("GRIDSEARCH REFINADO - XGBOOST")
print("======================================")

grid_refinado = otimizar_xgboost_refinado(
    X_train,
    y_train
)

print(
    "\nMelhores parâmetros refinados:"
)

print(
    grid_refinado.best_params_
)

print(
    "\nMelhor Recall médio CV:"
)

print(
    grid_refinado.best_score_
)


# --------------------------------------------------
# 18. OBTER MODELOS RESULTANTES DO TUNING
# --------------------------------------------------

modelo_grid_original = (
    grid_search.best_estimator_
)

modelo_random = (
    random_search.best_estimator_
)

modelo_refinado = (
    grid_refinado.best_estimator_
)


# --------------------------------------------------
# 19. AVALIAR TODAS AS VERSÕES XGBOOST
#     NO CONJUNTO DE VALIDAÇÃO
# --------------------------------------------------

y_pred_grid_original = prever(
    modelo_grid_original,
    X_val
)

y_pred_random = prever(
    modelo_random,
    X_val
)

y_pred_refinado = prever(
    modelo_refinado,
    X_val
)


resultado_grid_original, matriz_grid_original, relatorio_grid_original = avaliar_modelo(
    "XGBoost GridSearch Original",
    y_val,
    y_pred_grid_original,
    ["Benigno", "Malware"]
)

resultado_random, matriz_random, relatorio_random = avaliar_modelo(
    "XGBoost RandomizedSearch",
    y_val,
    y_pred_random,
    ["Benigno", "Malware"]
)

resultado_refinado, matriz_refinado, relatorio_refinado = avaliar_modelo(
    "XGBoost GridSearch Refinado",
    y_val,
    y_pred_refinado,
    ["Benigno", "Malware"]
)


# --------------------------------------------------
# 20. COMPARAÇÃO FINAL DO TUNING
# --------------------------------------------------

comparacao_tuning = pd.DataFrame([
    resultado_xgb,
    resultado_grid_original,
    resultado_random,
    resultado_refinado
])

print("\n======================================")
print("COMPARAÇÃO FINAL DO TUNING")
print("======================================")

print(
    comparacao_tuning
)


# --------------------------------------------------
# 21. SELECIONAR VERSÃO FINAL DO XGBOOST
# --------------------------------------------------
#
# Critério:
#
# 1.º Recall
# 2.º F1-score
# 3.º Accuracy
#
# O baseline aparece primeiro.
# Em caso de empate total, mantém-se o baseline.
# --------------------------------------------------

candidatos_xgboost = [
    (
        "XGBoost Baseline",
        xgboost,
        resultado_xgb
    ),
    (
        "XGBoost GridSearch Original",
        modelo_grid_original,
        resultado_grid_original
    ),
    (
        "XGBoost RandomizedSearch",
        modelo_random,
        resultado_random
    ),
    (
        "XGBoost GridSearch Refinado",
        modelo_refinado,
        resultado_refinado
    )
]


def criterio_selecao(item):

    resultado = item[2]

    return (
        resultado["Recall"],
        resultado["F1-score"],
        resultado["Accuracy"]
    )


nome_modelo_final, modelo_final, resultado_validacao_final = max(
    candidatos_xgboost,
    key=criterio_selecao
)


print("\n======================================")
print("MODELO FINAL APÓS TUNING")
print("======================================")

print(
    "Modelo selecionado:",
    nome_modelo_final
)


# --------------------------------------------------
# 22. ANÁLISE DE OVERFITTING
# --------------------------------------------------

overfitting_dt = analisar_overfitting(
    "Decision Tree",
    decision_tree,
    X_train,
    y_train,
    X_val,
    y_val
)

overfitting_rf = analisar_overfitting(
    "Random Forest",
    random_forest,
    X_train,
    y_train,
    X_val,
    y_val
)

overfitting_xgb = analisar_overfitting(
    "XGBoost Baseline",
    xgboost,
    X_train,
    y_train,
    X_val,
    y_val
)

overfitting_grid = analisar_overfitting(
    "XGBoost GridSearch Original",
    modelo_grid_original,
    X_train,
    y_train,
    X_val,
    y_val
)

overfitting_random = analisar_overfitting(
    "XGBoost RandomizedSearch",
    modelo_random,
    X_train,
    y_train,
    X_val,
    y_val
)

overfitting_refinado = analisar_overfitting(
    "XGBoost GridSearch Refinado",
    modelo_refinado,
    X_train,
    y_train,
    X_val,
    y_val
)


comparacao_overfitting = pd.DataFrame([
    overfitting_dt,
    overfitting_rf,
    overfitting_xgb,
    overfitting_grid,
    overfitting_random,
    overfitting_refinado
])

print(
    "\n--- ANÁLISE DE OVERFITTING ---"
)

print(
    comparacao_overfitting
)


# --------------------------------------------------
# 23. AVALIAÇÃO FINAL NO TESTE
# --------------------------------------------------
#
# Só agora utilizamos o conjunto de teste.
# O teste não é usado para escolher hiperparâmetros.
# --------------------------------------------------

y_pred_test = prever(
    modelo_final,
    X_test
)

(
    resultado_final,
    matriz_final,
    relatorio_final

) = avaliar_modelo(
    nome_modelo_final + " - Teste Final",
    y_test,
    y_pred_test,
    ["Benigno", "Malware"]
)


print("\n======================================")
print("AVALIAÇÃO FINAL NO CONJUNTO DE TESTE")
print("======================================")

mostrar_resultados(
    resultado_final,
    matriz_final,
    relatorio_final
)


# --------------------------------------------------
# 24. ROC-AUC
# --------------------------------------------------

auc, fpr, tpr, thresholds = calcular_roc_auc(
    modelo_final,
    X_test,
    y_test
)

print("\n======================================")
print("ROC-AUC - MODELO FINAL")
print("======================================")

print(
    "AUC:",
    auc
)


plt.figure(
    figsize=(8, 6)
)

plt.plot(
    fpr,
    tpr,
    label=(
        f"{nome_modelo_final} "
        f"- AUC = {auc:.4f}"
    )
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Classificador aleatório"
)

plt.xlabel(
    "False Positive Rate"
)

plt.ylabel(
    "True Positive Rate"
)

plt.title(
    "ROC Curve - Modelo Final"
)

plt.legend()

plt.tight_layout()

plt.show()


# --------------------------------------------------
# 25. GRÁFICO - ACCURACY DOS MODELOS BASELINE
# --------------------------------------------------

accuracy_modelos = tabela_validacao[
    [
        "Modelo",
        "Accuracy"
    ]
].copy()

plt.figure(
    figsize=(8, 5)
)

plt.bar(
    accuracy_modelos["Modelo"],
    accuracy_modelos["Accuracy"]
)

plt.title(
    "Accuracy dos Modelos - Validação"
)

plt.xlabel(
    "Modelo"
)

plt.ylabel(
    "Accuracy"
)

plt.ylim(
    0.95,
    1.00
)

plt.tight_layout()

plt.show()


# --------------------------------------------------
# 26. GRÁFICO - MÉTRICAS DOS MODELOS BASELINE
# --------------------------------------------------

metricas_validacao = tabela_validacao.set_index(
    "Modelo"
)[
    [
        "Accuracy",
        "Precision",
        "Recall",
        "F1-score"
    ]
]

metricas_validacao.plot(
    kind="bar",
    figsize=(10, 6)
)

plt.title(
    "Comparação das Métricas dos Modelos - Validação"
)

plt.xlabel(
    "Modelo"
)

plt.ylabel(
    "Resultado"
)

plt.ylim(
    0.95,
    1.00
)

plt.xticks(
    rotation=0
)

plt.legend(
    title="Métrica"
)

plt.tight_layout()

plt.show()


# --------------------------------------------------
# 27. GRÁFICO - CROSS-VALIDATION
# --------------------------------------------------

metricas_cv = tabela_cv.set_index(
    "Modelo"
)[
    [
        "Recall CV",
        "F1 CV"
    ]
]

metricas_cv.plot(
    kind="bar",
    figsize=(9, 6)
)

plt.title(
    "Comparação dos Modelos - 5-Fold Cross-Validation"
)

plt.xlabel(
    "Modelo"
)

plt.ylabel(
    "Resultado médio"
)

plt.ylim(
    0.97,
    1.00
)

plt.xticks(
    rotation=0
)

plt.legend(
    title="Métrica"
)

plt.tight_layout()

plt.show()


# --------------------------------------------------
# 28. GRÁFICO - COMPARAÇÃO DAS VERSÕES XGBOOST
# --------------------------------------------------

metricas_tuning = comparacao_tuning.set_index(
    "Modelo"
)[
    [
        "Accuracy",
        "Precision",
        "Recall",
        "F1-score"
    ]
]

metricas_tuning.plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title(
    "Comparação das Versões do XGBoost"
)

plt.xlabel(
    "Modelo"
)

plt.ylabel(
    "Resultado"
)

plt.ylim(
    0.95,
    1.00
)

plt.xticks(
    rotation=15
)

plt.legend(
    title="Métrica"
)

plt.tight_layout()

plt.show()


# --------------------------------------------------
# 29. GRÁFICO - TREINO VS VALIDAÇÃO
# --------------------------------------------------

dados_overfitting = comparacao_overfitting.set_index(
    "Modelo"
)[
    [
        "Accuracy treino",
        "Accuracy validação"
    ]
]

dados_overfitting.plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title(
    "Accuracy - Treino vs Validação"
)

plt.xlabel(
    "Modelo"
)

plt.ylabel(
    "Accuracy"
)

plt.ylim(
    0.95,
    1.01
)

plt.xticks(
    rotation=20
)

plt.legend()

plt.tight_layout()

plt.show()


# --------------------------------------------------
# 30. GRÁFICO - TOP 10 FEATURES DO MODELO FINAL
# --------------------------------------------------

importancias_finais = importancia_features(
    modelo_final,
    X.columns
).head(10)

importancias_finais = importancias_finais.sort_values(
    by="Importancia"
)

plt.figure(
    figsize=(9, 6)
)

plt.barh(
    importancias_finais["Feature"],
    importancias_finais["Importancia"]
)

plt.title(
    f"Top 10 Features - {nome_modelo_final}"
)

plt.xlabel(
    "Importância"
)

plt.ylabel(
    "Feature"
)

plt.tight_layout()

plt.show()

# --------------------------------------------------
# 31. GUARDAR MODELO FINAL
# --------------------------------------------------

import json


# Criar pasta models, caso ainda não exista
pasta_models = pasta_projeto / "models"

pasta_models.mkdir(
    exist_ok=True
)


# --------------------------------------------------
# GUARDAR MODELO XGBOOST
# --------------------------------------------------

caminho_modelo = (
    pasta_models
    / "malware_xgboost.json"
)

modelo_final.save_model(
    caminho_modelo
)

print(
    "\nModelo guardado em:",
    caminho_modelo
)


# --------------------------------------------------
# GUARDAR LISTA DE FEATURES
# --------------------------------------------------

features = list(
    X.columns
)

caminho_features = (
    pasta_models
    / "malware_features.json"
)

with open(
    caminho_features,
    "w",
    encoding="utf-8"
) as ficheiro:

    json.dump(
        features,
        ficheiro,
        indent=4,
        ensure_ascii=False
    )

print(
    "Features guardadas em:",
    caminho_features
)