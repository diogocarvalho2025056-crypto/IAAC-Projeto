"""
Module 7 - Hyperparameter optimization for Phishing Website Detector.

Run from the project root:
    python models/optimize_xgboost.py

The test set is held out for final evaluation. RandomizedSearchCV tunes only
on the training set using stratified 5-fold cross-validation.
"""
from pathlib import Path
import json
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    classification_report, make_scorer
)
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "dataset" / "phishing_prepared.csv"
OUTPUT_PATH = ROOT / "models" / "xgboost_tuning_results.json"

RANDOM_STATE = 42
df = pd.read_csv(DATA_PATH)
X = df.drop(columns=["class"])
# Project convention: -1 = phishing, 1 = legitimate; map to 0/1 for XGBoost.
y = df["class"].map({-1: 0, 1: 1})

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

# Score recall for class 0 (phishing), because missed phishing is a key risk.
def phishing_recall(y_true, y_pred):
    return recall_score(y_true, y_pred, pos_label=0)

scoring = {
    "phishing_recall": make_scorer(phishing_recall),
    "f1_macro": "f1_macro",
    "roc_auc": "roc_auc",
}

base_model = XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=RANDOM_STATE,
    n_jobs=1,
)

param_distributions = {
    "n_estimators": [100, 200, 300, 500],
    "max_depth": [3, 4, 5, 6, 8],
    "learning_rate": [0.01, 0.03, 0.05, 0.1, 0.2],
    "subsample": [0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
    "min_child_weight": [1, 3, 5, 7],
    "reg_lambda": [1, 3, 5, 10],
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_distributions,
    n_iter=30,
    scoring=scoring,
    refit="phishing_recall",
    cv=cv,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    verbose=1,
    return_train_score=True,
)
search.fit(X_train, y_train)

best_model = search.best_estimator_
y_pred = best_model.predict(X_test)
y_proba = best_model.predict_proba(X_test)[:, 1]

results = {
    "best_params": search.best_params_,
    "best_cv_phishing_recall": float(search.best_score_),
    "test_accuracy": float(accuracy_score(y_test, y_pred)),
    "test_precision_legitimate_class_1": float(precision_score(y_test, y_pred, pos_label=1)),
    "test_recall_legitimate_class_1": float(recall_score(y_test, y_pred, pos_label=1)),
    "test_recall_phishing_class_0": float(recall_score(y_test, y_pred, pos_label=0)),
    "test_f1_macro": float(f1_score(y_test, y_pred, average="macro")),
    "test_roc_auc": float(roc_auc_score(y_test, y_proba)),
    "test_pr_auc_for_legitimate_class_1": float(average_precision_score(y_test, y_proba)),
    "confusion_matrix_labels_0_phishing_1_legitimate": confusion_matrix(y_test, y_pred).tolist(),
    "classification_report": classification_report(
        y_test, y_pred, target_names=["Phishing (0)", "Legitimate (1)"], output_dict=True
    ),
    "note": "Compare these test metrics with the original model; tuning optimizes phishing recall on CV folds."
}
OUTPUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
print("\nBest parameters:")
print(search.best_params_)
print(f"Best CV phishing recall: {search.best_score_:.4f}")
print("\nFinal held-out test results:")
for key in ["test_accuracy", "test_recall_phishing_class_0", "test_f1_macro", "test_roc_auc", "test_pr_auc_for_legitimate_class_1"]:
    print(f"{key}: {results[key]:.4f}")
print("\nConfusion matrix [[phishing->phishing, phishing->legitimate], [legitimate->phishing, legitimate->legitimate]]:")
print(results["confusion_matrix_labels_0_phishing_1_legitimate"])
print(f"\nFull results saved to: {OUTPUT_PATH}")
