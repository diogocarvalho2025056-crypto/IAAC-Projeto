"""Inferência do modelo de Ransomware/Malware: valida a amostra e devolve a previsão."""
from functools import lru_cache
from numbers import Number
from pathlib import Path

import joblib
import pandas as pd

from features import load_feature_list, raw_sample_to_features

PASTA_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_MODELO = PASTA_PROJETO / "models" / "ransomware_model.pkl"
CAMINHO_FEATURES = PASTA_PROJETO / "models" / "ransomware_features.json"

CLASSES = {0: "Benigno", 1: "Ransomware/Malware"}


@lru_cache(maxsize=1)
def carregar_features():
    return load_feature_list(CAMINHO_FEATURES)


@lru_cache(maxsize=1)
def carregar_modelo():
    return joblib.load(CAMINHO_MODELO)


def validar_amostra(amostra, features):
    """Devolve (True, msg) se a amostra tem exatamente as features esperadas, todas numéricas."""
    if not isinstance(amostra, dict):
        return False, "A amostra deve ser fornecida como um dicionário."

    em_falta = [f for f in features if f not in amostra]
    if em_falta:
        return False, f"Features em falta ({len(em_falta)}): " + ", ".join(em_falta[:10]) + ("..." if len(em_falta) > 10 else "")

    extra = [f for f in amostra if f not in features]
    if extra:
        return False, f"Features não esperadas ({len(extra)}): " + ", ".join(extra[:10]) + ("..." if len(extra) > 10 else "")

    # bool é subclasse de int; aceita-se, mas strings/None não
    invalidos = [f for f in features if not isinstance(amostra[f], Number)]
    if invalidos:
        return False, "Valores não numéricos nas features: " + ", ".join(invalidos[:10])

    nulos = [f for f in features if pd.isna(amostra[f])]
    if nulos:
        return False, "Valores em falta (NaN) nas features: " + ", ".join(nulos[:10])

    return True, "Dados válidos."


def prever_ransomware(amostra):
    """Recebe um dict {feature: valor} já transformado e devolve a previsão."""
    features = carregar_features()
    valido, mensagem = validar_amostra(amostra, features)
    if not valido:
        return {"sucesso": False, "erro": mensagem}

    modelo = carregar_modelo()
    df = pd.DataFrame([[amostra[f] for f in features]], columns=features)  # garante a ordem
    classe = int(modelo.predict(df)[0])
    p = modelo.predict_proba(df)[0]
    return {
        "sucesso": True,
        "classe": classe,
        "classificacao": CLASSES[classe],
        "confianca": float(p[classe]),
        "probabilidade_benigno": float(p[0]),
        "probabilidade_malware": float(p[1]),
        "top_features": _top_features(modelo, df, features),
    }


def prever_ransomware_bruto(amostra_bruta):
    """Como prever_ransomware, mas recebe uma linha do ransom.csv original (hex/decimal, listas em texto)."""
    if not isinstance(amostra_bruta, dict):
        return {"sucesso": False, "erro": "A amostra deve ser fornecida como um dicionário."}
    return prever_ransomware(raw_sample_to_features(amostra_bruta, carregar_features()))


def _top_features(modelo, df, features, n=5):
    """As n features que mais contribuíram para ESTA previsão (contribuições SHAP do XGBoost).

    Devolve [] se o modelo não for XGBoost (não se inventam explicações).
    """
    try:
        from xgboost import DMatrix
        contrib = modelo.get_booster().predict(DMatrix(df, feature_names=features), pred_contribs=True)[0][:-1]
    except Exception:
        return []
    ordem = sorted(range(len(features)), key=lambda i: abs(contrib[i]), reverse=True)[:n]
    return [{"feature": features[i], "valor": float(df.iloc[0][features[i]]), "contribuicao": float(contrib[i])}
            for i in ordem]
