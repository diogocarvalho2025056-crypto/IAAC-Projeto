import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

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
# 3. DIVIDIR TREINO E TESTE
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n--- DIMENSÕES DOS CONJUNTOS ---")
print("X_train:", X_train.shape)
print("X_test:", X_test.shape)
print("y_train:", y_train.shape)
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

y_pred_dt = decision_tree.predict(
    X_test
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

y_pred_rf = random_forest.predict(
    X_test
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

y_pred_xgb = xgboost.predict(
    X_test
)


# --------------------------------------------------
# 7. FUNÇÃO DE AVALIAÇÃO
# --------------------------------------------------

def avaliar_modelo(nome, y_test, y_pred):

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred
    )

    recall = recall_score(
        y_test,
        y_pred
    )

    f1 = f1_score(
        y_test,
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
    print(
        confusion_matrix(
            y_test,
            y_pred
        )
    )

    print("\nRelatório de classificação:")
    print(
        classification_report(
            y_test,
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
# 8. AVALIAR MODELOS
# --------------------------------------------------

resultado_dt = avaliar_modelo(
    "Decision Tree",
    y_test,
    y_pred_dt
)

resultado_rf = avaliar_modelo(
    "Random Forest",
    y_test,
    y_pred_rf
)

resultado_xgb = avaliar_modelo(
    "XGBoost",
    y_test,
    y_pred_xgb
)


# --------------------------------------------------
# 9. COMPARAR MODELOS
# --------------------------------------------------

resultados = pd.DataFrame([
    resultado_dt,
    resultado_rf,
    resultado_xgb
])

print("\n--- COMPARAÇÃO DOS MODELOS ---")
print(resultados)


# --------------------------------------------------
# 10. COMPARAR TREINO VS TESTE
# --------------------------------------------------

print("\n==============================")
print("ACCURACY TREINO VS TESTE")
print("==============================")


print("\n--- DECISION TREE ---")

print(
    "Accuracy treino:",
    decision_tree.score(
        X_train,
        y_train
    )
)

print(
    "Accuracy teste:",
    decision_tree.score(
        X_test,
        y_test
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
    "Accuracy teste:",
    random_forest.score(
        X_test,
        y_test
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
    "Accuracy teste:",
    xgboost.score(
        X_test,
        y_test
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