"""
Script de Model Building - Phishing Website Detector
====================================================

Este script executa as etapas de modelação do projeto:
  1. Carregamento do dataset preparado (phishing_prepared.csv)
  2. Separação features/target e divisão treino/teste (80/20, estratificada)
  3. Treino de 4 modelos: Logistic Regression (baseline), Decision Tree,
     Random Forest e XGBoost
  4. Avaliação no conjunto de teste (Accuracy, Precision, Recall, F1,
     ROC AUC, PR AUC, matriz de confusão)
  5. Cross-validation (5-fold) no conjunto de treino
  6. Comparação treino vs teste (deteção de overfitting)
  7. Importância das features
    8. Mostrar a tabela comparativa e a importância das features

Todos os resultados são mostrados no terminal (não são criados gráficos).

Execução (a partir da pasta do projeto):
  python models/modeling.py
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

# Evita o erro de codificação (UnicodeEncodeError) na consola do Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

warnings.filterwarnings("ignore")

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------

PASTA_PROJETO = Path(__file__).parent.parent
FICHEIRO_CSV = PASTA_PROJETO / "dataset" / "phishing_prepared.csv"

TARGET = "class"
# No dataset original: -1 = Phishing, 1 = Legítimo.
# Mapeamos para 0 = Phishing, 1 = Legítimo (necessário para o XGBoost).
NOMES_CLASSES = ["Phishing (0)", "Legítimo (1)"]
RANDOM_STATE = 42

# --------------------------------------------------
# 1. CARREGAR DATASET PREPARADO
# --------------------------------------------------

print("=" * 60)
print("MODEL BUILDING - PHISHING WEBSITE DETECTOR")
print("=" * 60)

print("\n--- 1. CARREGAR DATASET PREPARADO ---")
df = pd.read_csv(FICHEIRO_CSV)
print(f"Dataset preparado carregado: {df.shape[0]} registos x {df.shape[1]} colunas")


# --------------------------------------------------
# 2. SEPARAR FEATURES E TARGET
# --------------------------------------------------

print("\n--- 2. SEPARAR FEATURES E TARGET ---")
X = df.drop(columns=[TARGET])
y = df[TARGET].map({-1: 0, 1: 1})
nomes_features = X.columns.tolist()

print("Features (X):", X.shape)
print("Target (y):", y.shape)
print("\nDistribuição das classes:")
print(y.value_counts())


# --------------------------------------------------
# 3. DIVIDIR TREINO E TESTE
# --------------------------------------------------

print("\n--- 3. DIVIDIR TREINO E TESTE ---")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)
print("X_train:", X_train.shape)
print("X_test: ", X_test.shape)
print("y_train:", y_train.shape)
print("y_test: ", y_test.shape)


# --------------------------------------------------
# 4. CRIAR MODELOS
# --------------------------------------------------

print("\n--- 4. CRIAR MODELOS ---")

modelos = [
    (
        "Logistic Regression",
        LogisticRegression(random_state=RANDOM_STATE, max_iter=1000, solver="lbfgs"),
    ),
    (
        "Decision Tree",
        DecisionTreeClassifier(
            random_state=RANDOM_STATE,
            max_depth=10,
            min_samples_split=20,
            min_samples_leaf=10,
            criterion="gini",
        ),
    ),
    (
        "Random Forest",
        RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=20,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    ),
    (
        "XGBoost",
        XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            n_jobs=-1,
        ),
    ),
]

for nome, modelo in modelos:
    print(f"  - {nome}: {modelo.__class__.__name__}")


# --------------------------------------------------
# 5. TREINAR MODELOS
# --------------------------------------------------

print("\n--- 5. TREINAR MODELOS ---")
for nome, modelo in modelos:
    modelo.fit(X_train, y_train)
    print(f"  - {nome} treinado.")


# --------------------------------------------------
# 6. AVALIAR NO CONJUNTO DE TESTE
# --------------------------------------------------

print("\n--- 6. AVALIAÇÃO NO CONJUNTO DE TESTE ---")

resultados = []
previsoes = {}

for nome, modelo in modelos:
    y_pred = modelo.predict(X_test)
    y_proba = modelo.predict_proba(X_test)[:, 1]
    matriz = confusion_matrix(y_test, y_pred)

    resultado = {
        "Modelo": nome,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1-score": f1_score(y_test, y_pred),
        "ROC AUC": roc_auc_score(y_test, y_proba),
        "PR AUC": average_precision_score(y_test, y_proba),
    }
    resultados.append(resultado)
    previsoes[nome] = {"y_pred": y_pred, "y_proba": y_proba, "matriz": matriz}

    print("\n" + "=" * 50)
    print(nome)
    print("=" * 50)
    for metrica in ["Accuracy", "Precision", "Recall", "F1-score", "ROC AUC", "PR AUC"]:
        print(f"{metrica + ':':<11} {resultado[metrica]:.4f}")
    print("\nMatriz de confusão:")
    print(matriz)
    print("\nRelatório de classificação:")
    print(classification_report(y_test, y_pred, target_names=NOMES_CLASSES))


# --------------------------------------------------
# 7. CROSS-VALIDATION (5-fold)
# --------------------------------------------------

print("\n--- 7. CROSS-VALIDATION (5-fold, no conjunto de treino) ---")

metricas_cv = ["accuracy", "precision", "recall", "f1"]
for nome, modelo in modelos:
    cv = cross_validate(
        modelo,
        X_train,
        y_train,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        scoring=metricas_cv,
    )
    print(f"\n  {nome}:")
    for m in metricas_cv:
        valores = cv[f"test_{m}"]
        print(f"    {m:<10} {valores.mean():.4f} +/- {valores.std():.4f}")


# --------------------------------------------------
# 8. COMPARAÇÃO TREINO VS TESTE (overfitting)
# --------------------------------------------------

print("\n--- 8. COMPARAÇÃO TREINO VS TESTE ---")

for nome, modelo in modelos:
    acc_treino = modelo.score(X_train, y_train)
    acc_teste = modelo.score(X_test, y_test)
    diferenca = acc_treino - acc_teste
    print(f"\n  {nome}:")
    print(f"    Accuracy treino: {acc_treino:.4f}")
    print(f"    Accuracy teste:  {acc_teste:.4f}")
    print(f"    Diferença:       {diferenca:.4f}")
    if diferenca > 0.05:
        print("    Possível overfitting (diferença > 5%)")
    else:
        print("    Sem indícios significativos de overfitting")


# --------------------------------------------------
# 9. COMPARAR MODELOS
# --------------------------------------------------

print("\n--- 9. COMPARAÇÃO DOS MODELOS ---")

tabela = pd.DataFrame(resultados).round(4)
print(tabela.to_string(index=False))

# --------------------------------------------------
# 10. IMPORTÂNCIA DAS FEATURES
# --------------------------------------------------

print("\n--- 10. IMPORTÂNCIA DAS FEATURES ---")


def obter_importancias(modelo):
    """Importância das features (coeficientes absolutos na Regressão Logística)."""
    final = modelo
    if hasattr(final, "feature_importances_"):
        valores = final.feature_importances_
    elif hasattr(final, "coef_"):
        valores = np.abs(final.coef_[0])
    else:
        return None
    return (
        pd.DataFrame({"Feature": nomes_features, "Importancia": valores})
        .sort_values("Importancia", ascending=False)
        .reset_index(drop=True)
    )


for nome, modelo in modelos:
    imp = obter_importancias(modelo)
    if imp is None:
        continue

    print(f"\n--- TOP 10 FEATURES - {nome.upper()} ---")
    print(imp.head(10).to_string(index=False))


# --------------------------------------------------
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