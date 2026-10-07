import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    StratifiedKFold
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from xgboost import XGBClassifier


# --------------------------------------------------
# 1. CARREGAR DATASET PREPARADO
# --------------------------------------------------

pasta_projeto = Path(__file__).parent.parent

ficheiro_csv = (
    pasta_projeto
    / "dataset"
    / "Malware_prepared.csv"
)

df = pd.read_csv(ficheiro_csv)

print("--- DATASET PREPARADO ---")
print(df.shape)


# --------------------------------------------------
# 2. SEPARAR FEATURES E TARGET
# --------------------------------------------------

X = df.drop(columns=["Malicious"])
y = df["Malicious"]

print("\n--- FEATURES ---")
print(X.shape)

print("\n--- TARGET ---")
print(y.shape)


# --------------------------------------------------
# 3. DIVIDIR TREINO, VALIDAÇÃO E TESTE
# --------------------------------------------------

# 70% treino
# 30% temporário

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

# Dos 30% temporários:
# 15% validação
# 15% teste

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
# 4. DECISION TREE
# --------------------------------------------------

decision_tree = DecisionTreeClassifier(
    random_state=42
)

decision_tree.fit(
    X_train,
    y_train
)

y_pred_val_dt = decision_tree.predict(
    X_val
)


# --------------------------------------------------
# 5. RANDOM FOREST
# --------------------------------------------------

random_forest = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

random_forest.fit(
    X_train,
    y_train
)

y_pred_val_rf = random_forest.predict(
    X_val
)


# --------------------------------------------------
# 6. XGBOOST
# --------------------------------------------------

xgboost = XGBClassifier(
    objective="binary:logistic",
    random_state=42,
    eval_metric="logloss"
)

xgboost.fit(
    X_train,
    y_train
)

y_pred_val_xgb = xgboost.predict(
    X_val
)


# --------------------------------------------------
# 7. FUNÇÃO DE AVALIAÇÃO
# --------------------------------------------------

def avaliar_modelo(nome, y_real, y_pred):

    accuracy = accuracy_score(
        y_real,
        y_pred
    )

    precision = precision_score(
        y_real,
        y_pred
    )

    recall = recall_score(
        y_real,
        y_pred
    )

    f1 = f1_score(
        y_real,
        y_pred
    )

    matriz = confusion_matrix(
        y_real,
        y_pred
    )

    print("\n==============================")
    print(nome)
    print("==============================")

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1-score:", f1)

    print("\nMatriz de confusão:")
    print(matriz)

    print("\nRelatório de classificação:")
    print(
        classification_report(
            y_real,
            y_pred,
            target_names=[
                "Benigno",
                "Malware"
            ]
        )
    )

    return {
        "Modelo": nome,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-score": f1
    }


# --------------------------------------------------
# 8. AVALIAR MODELOS NA VALIDAÇÃO
# --------------------------------------------------

print("\n======================================")
print("AVALIAÇÃO NO CONJUNTO DE VALIDAÇÃO")
print("======================================")

resultado_dt = avaliar_modelo(
    "Decision Tree",
    y_val,
    y_pred_val_dt
)

resultado_rf = avaliar_modelo(
    "Random Forest",
    y_val,
    y_pred_val_rf
)

resultado_xgb = avaliar_modelo(
    "XGBoost",
    y_val,
    y_pred_val_xgb
)


# --------------------------------------------------
# 9. COMPARAR MODELOS NA VALIDAÇÃO
# --------------------------------------------------

resultados = pd.DataFrame([
    resultado_dt,
    resultado_rf,
    resultado_xgb
])

print("\n--- COMPARAÇÃO DOS MODELOS - VALIDAÇÃO ---")
print(resultados)


# --------------------------------------------------
# 10. COMPARAR TREINO VS VALIDAÇÃO
# --------------------------------------------------

print("\n======================================")
print("ACCURACY TREINO VS VALIDAÇÃO")
print("======================================")


print("\n--- DECISION TREE ---")

print(
    "Accuracy treino:",
    decision_tree.score(
        X_train,
        y_train
    )
)

print(
    "Accuracy validação:",
    decision_tree.score(
        X_val,
        y_val
    )
)


print("\n--- RANDOM FOREST ---")

print(
    "Accuracy treino:",
    random_forest.score(
        X_train,
        y_train
    )
)

print(
    "Accuracy validação:",
    random_forest.score(
        X_val,
        y_val
    )
)


print("\n--- XGBOOST ---")

print(
    "Accuracy treino:",
    xgboost.score(
        X_train,
        y_train
    )
)

print(
    "Accuracy validação:",
    xgboost.score(
        X_val,
        y_val
    )
)


# --------------------------------------------------
# 11. IMPORTÂNCIA DAS FEATURES - DECISION TREE
# --------------------------------------------------

importancias_dt = pd.DataFrame({
    "Feature": X.columns,
    "Importancia": decision_tree.feature_importances_
})

importancias_dt = importancias_dt.sort_values(
    by="Importancia",
    ascending=False
)

print(
    "\n--- TOP 10 FEATURES MAIS IMPORTANTES "
    "- DECISION TREE ---"
)

print(
    importancias_dt.head(10)
)


# --------------------------------------------------
# 12. IMPORTÂNCIA DAS FEATURES - RANDOM FOREST
# --------------------------------------------------

importancias_rf = pd.DataFrame({
    "Feature": X.columns,
    "Importancia": random_forest.feature_importances_
})

importancias_rf = importancias_rf.sort_values(
    by="Importancia",
    ascending=False
)

print(
    "\n--- TOP 10 FEATURES MAIS IMPORTANTES "
    "- RANDOM FOREST ---"
)

print(
    importancias_rf.head(10)
)


# --------------------------------------------------
# 13. IMPORTÂNCIA DAS FEATURES - XGBOOST
# --------------------------------------------------

importancias_xgb = pd.DataFrame({
    "Feature": X.columns,
    "Importancia": xgboost.feature_importances_
})

importancias_xgb = importancias_xgb.sort_values(
    by="Importancia",
    ascending=False
)

print(
    "\n--- TOP 10 FEATURES MAIS IMPORTANTES "
    "- XGBOOST ---"
)

print(
    importancias_xgb.head(10)
)


# --------------------------------------------------
# 14. COMPARAR PREVISÕES RANDOM FOREST VS XGBOOST
#     NO CONJUNTO DE VALIDAÇÃO
# --------------------------------------------------

previsoes_iguais = (
    y_pred_val_rf == y_pred_val_xgb
)

print("\n--- RANDOM FOREST VS XGBOOST - VALIDAÇÃO ---")

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
# 15. COMPARAR PROBABILIDADES RF VS XGBOOST
#     NO CONJUNTO DE VALIDAÇÃO
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
# 16. CROSS-VALIDATION NO CONJUNTO DE TREINO
# --------------------------------------------------

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


def avaliar_cross_validation(
    nome,
    modelo,
    X_train,
    y_train
):

    recall_scores = cross_val_score(
        modelo,
        X_train,
        y_train,
        cv=cv,
        scoring="recall"
    )

    f1_scores = cross_val_score(
        modelo,
        X_train,
        y_train,
        cv=cv,
        scoring="f1"
    )

    print("\n==============================")
    print(nome)
    print("==============================")

    print("Recall por fold:")
    print(recall_scores)

    print(
        "Recall médio:",
        recall_scores.mean()
    )

    print(
        "Desvio-padrão Recall:",
        recall_scores.std()
    )

    print("\nF1-score por fold:")
    print(f1_scores)

    print(
        "F1-score médio:",
        f1_scores.mean()
    )

    print(
        "Desvio-padrão F1:",
        f1_scores.std()
    )

    return {
        "Modelo": nome,
        "Recall CV": recall_scores.mean(),
        "F1 CV": f1_scores.mean(),
        "Desvio Recall": recall_scores.std(),
        "Desvio F1": f1_scores.std()
    }


# --------------------------------------------------
# 17. AVALIAR CROSS-VALIDATION
# --------------------------------------------------

resultado_cv_dt = avaliar_cross_validation(
    "Decision Tree",
    decision_tree,
    X_train,
    y_train
)

resultado_cv_rf = avaliar_cross_validation(
    "Random Forest",
    random_forest,
    X_train,
    y_train
)

resultado_cv_xgb = avaliar_cross_validation(
    "XGBoost",
    xgboost,
    X_train,
    y_train
)
resultados_cv = pd.DataFrame([
    resultado_cv_dt,
    resultado_cv_rf,
    resultado_cv_xgb
])

print("\n--- COMPARAÇÃO CROSS-VALIDATION ---")
print(resultados_cv)


# --------------------------------------------------
# 18. SELECIONAR MELHOR MODELO
# --------------------------------------------------

# Primeiro comparamos os resultados da validação.
# Em caso de empate, utilizamos os resultados médios
# da cross-validation realizada apenas no treino.

resultados_validacao = {
    "Decision Tree": resultado_dt,
    "Random Forest": resultado_rf,
    "XGBoost": resultado_xgb
}

resultados_cross_validation = {
    "Decision Tree": resultado_cv_dt,
    "Random Forest": resultado_cv_rf,
    "XGBoost": resultado_cv_xgb
}


def criterio_selecao(nome):

    validacao = resultados_validacao[nome]
    cv_resultado = resultados_cross_validation[nome]

    return (
        validacao["Recall"],
        validacao["F1-score"],
        validacao["Accuracy"],
        cv_resultado["Recall CV"],
        cv_resultado["F1 CV"]
    )


nome_melhor_modelo = max(
    resultados_validacao.keys(),
    key=criterio_selecao
)

print("\n======================================")
print("MODELO SELECIONADO")
print("======================================")

print(
    "Melhor modelo:",
    nome_melhor_modelo
)

# --------------------------------------------------
# 19. IDENTIFICAR O MODELO SELECIONADO
# --------------------------------------------------

if nome_melhor_modelo == "Decision Tree":
    melhor_modelo = decision_tree

elif nome_melhor_modelo == "Random Forest":
    melhor_modelo = random_forest

else:
    melhor_modelo = xgboost


# --------------------------------------------------
# 20. AVALIAÇÃO FINAL NO CONJUNTO DE TESTE
# --------------------------------------------------

y_pred_test = melhor_modelo.predict(
    X_test
)

print("\n======================================")
print("AVALIAÇÃO FINAL NO CONJUNTO DE TESTE")
print("======================================")

resultado_final = avaliar_modelo(
    nome_melhor_modelo + " - Teste Final",
    y_test,
    y_pred_test
)