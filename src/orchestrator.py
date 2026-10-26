"""Orquestrador do módulo de Phishing (versão autónoma do projeto do Diogo)."""

from src.phishing_agent import analisar_phishing
from src.report_agent import carregar_gerador, gerar_relatorio

_gerador = None
_gerador_carregado = False


def _obter_gerador():
    """Carrega o modelo generativo apenas na primeira utilização."""
    global _gerador, _gerador_carregado
    if not _gerador_carregado:
        _gerador = carregar_gerador()
        _gerador_carregado = True
    return _gerador


def processar_pedido(tipo, amostra):
    tipo = tipo.lower()

    if tipo == "phishing":
        resultado = analisar_phishing(amostra)
        if resultado["sucesso"] is False:
            return {"sucesso": False, "tipo": "Phishing", "erro": resultado["mensagem"]}
        return {
            "sucesso": True,
            "tipo": "Phishing",
            "resultado": resultado,
            "relatorio": gerar_relatorio(resultado, _obter_gerador()),
        }

    return {"sucesso": False, "erro": "Tipo de análise não suportado: " + tipo}
