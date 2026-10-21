from src.malware_agent import analisar_malware
from src.report_agent import carregar_gerador, gerar_relatorio


# --------------------------------------------------
# CARREGAR MODELO GENERATIVO
# --------------------------------------------------

gerador = carregar_gerador()


# --------------------------------------------------
# ORQUESTRADOR
# --------------------------------------------------

def processar_pedido(
    tipo,
    amostra
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
            gerador
        )


        return {
            "sucesso": True,
            "tipo": "Malware",
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