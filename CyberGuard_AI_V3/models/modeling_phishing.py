"""
Model Building final - Phishing Website Detector
=================================================

Pipeline completo, alinhado com os módulos de Malware e Ransomware do grupo:

  1. Carregar dataset preparado (dataset/phishing_prepared.csv)
  2. Divisão estratificada 70% treino / 15% validação / 15% teste
  3. Comparar 8 classificadores (Módulo 6 do roadmap)
  4. Avaliar na validação (Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC)
  5. Cross-validation estratificada de 5 folds (só no treino)
  6. Análise de overfitting (treino vs validação)
  7. Hyperparameter tuning do XGBoost (RandomizedSearchCV, só no treino)
  8. Seleção do modelo final (critério: Recall de phishing, entre os modelos com F1 aceitável)
  9. Avaliação única no conjunto de teste + guardar modelo e ficheiros de apoio

Convenção de classes (igual aos módulos de Malware/Ransomware: 1 = ameaça):
    0 = Legítimo
    1 = Phishing
No CSV original a coluna `class` usa -1 = phishing e 1 = legítimo; aqui converte-se.

Execução (a partir da raiz do projeto):
    python models/modeling_phishing.py            # completo
    python models/modeling_phishing.py --quick    # tuning reduzido (mais rápido)
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
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
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_validate,
    train_test_split,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

warnings.filterwarnings("ignore")

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------

PASTA_PROJETO = Path(__file__).resolve().parent.parent
FICHEIRO_CSV = PASTA_PROJETO / "dataset" / "phishing_prepared.csv"
PASTA_MODELOS = PASTA_PROJETO / "models"

CAMINHO_MODELO = PASTA_MODELOS / "phishing_xgboost.json"
CAMINHO_FEATURES = PASTA_MODELOS / "phishing_features.json"
CAMINHO_METRICAS = PASTA_MODELOS / "phishing_metrics.json"
CAMINHO_CV = PASTA_MODELOS / "phishing_cv_results.csv"

TARGET = "class"
RANDOM_STATE = 42
F1_MINIMO = 0.90  # só concorrem a "melhor modelo" os que têm F1 de validação >= 0.90


# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------

def metricas(y_real, y_pred, y_proba):
    """Métricas com Phishing (1) como classe positiva."""
    return {
        "accuracy": accuracy_score(y_real, y_pred),
        "precision": precision_score(y_real, y_pred, zero_division=0),
        "recall": recall_score(y_real, y_pred),
        "f1": f1_score(y_real, y_pred),
        "roc_auc": roc_auc_score(y_real, y_proba),
        "pr_auc": average_precision_score(y_real, y_proba),
    }


def criar_modelos():
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "k-NN": KNeighborsClassifier(n_neighbors=7),
        "Naive Bayes": GaussianNB(),
        "SVM (RBF)": SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=10, min_samples_split=20, min_samples_leaf=10, random_state=RANDOM_STATE
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=20, min_samples_leaf=5,
            random_state=RANDOM_STATE, n_jobs=1,
        ),
        "Gradient Boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
        "XGBoost": XGBClassifier(
            objective="binary:logistic", eval_metric="logloss", n_estimators=200,
            max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8,
            random_state=RANDOM_STATE, n_jobs=1,
        ),
    }


def main(quick=False):
    # --------------------------------------------------
    # 1. DATASET
    # --------------------------------------------------
    print("=" * 64)
    print("MODEL BUILDING FINAL - PHISHING WEBSITE DETECTOR")
    print("=" * 64)

    df = pd.read_csv(FICHEIRO_CSV)
    X = df.drop(columns=[TARGET])
    y = (df[TARGET] == -1).astype(int)  # 1 = Phishing, 0 = Legítimo
    features = X.columns.tolist()

    print(f"\nDataset preparado: {df.shape[0]} registos, {len(features)} features")
    print("Distribuição (0 = Legítimo, 1 = Phishing):", y.value_counts().sort_index().to_dict())

    # --------------------------------------------------
    # 2. DIVISÃO 70 / 15 / 15
    # --------------------------------------------------
    X_treino, X_resto, y_treino, y_resto = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_STATE, stratify=y
    )
    X_val, X_teste, y_val, y_teste = train_test_split(
        X_resto, y_resto, test_size=0.50, random_state=RANDOM_STATE, stratify=y_resto
    )
    print(f"\nTreino: {len(X_treino)} | Validação: {len(X_val)} | Teste: {len(X_teste)}")

    # --------------------------------------------------
    # 3-6. COMPARAÇÃO DOS MODELOS
    # --------------------------------------------------
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    modelos = criar_modelos()
    linhas = []

    print("\n--- COMPARAÇÃO DOS MODELOS (validação + CV 5-fold no treino) ---")
    for nome, modelo in modelos.items():
        modelo.fit(X_treino, y_treino)
        proba_val = modelo.predict_proba(X_val)[:, 1]
        pred_val = modelo.predict(X_val)
        m = metricas(y_val, pred_val, proba_val)

        cv_res = cross_validate(modelo, X_treino, y_treino, cv=cv, scoring=["recall", "f1"], n_jobs=1)
        acc_treino = modelo.score(X_treino, y_treino)

        linhas.append({
            "Modelo": nome,
            "Val_Accuracy": m["accuracy"],
            "Val_Precision": m["precision"],
            "Val_Recall": m["recall"],
            "Val_F1": m["f1"],
            "Val_ROC_AUC": m["roc_auc"],
            "CV_Recall_medio": cv_res["test_recall"].mean(),
            "CV_Recall_std": cv_res["test_recall"].std(),
            "CV_F1_medio": cv_res["test_f1"].mean(),
            "Acc_Treino": acc_treino,
            "Gap_Treino_Val": acc_treino - m["accuracy"],
        })
        print(f"  {nome:<20} F1 val {m['f1']:.4f} | Recall val {m['recall']:.4f} | "
              f"CV Recall {cv_res['test_recall'].mean():.4f} | gap {acc_treino - m['accuracy']:+.4f}")

    tabela = pd.DataFrame(linhas).round(4)
    tabela.to_csv(CAMINHO_CV, index=False, encoding="utf-8")
    print("\nOverfitting (gap treino-validação > 0.05 é suspeito):")
    for _, r in tabela.iterrows():
        aviso = "possível overfitting" if r["Gap_Treino_Val"] > 0.05 else "ok"
        print(f"  {r['Modelo']:<20} {r['Gap_Treino_Val']:+.4f}  {aviso}")

    # --------------------------------------------------
    # 7. TUNING DO XGBOOST (só no treino)
    # --------------------------------------------------
    n_iter = 6 if quick else 20
    print(f"\n--- HYPERPARAMETER TUNING XGBoost (RandomizedSearchCV, n_iter={n_iter}) ---")
    espaco = {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [3, 4, 5, 6, 8],
        "learning_rate": [0.03, 0.05, 0.1, 0.2],
        "subsample": [0.7, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
        "min_child_weight": [1, 3, 5],
        "reg_lambda": [1, 3, 5, 10],
    }
    pesquisa = RandomizedSearchCV(
        XGBClassifier(objective="binary:logistic", eval_metric="logloss",
                      random_state=RANDOM_STATE, n_jobs=1),
        espaco, n_iter=n_iter, scoring="recall", cv=cv, random_state=RANDOM_STATE,
        n_jobs=1, refit=True,
    )
    pesquisa.fit(X_treino, y_treino)
    xgb_tuned = pesquisa.best_estimator_
    print("Melhores parâmetros:", pesquisa.best_params_)
    print(f"Melhor Recall médio (CV): {pesquisa.best_score_:.4f}")

    proba_val_t = xgb_tuned.predict_proba(X_val)[:, 1]
    m_tuned = metricas(y_val, xgb_tuned.predict(X_val), proba_val_t)
    m_base = tabela.loc[tabela["Modelo"] == "XGBoost"].iloc[0]
    print(f"XGBoost baseline  -> Val Recall {m_base['Val_Recall']:.4f} | Val F1 {m_base['Val_F1']:.4f}")
    print(f"XGBoost otimizado -> Val Recall {m_tuned['recall']:.4f} | Val F1 {m_tuned['f1']:.4f}")

    # --------------------------------------------------
    # 8. SELEÇÃO DO MODELO FINAL
    # --------------------------------------------------
    candidatos = {nome: (modelos[nome], r) for nome, r in zip(tabela["Modelo"], tabela.to_dict("records"))}
    candidatos["XGBoost (otimizado)"] = (xgb_tuned, {
        "Val_Recall": m_tuned["recall"], "Val_F1": m_tuned["f1"],
        "Val_Accuracy": m_tuned["accuracy"],
    })
    elegiveis = {n: v for n, v in candidatos.items() if v[1]["Val_F1"] >= F1_MINIMO}
    # Critério: maior Recall de phishing na validação; desempate pelo F1.
    # Só se consideram modelos XGBoost para o ficheiro persistido (formato .json do grupo).
    elegiveis_xgb = {n: v for n, v in elegiveis.items() if isinstance(v[0], XGBClassifier)}
    escolhido = max(elegiveis_xgb, key=lambda n: (round(elegiveis_xgb[n][1]["Val_Recall"], 4),
                                                   elegiveis_xgb[n][1]["Val_F1"]))
    modelo_final = elegiveis_xgb[escolhido][0]
    melhor_geral = max(elegiveis, key=lambda n: (round(elegiveis[n][1]["Val_Recall"], 4),
                                                  elegiveis[n][1]["Val_F1"]))
    print(f"\nMelhor modelo geral na validação (Recall, depois F1): {melhor_geral}")
    print(f"Modelo guardado para o sistema multiagente (XGBoost): {escolhido}")

    # --------------------------------------------------
    # 9. AVALIAÇÃO FINAL NO TESTE (uma única vez)
    # --------------------------------------------------
    pred_t = modelo_final.predict(X_teste)
    proba_t = modelo_final.predict_proba(X_teste)[:, 1]
    final = metricas(y_teste, pred_t, proba_t)
    matriz = confusion_matrix(y_teste, pred_t)

    print("\n--- RESULTADOS FINAIS NO TEST SET ---")
    for k, v in final.items():
        print(f"  {k:<10} {v:.4f}")
    print("\nMatriz de confusão (linhas = real, colunas = previsto; 0 = Legítimo, 1 = Phishing):")
    print(matriz)
    print("\n" + classification_report(y_teste, pred_t, target_names=["Legítimo (0)", "Phishing (1)"]))

    imp = pd.Series(modelo_final.feature_importances_, index=features).sort_values(ascending=False)
    print("Top 10 features (importância):")
    print(imp.head(10).round(4).to_string())

    # --------------------------------------------------
    # GUARDAR
    # --------------------------------------------------
    modelo_final.save_model(CAMINHO_MODELO)
    CAMINHO_FEATURES.write_text(json.dumps(features, indent=2), encoding="utf-8")
    relatorio = {
        "modelo": escolhido,
        "melhor_modelo_geral_validacao": melhor_geral,
        "classes": {"0": "Legítimo", "1": "Phishing"},
        "tamanhos": {"treino": len(X_treino), "validacao": len(X_val), "teste": len(X_teste)},
        "parametros": {k: (v.item() if hasattr(v, "item") else v)
                       for k, v in modelo_final.get_params().items()
                       if k in espaco},
        "tuning": {
            "melhor_recall_cv": float(pesquisa.best_score_),
            "n_iter": n_iter,
            "melhores_parametros": {k: (v.item() if hasattr(v, "item") else v)
                                    for k, v in pesquisa.best_params_.items()},
        },
        "teste": {k: float(v) for k, v in final.items()},
        "matriz_confusao": matriz.tolist(),
        "top_features": {k: float(v) for k, v in imp.head(10).items()},
    }
    CAMINHO_METRICAS.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nGuardado: {CAMINHO_MODELO.name}, {CAMINHO_FEATURES.name}, "
          f"{CAMINHO_METRICAS.name}, {CAMINHO_CV.name}")
    print("Model Building concluído.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="tuning reduzido")
    main(quick=ap.parse_args().quick)
