"""Inferência do modelo de Phishing: valida a amostra e devolve a previsão.

Convenção de classes (igual à dos módulos de Malware e Ransomware: 1 = ameaça):
    0 = Legítimo
    1 = Phishing
"""
from functools import lru_cache
import json
from numbers import Number
from pathlib import Path

import pandas as pd
from xgboost import DMatrix, XGBClassifier

PASTA_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_MODELO = PASTA_PROJETO / "models" / "phishing_xgboost.json"
CAMINHO_FEATURES = PASTA_PROJETO / "models" / "phishing_features.json"

CLASSES = {0: "Legítimo", 1: "Phishing"}

# As 30 features do dataset estão codificadas com estes três valores:
#   -1 = indicador típico de phishing | 0 = suspeito/neutro | 1 = indicador típico de legítimo
VALORES_VALIDOS = (-1, 0, 1)


@lru_cache(maxsize=1)
def carregar_features():
    with open(CAMINHO_FEATURES, "r", encoding="utf-8") as ficheiro:
        return json.load(ficheiro)


@lru_cache(maxsize=1)
def carregar_modelo():
    modelo = XGBClassifier()
    modelo.load_model(CAMINHO_MODELO)
    return modelo


def validar_amostra(amostra, features):
    """Devolve (True, msg) se a amostra tem exatamente as features esperadas, com valores -1, 0 ou 1."""
    if not isinstance(amostra, dict):
        return False, "A amostra deve ser fornecida como um dicionário."

    em_falta = [f for f in features if f not in amostra]
    if em_falta:
        return False, "Features em falta: " + ", ".join(em_falta)

    extra = [f for f in amostra if f not in features]
    if extra:
        return False, "Features não esperadas: " + ", ".join(extra)

    # bool é subclasse de int; aceita-se, mas strings/None não
    nao_numericas = [f for f in features if not isinstance(amostra[f], Number)]
    if nao_numericas:
        return False, "Valores não numéricos nas features: " + ", ".join(nao_numericas)

    nulos = [f for f in features if pd.isna(amostra[f])]
    if nulos:
        return False, "Valores em falta (NaN) nas features: " + ", ".join(nulos)

    fora_do_dominio = [f for f in features if amostra[f] not in VALORES_VALIDOS]
    if fora_do_dominio:
        return False, (
            "Valores fora do domínio permitido (-1, 0 ou 1) nas features: "
            + ", ".join(fora_do_dominio)
        )

    return True, "Dados válidos."


def prever_phishing(amostra):
    """Recebe um dict {feature: valor} e devolve a previsão do classificador."""
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
        "probabilidade_legitimo": float(p[0]),
        "probabilidade_phishing": float(p[1]),
        "top_features": _top_features(modelo, df, features),
    }


def _top_features(modelo, df, features, n=5):
    """As n features que mais contribuíram para ESTA previsão (contribuições SHAP do XGBoost).

    Contribuição positiva = empurra para Phishing; negativa = empurra para Legítimo.
    Devolve [] se não for possível calcular (não se inventam explicações).
    """
    try:
        contrib = modelo.get_booster().predict(
            DMatrix(df, feature_names=features), pred_contribs=True
        )[0][:-1]
    except Exception:
        return []
    ordem = sorted(range(len(features)), key=lambda i: abs(contrib[i]), reverse=True)[:n]
    return [
        {
            "feature": features[i],
            "valor": float(df.iloc[0][features[i]]),
            "contribuicao": float(contrib[i]),
        }
        for i in ordem
    ]
