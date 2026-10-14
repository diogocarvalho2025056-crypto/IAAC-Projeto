import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, f1_score


def split_dataset(
    X, y, train_size=0.70, val_size=0.15, test_size=0.15, random_state=42
):
    """
    Divide o dataset em 70% Treino, 15% Validação e 15% Teste mantendo a proporção de classes (stratified).
    """
    # Primeiro corte: separa 70% para treino e 30% para (validação + teste)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(val_size + test_size), random_state=random_state, stratify=y
    )

    # Segundo corte: divide os 30% restantes ao meio (15% validação e 15% teste)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=random_state, stratify=y_temp
    )

    print(f"🔹 Conjunto de Treino (70%): {X_train.shape[0]} amostras")
    print(f"🔹 Conjunto de Validação (15%): {X_val.shape[0]} amostras")
    print(f"🔹 Conjunto de Teste (15%): {X_test.shape[0]} amostras")

    return X_train, X_val, X_test, y_train, y_val, y_test


def get_all_classifiers():
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "DecisionTree": DecisionTreeClassifier(random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "NaiveBayes": GaussianNB(),
        "LinearSVM": LinearSVC(random_state=42, max_iter=2000),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=42),
    }


def train_and_evaluate_all_models(X_train, y_train, X_val, y_val):
    models = get_all_classifiers()
    results = []

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    best_model = None
    best_f1 = 0.0
    best_name = ""

    print("=== INICIANDO AVALIAÇÃO DE MÚLTIPLOS MODELOS ===")
    for name, model in models.items():
        cv_scores = cross_val_score(
            model, X_train, y_train, cv=cv, scoring="f1_weighted"
        )

        model.fit(X_train, y_train)
        val_preds = model.predict(X_val)
        val_f1 = f1_score(y_val, val_preds, average="weighted")

        results.append(
            {"Model": name, "CV_F1_Mean": cv_scores.mean(), "Validation_F1": val_f1}
        )

        print(f"✔️ {name:20s} | CV F1: {cv_scores.mean():.4f} | Val F1: {val_f1:.4f}")

        if val_f1 > best_f1:
            best_f1 = val_f1
            best_model = model
            best_name = name

    model_path = f"../models/{best_name.lower()}_ransomware_model.pkl"
    joblib.dump(best_model, model_path)
    print(
        f"\n🏆 Melhor modelo: {best_name} (F1 = {best_f1:.4f}) guardado em '{model_path}'"
    )

    return pd.DataFrame(results), best_model
