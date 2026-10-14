import pandas as pd

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    roc_curve
)

from sklearn.model_selection import (
    cross_val_score,
    StratifiedKFold,
    GridSearchCV,
    RandomizedSearchCV
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

def treinar_modelo(
    modelo,
    X_train,
    y_train
):

    modelo.fit(
        X_train,
        y_train
    )

    return modelo


# --------------------------------------------------
# 5. FAZER PREVISÕES
# --------------------------------------------------

def prever(
    modelo,
    X_dados
):

    y_pred = modelo.predict(
        X_dados
    )

    return y_pred


# --------------------------------------------------
# 6. AVALIAR MODELO
# --------------------------------------------------

def avaliar_modelo(
    nome,
    y_real,
    y_pred,
    nomes_classes=None
):

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

    relatorio = classification_report(
        y_real,
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

    return (
        resultados,
        matriz,
        relatorio
    )


# --------------------------------------------------
# 7. COMPARAR MODELOS
# --------------------------------------------------

def comparar_modelos(
    resultados
):

    tabela = pd.DataFrame(
        resultados
    )

    return tabela


# --------------------------------------------------
# 8. COMPARAR TREINO VS VALIDAÇÃO
# --------------------------------------------------

def comparar_treino_validacao(
    modelo,
    X_train,
    y_train,
    X_val,
    y_val
):

    accuracy_treino = modelo.score(
        X_train,
        y_train
    )

    accuracy_validacao = modelo.score(
        X_val,
        y_val
    )

    return (
        accuracy_treino,
        accuracy_validacao
    )


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


# --------------------------------------------------
# 10. CROSS-VALIDATION
# --------------------------------------------------

def avaliar_cross_validation(
    nome,
    modelo,
    X_train,
    y_train,
    n_splits=5,
    random_state=42
):

    cv = StratifiedKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=random_state
    )

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

    resultados = {
        "Modelo": nome,
        "Recall CV": recall_scores.mean(),
        "F1 CV": f1_scores.mean(),
        "Desvio Recall": recall_scores.std(),
        "Desvio F1": f1_scores.std()
    }

    return (
        resultados,
        recall_scores,
        f1_scores
    )


# --------------------------------------------------
# 11. SELECIONAR MELHOR MODELO
# --------------------------------------------------

def selecionar_melhor_modelo(
    resultados_validacao,
    resultados_cv
):

    resultados_validacao_dict = {
        resultado["Modelo"]: resultado
        for resultado in resultados_validacao
    }

    resultados_cv_dict = {
        resultado["Modelo"]: resultado
        for resultado in resultados_cv
    }

    def criterio(nome):

        validacao = resultados_validacao_dict[nome]
        cv = resultados_cv_dict[nome]

        return (
            validacao["Recall"],
            validacao["F1-score"],
            validacao["Accuracy"],
            cv["Recall CV"],
            cv["F1 CV"]
        )

    nome_melhor_modelo = max(
        resultados_validacao_dict.keys(),
        key=criterio
    )

    return nome_melhor_modelo


# --------------------------------------------------
# 12. OBTER MODELO SELECIONADO
# --------------------------------------------------

def obter_modelo_selecionado(
    nome_modelo,
    decision_tree,
    random_forest,
    xgboost
):

    if nome_modelo == "Decision Tree":
        return decision_tree

    if nome_modelo == "Random Forest":
        return random_forest

    return xgboost


# --------------------------------------------------
# 13. HYPERPARAMETER TUNING - XGBOOST
# --------------------------------------------------

def otimizar_xgboost_random(
    X_train,
    y_train,
    random_state=42
):

    parametros = {
        "n_estimators": [
            100,
            150,
            200,
            300,
            400
        ],

        "max_depth": [
            2,
            3,
            4,
            5,
            6
        ],

        "learning_rate": [
            0.01,
            0.03,
            0.05,
            0.10,
            0.20
        ],

        "min_child_weight": [
            1,
            3,
            5,
            7
        ],

        "subsample": [
            0.7,
            0.8,
            0.9,
            1.0
        ],

        "colsample_bytree": [
            0.7,
            0.8,
            0.9,
            1.0
        ],

        "gamma": [
            0,
            0.1,
            0.2,
            0.5
        ],

        "reg_alpha": [
            0,
            0.01,
            0.1,
            0.5
        ],

        "reg_lambda": [
            1,
            2,
            5,
            10
        ]
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=random_state
    )

    modelo = XGBClassifier(
        objective="binary:logistic",
        random_state=random_state,
        eval_metric="logloss"
    )

    random_search = RandomizedSearchCV(
        estimator=modelo,
        param_distributions=parametros,
        n_iter=50,
        scoring="recall",
        cv=cv,
        random_state=random_state,
        n_jobs=-1,
        verbose=1
    )

    random_search.fit(
        X_train,
        y_train
    )

    return random_search


def otimizar_xgboost_refinado(
    X_train,
    y_train,
    random_state=42
):

    parametros = {
        "n_estimators": [100, 150, 200],
        "learning_rate": [0.03, 0.05],
        "min_child_weight": [5, 7],
        "gamma": [0.3, 0.5],
        "reg_lambda": [5, 10],

        "max_depth": [2],
        "subsample": [0.9],
        "colsample_bytree": [0.9],
        "reg_alpha": [0]
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=random_state
    )

    modelo = XGBClassifier(
        objective="binary:logistic",
        random_state=random_state,
        eval_metric="logloss"
    )

    grid_search = GridSearchCV(
        estimator=modelo,
        param_grid=parametros,
        scoring="recall",
        cv=cv,
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(
        X_train,
        y_train
    )

    return grid_search


def otimizar_xgboost(
    X_train,
    y_train,
    random_state=42
):

    parametros = {
        "n_estimators": [
            100,
            200
        ],

        "max_depth": [
            2,
            3,
            4
        ],

        "learning_rate": [
            0.05,
            0.10
        ],

        "reg_alpha": [
            0,
            0.1
        ],

        "reg_lambda": [
            1,
            5
        ]
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=random_state
    )

    modelo = XGBClassifier(
        objective="binary:logistic",
        random_state=random_state,
        eval_metric="logloss"
    )

    grid_search = GridSearchCV(
        estimator=modelo,
        param_grid=parametros,
        scoring="recall",
        cv=cv,
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(
        X_train,
        y_train
    )

    return grid_search


# --------------------------------------------------
# 14. SELECIONAR BASELINE OU OTIMIZADO
# --------------------------------------------------

def selecionar_baseline_ou_otimizado(
    resultado_baseline,
    resultado_otimizado,
    modelo_baseline,
    modelo_otimizado
):

    criterio_baseline = (
        resultado_baseline["Recall"],
        resultado_baseline["F1-score"],
        resultado_baseline["Accuracy"]
    )

    criterio_otimizado = (
        resultado_otimizado["Recall"],
        resultado_otimizado["F1-score"],
        resultado_otimizado["Accuracy"]
    )

    if criterio_otimizado > criterio_baseline:

        return (
            modelo_otimizado,
            "XGBoost Otimizado"
        )

    return (
        modelo_baseline,
        "XGBoost Baseline"
    )


# --------------------------------------------------
# 15. ROC / AUC
# --------------------------------------------------

def calcular_roc_auc(
    modelo,
    X_dados,
    y_real
):

    probabilidades = modelo.predict_proba(
        X_dados
    )[:, 1]

    auc = roc_auc_score(
        y_real,
        probabilidades
    )

    fpr, tpr, thresholds = roc_curve(
        y_real,
        probabilidades
    )

    return (
        auc,
        fpr,
        tpr,
        thresholds
    )


# --------------------------------------------------
# 16. ANÁLISE DE OVERFITTING
# --------------------------------------------------

def analisar_overfitting(
    nome,
    modelo,
    X_train,
    y_train,
    X_val,
    y_val
):

    accuracy_treino = modelo.score(
        X_train,
        y_train
    )

    accuracy_validacao = modelo.score(
        X_val,
        y_val
    )

    diferenca = (
        accuracy_treino
        - accuracy_validacao
    )

    return {
        "Modelo": nome,
        "Accuracy treino": accuracy_treino,
        "Accuracy validação": accuracy_validacao,
        "Diferença": diferenca
    }

