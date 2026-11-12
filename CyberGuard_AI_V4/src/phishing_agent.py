"""Agente de Phishing: usa o módulo de inferência e devolve um resultado estruturado."""
from src.phishing_inference import prever_phishing


def analisar_phishing(amostra):
    """Classifica um website (30 features) como Phishing ou Legítimo."""
    resultado = prever_phishing(amostra)

    if resultado["sucesso"] is False:
        return {
            "sucesso": False,
            "tipo": "Phishing",
            "mensagem": "Não foi possível analisar a amostra. " + resultado["erro"],
        }

    resultado["tipo"] = "Phishing"
    resultado["mensagem"] = (
        f"A amostra foi classificada como {resultado['classificacao']} "
        f"com {resultado['confianca'] * 100:.2f}% de confiança."
    )
    return resultado
