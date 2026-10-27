from orchestrator import processar_pedido
from ransomware_agent import analisar_ransomware
from report_agent import gerar_relatorio, relatorio_modelo_fixo


def test_agente_classifica(malware):
    r = analisar_ransomware(
    malware,
    bruta=True
)
    assert r["sucesso"] and r["classificacao"] == "Ransomware/Malware" and "confiança" in r["mensagem"]


def test_agente_erro_amostra_invalida():
    r = analisar_ransomware({"apis": 1})
    assert r["sucesso"] is False and "Features em falta" in r["mensagem"]


def test_relatorio_nao_altera_classificacao(benigna):
    r = analisar_ransomware(
    benigna,
    bruta=True
)
    texto = gerar_relatorio(r, gerador=None)
    assert "Benigno" in texto and "certeza absoluta" in texto
    assert texto == relatorio_modelo_fixo(r)


def test_orquestrador_ransomware(malware):
    r = processar_pedido(
    "Ransomware",
    malware,
    bruta=True
)
    assert r["sucesso"] and r["tipo"] == "Ransomware" and r["relatorio"]


def test_orquestrador_tipo_desconhecido(
    malware
):

    r = processar_pedido(
        "tipo_inexistente",
        malware
    )

    assert (
        r["sucesso"] is False
        and "não suportado" in r["erro"]
    )


def test_orquestrador_propaga_erro():
    assert processar_pedido("ransomware", {})["sucesso"] is False
