"""Testes do módulo de inferência e do agente de Phishing."""
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.phishing_agent import analisar_phishing
from src.phishing_inference import carregar_features, prever_phishing, validar_amostra


@pytest.fixture(scope="module")
def dados():
    return pd.read_csv(RAIZ / "dataset" / "phishing_prepared.csv")


def _amostra(dados, classe):
    return dados[dados["class"] == classe].iloc[0].drop("class").to_dict()


def test_modelo_tem_30_features():
    assert len(carregar_features()) == 30


def test_amostra_phishing_e_classificada_como_phishing(dados):
    r = prever_phishing(_amostra(dados, -1))
    assert r["sucesso"] is True
    assert r["classe"] == 1
    assert r["classificacao"] == "Phishing"


def test_amostra_legitima_e_classificada_como_legitima(dados):
    r = prever_phishing(_amostra(dados, 1))
    assert r["sucesso"] is True
    assert r["classe"] == 0
    assert r["classificacao"] == "Legítimo"


def test_probabilidades_somam_um(dados):
    r = prever_phishing(_amostra(dados, 1))
    assert r["probabilidade_legitimo"] + r["probabilidade_phishing"] == pytest.approx(1.0)
    assert 0.5 <= r["confianca"] <= 1.0


def test_top_features_tem_5_entradas(dados):
    r = prever_phishing(_amostra(dados, -1))
    assert len(r["top_features"]) == 5
    assert {"feature", "valor", "contribuicao"} <= set(r["top_features"][0])


def test_desempenho_minimo_no_dataset_preparado(dados):
    """Verificação de sanidade: o modelo guardado separa bem as duas classes."""
    amostra = dados.sample(300, random_state=0)
    certos = 0
    for _, linha in amostra.iterrows():
        esperado = 1 if linha["class"] == -1 else 0
        r = prever_phishing(linha.drop("class").to_dict())
        certos += int(r["classe"] == esperado)
    assert certos / len(amostra) >= 0.90


def test_feature_em_falta_devolve_erro(dados):
    a = _amostra(dados, 1)
    a.pop("HTTPS")
    r = prever_phishing(a)
    assert r["sucesso"] is False
    assert "HTTPS" in r["erro"]


def test_feature_extra_devolve_erro(dados):
    a = _amostra(dados, 1)
    a["inventada"] = 1
    assert prever_phishing(a)["sucesso"] is False


def test_valor_fora_do_dominio_devolve_erro(dados):
    a = _amostra(dados, 1)
    a["HTTPS"] = 7
    r = prever_phishing(a)
    assert r["sucesso"] is False
    assert "HTTPS" in r["erro"]


def test_valor_nao_numerico_devolve_erro(dados):
    a = _amostra(dados, 1)
    a["HTTPS"] = "sim"
    assert prever_phishing(a)["sucesso"] is False


def test_entrada_que_nao_e_dicionario():
    valido, _ = validar_amostra([1, 2, 3], carregar_features())
    assert valido is False


def test_agente_devolve_mensagem_e_tipo(dados):
    r = analisar_phishing(_amostra(dados, -1))
    assert r["sucesso"] is True
    assert r["tipo"] == "Phishing"
    assert "Phishing" in r["mensagem"]


def test_agente_trata_erro_sem_excecao():
    r = analisar_phishing({"x": 1})
    assert r["sucesso"] is False
    assert r["tipo"] == "Phishing"
