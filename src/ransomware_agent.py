"""Agente de Ransomware/Malware: usa o módulo de inferência e devolve um resultado estruturado."""
from ransomware_inference import prever_ransomware, prever_ransomware_bruto


def analisar_ransomware(amostra, bruta=False):
    """Classifica uma amostra. `bruta=True` se for uma linha do ransom.csv original."""
    resultado = (prever_ransomware_bruto if bruta else prever_ransomware)(amostra)

    if resultado["sucesso"] is False:
        return {
            "sucesso": False,
            "tipo": "Ransomware",
            "mensagem": "Não foi possível analisar a amostra. " + resultado["erro"],
        }

    resultado["tipo"] = "Ransomware"
    resultado["mensagem"] = (
        f"A amostra foi classificada como {resultado['classificacao']} "
        f"com {resultado['confianca'] * 100:.2f}% de confiança."
    )
    return resultado
