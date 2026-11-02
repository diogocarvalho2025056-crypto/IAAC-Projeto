"""Pipeline completo de modela├º├úo (equivalente aos notebooks 02 -> 04).

Executar a partir da raiz do projeto:
    python models/modeling.py            # tuning completo (alguns minutos)
    python models/modeling.py --quick    # sem GridSearch (teste r├ípido)

Produz:
    models/ransomware_model.pkl         modelo final
    models/ransomware_features.json     lista (e ordem) das features
    models/ransomware_metrics.json      m├®tricas finais no Test Set
    models/ransomware_cv_results.csv    compara├º├úo de modelos (CV + valida├º├úo)
    data/processed/ransom_demo_samples.csv  amostras do Test Set para main.py e testes
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from features import prepare_datasets  # noqa: E402
from models import (  # noqa: E402
    choose_baseline_or_tuned, evaluate_all_models, feature_importance, final_evaluation,
    overfitting_report, save_model, split_dataset, tune_xgboost,
)

parser = argparse.ArgumentParser()
parser.add_argument("--quick", action="store_true", help="salta o GridSearchCV")
args = parser.parse_args()

# 1. Dados -------------------------------------------------------------------
raw = pd.read_csv(RAIZ / "data" / "raw" / "ransom.csv")
X, y, le, groups = prepare_datasets(raw, return_groups=True)
print(f"Dataset: {raw.shape[0]} linhas, {raw['md5'].nunique()} ficheiros ├║nicos | {X.shape[1]} features | classes: {list(le.classes_)}")

# 2. Divis├úo 70/15/15 por ficheiro (md5) ---------------------------------------
X_train, X_val, X_test, y_train, y_val, y_test, g_train = split_dataset(X, y, groups)

# 3. Compara├º├úo de modelos (valida├º├úo + 5-Fold CV) --------------------------------
tabela, ajustados = evaluate_all_models(X_train, y_train, X_val, y_val, g_train)
tabela.to_csv(RAIZ / "models" / "ransomware_cv_results.csv", index=False)
print("\n", tabela.round(4).to_string(index=False))
melhor_nome = tabela.iloc[0]["Model"]
print(f"\n­ƒÅå Melhor por CV Recall entre os eleg├¡veis (CV F1 >= 0.95): {melhor_nome}")

# 4. Otimiza├º├úo do XGBoost + escolha baseline/otimizado ------------------------
modelo_final, versao = ajustados[melhor_nome], "baseline"
params = {}
if melhor_nome == "XGBoost" and not args.quick:
    otimizado, params, _ = tune_xgboost(X_train, y_train, g_train)
    modelo_final, versao = choose_baseline_or_tuned(ajustados["XGBoost"], otimizado, X_val, y_val)
    ajustados["XGBoost (otimizado)"] = otimizado
print(f"Modelo final: {melhor_nome} ({versao})")

# 5. Overfitting -------------------------------------------------------------
print("\n", overfitting_report(ajustados, X_train, y_train, X_val, y_val).round(4).to_string(index=False))

# 6. Avalia├º├úo final no Test Set (uma ├║nica vez) ---------------------------------
metricas = final_evaluation(modelo_final, X_test, y_test)
print("\n=== TEST SET ===")
for k, v in metricas.items():
    print(f"{k:10s} {v:.4f}" if isinstance(v, float) else f"{k:10s} {v}")
print("\nTop 10 features:\n", feature_importance(modelo_final, X.columns, 10).round(4).to_string())

# 7. Guardar ------------------------------------------------------------------
save_model(modelo_final, X.columns, RAIZ / "models", metrics=metricas,
           meta={"modelo": melhor_nome, "versao": versao,
                 "parametros": params if versao == "otimizado" else {},
                 "melhores_parametros_gridsearch": params,
                 "n_features": X.shape[1], "treino": len(X_train), "validacao": len(X_val), "teste": len(X_test)})

demo = pd.concat([X_test[y_test == 0].head(10), X_test[y_test == 1].head(10)])
demo["Class"] = [0] * 10 + [1] * 10   # 0 = Benign, 1 = Malware
demo.to_csv(RAIZ / "data" / "processed" / "ransom_demo_samples.csv", index=False)
print("\nÔ£à Modelo, features, m├®tricas e amostras de demonstra├º├úo guardados.")
