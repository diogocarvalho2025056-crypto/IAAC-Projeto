"""Testes da integração do Phishing no orquestrador e no agente de relatórios."""
import os
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
os.environ.setdefault("IAAC_SEM_LLM", "1")  # os testes não descarregam o LLM

from src.orchestrator import processar_pedido
from src.report_agent import gerar_relatorio


@pytest.fixture(scope="module")
def dados():
    return pd.read_csv(RAIZ / "dataset" / "phishing_prepared.csv")


def _amostra(dados, classe):
    return dados[dados["class"] == classe].iloc[0].drop("class").to_dict()


def test_orquestrador_encaminha_phishing(dados):
    r = processar_pedido("phishing", _amostra(dados, -1))
    assert r["sucesso"] is True
    assert r["tipo"] == "Phishing"
    assert r["resultado"]["classificacao"] == "Phishing"
    assert isinstance(r["relatorio"], str) and r["relatorio"]


def test_tipo_e_insensivel_a_maiusculas(dados):
    assert processar_pedido("PHISHING", _amostra(dados, 1))["sucesso"] is True


def test_relatorio_de_phishing_usa_vocabulario_correto(dados):
    r = processar_pedido("phishing", _amostra(dados, 1))
    texto = r["relatorio"]
    assert "Legítimo" in texto
    assert "Phishing" in texto
    assert "Benigno" not in texto
    assert "Malware" not in texto


def test_relatorio_com_dados_invalidos(dados):
    r = processar_pedido("phishing", {"x": 1})
    assert r["sucesso"] is False
    assert "erro" in r


def test_gerar_relatorio_aceita_resultado_de_erro():
    texto = gerar_relatorio({"sucesso": False, "mensagem": "falhou"}, None)
    assert "falhou" in texto


def test_tipo_nao_suportado():
    r = processar_pedido("spyware", {})
    assert r["sucesso"] is False
