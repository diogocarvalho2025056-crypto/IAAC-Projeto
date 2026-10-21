"""Orquestrador: encaminha cada pedido para o agente certo e gera o relatório."""
from ransomware_agent import analisar_ransomware
from report_agent import carregar_gerador, gerar_relatorio

_gerador = None
_gerador_carregado = False


def _obter_gerador():
    """Carrega o LLM só na primeira utilização (importar o módulo é barato)."""
    global _gerador, _gerador_carregado
    if not _gerador_carregado:
        _gerador, _gerador_carregado = carregar_gerador(), True
    return _gerador


def processar_pedido(tipo, amostra, bruta=False):
    tipo = tipo.lower()

    if tipo == "ransomware":
        resultado = analisar_ransomware(amostra, bruta=bruta)
        if resultado["sucesso"] is False:
            return {"sucesso": False, "tipo": "Ransomware", "erro": resultado["mensagem"]}
        return {
            "sucesso": True,
            "tipo": "Ransomware",
            "resultado": resultado,
            "relatorio": gerar_relatorio(resultado, _obter_gerador()),
        }

    return {"sucesso": False, "erro": "Tipo de análise não suportado: " + tipo}
