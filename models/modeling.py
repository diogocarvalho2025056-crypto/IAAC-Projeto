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
    selecionar_baseline_ou_otimizado,
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
# 4. CRIAR MODELOS
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
# 11. COMPARAR RF E XGBOOST
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
# 14. SELECIONAR MELHOR MODELO
# --------------------------------------------------

nome_melhor_modelo = selecionar_melhor_modelo(
    resultados_validacao,
    resultados_cv
)

print("\n======================================")
print("MODELO SELECIONADO")
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
# 15. HYPERPARAMETER TUNING - XGBOOST
# --------------------------------------------------

grid_search = otimizar_xgboost(
    X_train,
    y_train
)

print("\n======================================")
print("HYPERPARAMETER TUNING - XGBOOST")
print("======================================")

print(
    "Melhores parâmetros:"
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

xgboost_otimizado = (
    grid_search.best_estimator_
)


# --------------------------------------------------
# 16. AVALIAR XGBOOST OTIMIZADO
# --------------------------------------------------

y_pred_val_xgb_otimizado = prever(
    xgboost_otimizado,
    X_val
)

(
    resultado_xgb_otimizado,
    matriz_xgb_otimizado,
    relatorio_xgb_otimizado
) = avaliar_modelo(
    "XGBoost Otimizado",
    y_val,
    y_pred_val_xgb_otimizado,
    ["Benigno", "Malware"]
)

mostrar_resultados(
    resultado_xgb_otimizado,
    matriz_xgb_otimizado,
    relatorio_xgb_otimizado
)


comparacao_xgb = pd.DataFrame([
    resultado_xgb,
    resultado_xgb_otimizado
])

print(
    "\n--- XGBOOST BASELINE VS OTIMIZADO ---"
)

print(
    comparacao_xgb
)


# --------------------------------------------------
# 17. SELECIONAR BASELINE OU OTIMIZADO
# --------------------------------------------------

modelo_final, nome_modelo_final = (
    selecionar_baseline_ou_otimizado(
        resultado_xgb,
        resultado_xgb_otimizado,
        xgboost,
        xgboost_otimizado
    )
)

print("\n======================================")
print("MODELO FINAL APÓS TUNING")
print("======================================")

print(
    "Modelo selecionado:",
    nome_modelo_final
)


# --------------------------------------------------
# 18. AVALIAÇÃO FINAL NO TESTE
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
# 19. ROC-AUC
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
# 20. ANÁLISE DE OVERFITTING
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

overfitting_xgb_otimizado = analisar_overfitting(
    "XGBoost Otimizado",
    xgboost_otimizado,
    X_train,
    y_train,
    X_val,
    y_val
)


comparacao_overfitting = pd.DataFrame([
    overfitting_dt,
    overfitting_rf,
    overfitting_xgb,
    overfitting_xgb_otimizado
])

print(
    "\n--- ANÁLISE DE OVERFITTING ---"
)

print(
    comparacao_overfitting
)