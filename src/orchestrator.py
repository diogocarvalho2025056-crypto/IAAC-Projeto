from src.malware_agent import analisar_malware
from src.ransomware_agent import analisar_ransomware
from src.phishing_agent import analisar_phishing

from src.report_agent import (
    carregar_gerador,
    gerar_relatorio
)


# --------------------------------------------------
# GERADOR LLM
# --------------------------------------------------

_gerador = None


def _obter_gerador():

    global _gerador

    if _gerador is None:

        _gerador = carregar_gerador()

    return _gerador


# --------------------------------------------------
# ORQUESTRADOR
# --------------------------------------------------

def processar_pedido(
    tipo,
    amostra,
    bruta=False
):

    tipo = tipo.lower().strip()


    # --------------------------------------------------
    # MALWARE
    # --------------------------------------------------

    if tipo == "malware":

        resultado = analisar_malware(
            amostra
        )


    # --------------------------------------------------
    # RANSOMWARE
    # --------------------------------------------------

    elif tipo == "ransomware":

        resultado = analisar_ransomware(
            amostra,
            bruta=bruta
        )


    # --------------------------------------------------
    # PHISHING
    # --------------------------------------------------

    elif tipo == "phishing":

        resultado = analisar_phishing(
            amostra
        )


    # --------------------------------------------------
    # TIPO NÃO SUPORTADO
    # --------------------------------------------------

    else:

        return {
            "sucesso": False,
            "tipo": tipo,
            "erro": (
                "Tipo de análise não suportado. "
                "Opções disponíveis: "
                "malware, ransomware ou phishing."
            )
        }


    # --------------------------------------------------
    # ERRO NO AGENTE
    # --------------------------------------------------

    if resultado[
        "sucesso"
    ] is False:

        return {
            "sucesso": False,
            "tipo": tipo,
            "erro": resultado.get(
                "mensagem",
                "Não foi possível analisar a amostra."
            )
        }


    # --------------------------------------------------
    # GERAR RELATÓRIO
    # --------------------------------------------------

    relatorio = gerar_relatorio(
        resultado,
        _obter_gerador()
    )


    # --------------------------------------------------
    # RESULTADO FINAL
    # --------------------------------------------------

    return {
    "sucesso": True,
    "tipo": resultado["tipo"],
    "resultado": resultado,
    "relatorio": relatorio
}