import pandas as pd

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
# 1. CRIAR DECISION TREE
# --------------------------------------------------

def criar_decision_tree(random_state=42):

    modelo = DecisionTreeClassifier(
        random_state=random_state
    )

    return modelo


# --------------------------------------------------
# 2. CRIAR RANDOM FOREST
# --------------------------------------------------

def criar_random_forest(random_state=42):

    modelo = RandomForestClassifier(
        n_estimators=100,
        random_state=random_state
    )

    return modelo


# --------------------------------------------------
# 3. CRIAR XGBOOST
# --------------------------------------------------

def criar_xgboost(random_state=42):

    modelo = XGBClassifier(
        objective="binary:logistic",
        random_state=random_state,
        eval_metric="logloss"
    )

    return modelo


# --------------------------------------------------
# 4. TREINAR MODELO
# --------------------------------------------------

def treinar_modelo(modelo, X_train, y_train):

    modelo.fit(
        X_train,
        y_train
    )

    return modelo


# --------------------------------------------------
# 5. FAZER PREVISÕES
# --------------------------------------------------

def prever(modelo, X_test):

    y_pred = modelo.predict(
        X_test
    )

    return y_pred


# --------------------------------------------------
# 6. AVALIAR MODELO
# --------------------------------------------------

def avaliar_modelo(
    nome,
    y_test,
    y_pred,
    nomes_classes=None
):

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

    matriz = confusion_matrix(
        y_test,
        y_pred
    )

    relatorio = classification_report(
        y_test,
        y_pred,
        target_names=nomes_classes
    )

    resultados = {
        "Modelo": nome,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-score": f1
    }

    return resultados, matriz, relatorio


# --------------------------------------------------
# 7. COMPARAR MODELOS
# --------------------------------------------------

def comparar_modelos(resultados):

    tabela = pd.DataFrame(
        resultados
    )

    return tabela


# --------------------------------------------------
# 8. ACCURACY TREINO VS TESTE
# --------------------------------------------------

def comparar_treino_teste(
    modelo,
    X_train,
    y_train,
    X_test,
    y_test
):

    accuracy_treino = modelo.score(
        X_train,
        y_train
    )

    accuracy_teste = modelo.score(
        X_test,
        y_test
    )

    return accuracy_treino, accuracy_teste


# --------------------------------------------------
# 9. IMPORTÂNCIA DAS FEATURES
# --------------------------------------------------

def importancia_features(
    modelo,
    nomes_features
):

    importancias = pd.DataFrame({
        "Feature": nomes_features,
        "Importancia": modelo.feature_importances_
    })

    importancias = importancias.sort_values(
        by="Importancia",
        ascending=False
    )

    return importancias