"""Orquestrador do sistema multiagente de cibersegurança."""

from src.malware_agent import analisar_malware
from src.ransomware_agent import analisar_ransomware

from src.report_agent import (
    carregar_gerador,
    gerar_relatorio
)


# --------------------------------------------------
# MODELO GENERATIVO
# --------------------------------------------------

_gerador = None
_gerador_carregado = False


def _obter_gerador():
    """
    Carrega o modelo generativo apenas na primeira utilização.
    """

    global _gerador
    global _gerador_carregado

    if not _gerador_carregado:

        _gerador = carregar_gerador()

        _gerador_carregado = True

    return _gerador


# --------------------------------------------------
# ORQUESTRADOR
# --------------------------------------------------

def processar_pedido(
    tipo,
    amostra,
    bruta=False
):

    tipo = tipo.lower()


    # ----------------------------------------------
    # MALWARE
    # ----------------------------------------------

    if tipo == "malware":

        resultado = analisar_malware(
            amostra
        )


        if resultado["sucesso"] is False:

            return {
                "sucesso": False,
                "tipo": "Malware",
                "erro": resultado["mensagem"]
            }


        relatorio = gerar_relatorio(
            resultado,
            _obter_gerador()
        )


        return {
            "sucesso": True,
            "tipo": "Malware",
            "resultado": resultado,
            "relatorio": relatorio
        }


    # ----------------------------------------------
    # RANSOMWARE
    # ----------------------------------------------

    if tipo == "ransomware":

        resultado = analisar_ransomware(
            amostra,
            bruta=bruta
        )


        if resultado["sucesso"] is False:

            return {
                "sucesso": False,
                "tipo": "Ransomware",
                "erro": resultado["mensagem"]
            }


        relatorio = gerar_relatorio(
            resultado,
            _obter_gerador()
        )


        return {
            "sucesso": True,
            "tipo": "Ransomware",
            "resultado": resultado,
            "relatorio": relatorio
        }


    # ----------------------------------------------
    # TIPO NÃO SUPORTADO
    # ----------------------------------------------

    return {
        "sucesso": False,
        "erro": (
            "Tipo de análise não suportado: "
            + tipo
        )
    }