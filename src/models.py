"""Treino, validação cruzada, otimização e avaliação dos modelos de Ransomware/Malware."""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, precision_score,
    recall_score, roc_auc_score,
)
from sklearn.model_selection import (
    GridSearchCV, StratifiedGroupKFold, cross_validate,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

RANDOM_STATE = 42
MIN_CV_F1 = 0.95  # piso de F1 para um modelo poder ser escolhido pelo Recall


# ------------------------------------------------------------------ divisão
def split_dataset(X, y, groups=None, train_size=0.70, val_size=0.15, test_size=0.15,
                  random_state=RANDOM_STATE, verbose=True):
    """Divide em 70% treino / 15% validação / 15% teste, estratificado por classe.

    Se `groups` (md5) for dado, um mesmo ficheiro nunca aparece em dois conjuntos
    (StratifiedGroupKFold com 20 folds: 14 treino, 3 validação, 3 teste).
    Devolve X_train, X_val, X_test, y_train, y_val, y_test (+ g_train se houver groups).
    """
    y = np.asarray(y)
    had_groups = groups is not None
    g = np.asarray(groups) if had_groups else np.arange(len(X))  # sem groups: cada linha é um grupo

    n_folds = 20
    n_test, n_val = round(test_size * n_folds), round(val_size * n_folds)
    folds = [te for _, te in StratifiedGroupKFold(n_folds, shuffle=True, random_state=random_state).split(X, y, g)]
    te = np.concatenate(folds[:n_test])
    va = np.concatenate(folds[n_test:n_test + n_val])
    tr = np.concatenate(folds[n_test + n_val:])

    if verbose:
        for nome, idx in [("Treino", tr), ("Validação", va), ("Teste", te)]:
            print(f"🔹 {nome}: {len(idx)} amostras ({len(idx)/len(X)*100:.1f}%) | % Malware = {y[idx].mean()*100:.1f}%")
        if had_groups:
            overlap = len(set(g[tr]) & set(g[te])) + len(set(g[tr]) & set(g[va])) + len(set(g[va]) & set(g[te]))
            print(f"🔹 Ficheiros (md5) partilhados entre conjuntos: {overlap}")

    out = (X.iloc[tr], X.iloc[va], X.iloc[te], y[tr], y[va], y[te])
    return out + (g[tr],) if had_groups else out


# ------------------------------------------------------------------ modelos
def get_all_classifiers():
    """Modelos sensíveis à escala levam StandardScaler dentro de um Pipeline."""
    return {
        "LogisticRegression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
        "DecisionTree": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "KNN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "NaiveBayes": GaussianNB(),
        "LinearSVM": make_pipeline(StandardScaler(), LinearSVC(random_state=RANDOM_STATE, max_iter=5000)),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1),
        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE, n_jobs=-1),
    }


def metrics_dict(y_true, y_pred, y_score=None):
    m = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    m.update({"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)})
    if y_score is not None:
        m["roc_auc"] = roc_auc_score(y_true, y_score)
    return m


# ------------------------------------------------------- comparação de modelos
def evaluate_all_models(X_train, y_train, X_val, y_val, groups_train=None, n_splits=5):
    """Treina todos os modelos, mede no Validation Set e faz Stratified(Group) 5-Fold CV no treino.

    Métrica principal: Recall da classe Malware (ver Machine Learning Canvas), mas só entre
    modelos "elegíveis" (CV F1 >= MIN_CV_F1). Sem este piso, um modelo que classifica tudo
    como malware (ex.: Naive Bayes, Recall ~99,7% com Precision ~51%) ganharia.
    """
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    splits = list(cv.split(X_train, y_train, groups_train)) if groups_train is not None else n_splits
    rows, fitted = [], {}
    for name, model in get_all_classifiers().items():
        cvr = cross_validate(model, X_train, y_train, cv=splits, scoring=["recall", "f1"], n_jobs=1)
        model.fit(X_train, y_train)
        pred = model.predict(X_val)
        rows.append({
            "Model": name,
            "CV_Recall": cvr["test_recall"].mean(),
            "CV_F1": cvr["test_f1"].mean(),
            "Val_Recall": recall_score(y_val, pred),
            "Val_Precision": precision_score(y_val, pred),
            "Val_F1": f1_score(y_val, pred),
            "Train_Acc": accuracy_score(y_train, model.predict(X_train)),
            "Val_Acc": accuracy_score(y_val, pred),
        })
        fitted[name] = model
        print(f"✔️ {name:19s} CV Recall {rows[-1]['CV_Recall']:.4f} | CV F1 {rows[-1]['CV_F1']:.4f} "
              f"| Val Recall {rows[-1]['Val_Recall']:.4f} | Val F1 {rows[-1]['Val_F1']:.4f}")
    table = pd.DataFrame(rows)
    table["Elegivel"] = table["CV_F1"] >= MIN_CV_F1
    table = table.sort_values(["Elegivel", "CV_Recall", "CV_F1"], ascending=False).reset_index(drop=True)
    return table, fitted


# ------------------------------------------------------------ otimização
XGB_GRID = {
    "n_estimators": [100, 200],
    "max_depth": [3, 6],
    "learning_rate": [0.05, 0.1],
    "reg_lambda": [1, 5],
}


def tune_xgboost(X_train, y_train, groups_train=None, param_grid=None, n_splits=5):
    """GridSearchCV orientado ao Recall (F1 como critério de desempate via refit=recall)."""
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    splits = list(cv.split(X_train, y_train, groups_train)) if groups_train is not None else n_splits
    gs = GridSearchCV(
        XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE, n_jobs=-1),
        param_grid or XGB_GRID, scoring={"recall": "recall", "f1": "f1"},
        refit="recall", cv=splits, n_jobs=1,
    )
    gs.fit(X_train, y_train)
    # Empates em recall são frequentes: escolhe o melhor F1 entre os de recall máximo
    res = pd.DataFrame(gs.cv_results_)
    best = res[res["mean_test_recall"] >= res["mean_test_recall"].max() - 1e-12]
    best = best.sort_values("mean_test_f1", ascending=False).iloc[0]
    params = best["params"]
    model = XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE, n_jobs=-1, **params)
    model.fit(X_train, y_train)
    print(f"🔧 Melhores parâmetros: {params} | CV Recall {best['mean_test_recall']:.4f} | CV F1 {best['mean_test_f1']:.4f}")
    return model, params, res


def choose_baseline_or_tuned(baseline, tuned, X_val, y_val):
    """Mantém o baseline em caso de empate (modelo mais simples/menos risco de overfitting)."""
    sb = (recall_score(y_val, baseline.predict(X_val)), f1_score(y_val, baseline.predict(X_val)))
    st = (recall_score(y_val, tuned.predict(X_val)), f1_score(y_val, tuned.predict(X_val)))
    print(f"Validação | baseline (recall, f1) = {sb[0]:.4f}, {sb[1]:.4f} | otimizado = {st[0]:.4f}, {st[1]:.4f}")
    return (tuned, "otimizado") if st > sb else (baseline, "baseline")


# ------------------------------------------------------------ diagnóstico
def overfitting_report(models: dict, X_train, y_train, X_val, y_val) -> pd.DataFrame:
    rows = []
    for name, m in models.items():
        a, b = accuracy_score(y_train, m.predict(X_train)), accuracy_score(y_val, m.predict(X_val))
        rows.append({"Model": name, "Acc_Treino": a, "Acc_Validação": b, "Diferença_pp": (a - b) * 100})
    return pd.DataFrame(rows)


def feature_importance(model, columns, top=15) -> pd.Series:
    est = model[-1] if hasattr(model, "steps") else model
    if hasattr(est, "feature_importances_"):
        vals = est.feature_importances_
    elif hasattr(est, "coef_"):
        vals = np.abs(est.coef_).ravel()
    else:
        raise ValueError("Modelo sem importâncias de features.")
    return pd.Series(vals, index=columns).nlargest(top)


def final_evaluation(model, X_test, y_test) -> dict:
    """Só deve ser chamada UMA vez, no fim, com o Test Set."""
    pred = model.predict(X_test)
    score = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(X_test)
    return metrics_dict(y_test, pred, score)


# ------------------------------------------------------------ persistência
def save_model(model, feature_columns, models_dir, name="ransomware_model", metrics=None, meta=None):
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, models_dir / f"{name}.pkl")
    (models_dir / "ransomware_features.json").write_text(json.dumps(list(feature_columns), indent=2), encoding="utf-8")
    if metrics is not None:
        payload = {"metrics_test": metrics, **(meta or {})}
        (models_dir / "ransomware_metrics.json").write_text(json.dumps(payload, indent=2, default=float), encoding="utf-8")
