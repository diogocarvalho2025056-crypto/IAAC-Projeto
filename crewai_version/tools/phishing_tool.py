
import json

from crewai.tools import tool
from src.phishing_agent import analisar_phishing


_amostra_phishing_atual = None
_ultimo_resultado_phishing = None


def definir_amostra_phishing(amostra: dict):
    """
    Prepara a amostra e limpa o resultado anterior.
    """
    global _amostra_phishing_atual
    global _ultimo_resultado_phishing

    _amostra_phishing_atual = amostra.copy()
    _ultimo_resultado_phishing = None


@tool("Analisar Phishing")
def analisar_phishing_tool() -> str:
    """
    Executa o modelo XGBoost sobre a amostra
    de Phishing previamente preparada.
    """
    global _ultimo_resultado_phishing

    if _amostra_phishing_atual is None:
        return "Erro: nenhuma amostra de Phishing preparada."

    try:
        # Evitar inferências repetidas da mesma amostra
        if (
            _ultimo_resultado_phishing is not None
            and _ultimo_resultado_phishing.get("sucesso") is True
        ):
            resultado = _ultimo_resultado_phishing
        else:
            resultado = analisar_phishing(
                _amostra_phishing_atual
            )
            _ultimo_resultado_phishing = resultado

        return json.dumps(
            resultado,
            ensure_ascii=False,
            default=str
        )

    except Exception as erro:
        _ultimo_resultado_phishing = None
        return f"Erro na análise de Phishing: {erro}"


def validar_resultado_phishing(saida):
    """
    Guardrail: só aceita uma análise validada
    através da Tool e do modelo XGBoost.
    """

    resultado = _ultimo_resultado_phishing

    if resultado is None:
        print(
            "\n[VALIDAÇÃO] REJEITADO: "
            "a Tool de Phishing não foi executada."
        )

        return (
            False,
            "Não executaste a ferramenta "
            "'Analisar Phishing'. "
            "Executa-a antes de responder."
        )

    if resultado.get("sucesso") is not True:
        return (
            False,
            "A análise técnica de Phishing falhou."
        )

    campos_obrigatorios = (
        "classe",
        "classificacao",
        "confianca",
        "probabilidade_legitimo",
        "probabilidade_phishing",
        "top_features"
    )

    if any(
        campo not in resultado
        for campo in campos_obrigatorios
    ):
        return (
            False,
            "O resultado do modelo está incompleto."
        )

    print(
        "\n[VALIDAÇÃO] APROVADO: "
        "Tool de Phishing executada e "
        "resultado XGBoost confirmado."
    )

    relatorio = (
        "RESULTADO TÉCNICO VALIDADO PELO XGBOOST\n\n"
        + json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
            default=str
        )
    )

    return (True, relatorio)

def obter_ultimo_resultado_phishing():
    """
    Devolve o resultado técnico já calculado
    pela Tool, sem executar novamente o XGBoost.
    """

    if (
        _ultimo_resultado_phishing is None
        or _ultimo_resultado_phishing.get("sucesso") is not True
    ):
        return None

    return _ultimo_resultado_phishing.copy()