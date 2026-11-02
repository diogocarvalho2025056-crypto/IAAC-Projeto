
import json

from crewai.tools import tool
from src.ransomware_agent import analisar_ransomware


# ==================================================
# ESTADO DA ANÁLISE
# ==================================================

_amostra_ransomware_atual = None
_ultimo_resultado_ransomware = None


def definir_amostra_ransomware(amostra: dict):
    """
    Prepara a amostra para uma nova análise.
    Limpa qualquer resultado de execução anterior.
    """
    global _amostra_ransomware_atual
    global _ultimo_resultado_ransomware

    _amostra_ransomware_atual = amostra
    _ultimo_resultado_ransomware = None


# ==================================================
# TOOL CREWAI
# ==================================================

@tool("Analisar Ransomware")
def analisar_ransomware_tool() -> str:
    """
    Executa a análise através do modelo XGBoost
    de Ransomware previamente treinado.
    """
    global _ultimo_resultado_ransomware

    if _amostra_ransomware_atual is None:
        return "Erro: nenhuma amostra preparada."

    try:
        resultado = analisar_ransomware(
            _amostra_ransomware_atual
        )

        _ultimo_resultado_ransomware = resultado

        return json.dumps(
            resultado,
            ensure_ascii=False,
            default=str
        )

    except Exception as erro:
        _ultimo_resultado_ransomware = None
        return f"Erro na análise: {erro}"


# ==================================================
# GUARDRAIL - VALIDAÇÃO TÉCNICA
# ==================================================

def validar_resultado_ransomware(saida):
    """
    Impede que o agente apresente uma análise
    que não tenha sido produzida pela Tool.

    O relatório final é substituído pelos
    resultados reais do modelo XGBoost.
    """

    resultado = _ultimo_resultado_ransomware

    if resultado is None:
        print(
            "\n[VALIDAÇÃO] REJEITADO: "
            "a Tool de Ransomware não foi executada."
        )

        return (
            False,
            "Não executaste a ferramenta "
            "'Analisar Ransomware'. "
            "Chama a ferramenta antes de responder."
        )

    if resultado.get("sucesso") is not True:
        return (
            False,
            "A análise técnica de Ransomware falhou."
        )

    campos_obrigatorios = (
        "classe",
        "classificacao",
        "confianca",
        "probabilidade_benigno",
        "probabilidade_malware",
        "top_features"
    )

    if any(
        campo not in resultado
        for campo in campos_obrigatorios
    ):
        return (
            False,
            "O resultado técnico do modelo "
            "está incompleto."
        )

    print(
        "\n[VALIDAÇÃO] APROVADO: "
        "Tool de Ransomware executada "
        "e resultado XGBoost confirmado."
    )

    relatorio_validado = (
        "RESULTADO TÉCNICO VALIDADO PELO XGBOOST\n\n"
        + json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
            default=str
        )
    )

    return (True, relatorio_validado)


def obter_ultimo_resultado_ransomware():
    """
    Recupera o resultado técnico produzido pela Tool,
    sem executar novamente o modelo XGBoost.
    """

    if (
        _ultimo_resultado_ransomware is None
        or _ultimo_resultado_ransomware.get("sucesso") is not True
    ):
        return None

    return _ultimo_resultado_ransomware.copy()

