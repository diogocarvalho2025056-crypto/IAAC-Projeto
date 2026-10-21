"""Agente generativo: transforma o resultado do classificador num pequeno relatório em português.

Usa um LLM local (Qwen2.5-1.5B-Instruct via transformers). Se o `transformers` não estiver
instalado (ou IAAC_SEM_LLM=1), usa um relatório por modelo fixo, para o sistema funcionar sempre.
O LLM nunca decide a classificação: apenas explica o que o classificador devolveu.
"""
import os

NOME_MODELO = "Qwen/Qwen2.5-1.5B-Instruct"


def carregar_gerador():
    if os.environ.get("IAAC_SEM_LLM") == "1":
        return None
    try:
        from transformers import pipeline
        return pipeline("text-generation", model=NOME_MODELO, device_map="auto", dtype="auto")
    except Exception as erro:  # sem transformers, sem rede, sem memória...
        print(f"[aviso] LLM indisponível ({type(erro).__name__}); a usar relatório por modelo fixo.")
        return None


def _linhas_features(resultado):
    return [
        f"{t['feature']} = {t['valor']:g} ({'aumenta' if t['contribuicao'] > 0 else 'reduz'} a probabilidade de malware)"
        for t in resultado.get("top_features", [])
    ]


def criar_mensagens(resultado):
    sistema = """
És um analista de cibersegurança.
A tua função é transformar o resultado de um classificador de Machine Learning num pequeno relatório técnico.
O classificador já tomou a decisão.

Nunca alteres a classificação.
Nunca inventes características do ficheiro nem métricas.
Nunca apresentes a confiança desta previsão como sendo a precisão global do modelo.
Escreve sempre em português de Portugal (usa "ficheiro", nunca "arquivo").
Não digas que tu próprio analisaste o ficheiro. Explica apenas o resultado do classificador.
"""
    feats = _linhas_features(resultado)
    bloco = ("\nFeatures que mais pesaram nesta previsão:\n- " + "\n- ".join(feats)) if feats else ""
    utilizador = f"""
Resultado fornecido pelo classificador:

Classificação: {resultado['classificacao']}
Confiança desta previsão: {resultado['confianca'] * 100:.2f}%
Probabilidade Benigno: {resultado['probabilidade_benigno'] * 100:.2f}%
Probabilidade Ransomware/Malware: {resultado['probabilidade_malware'] * 100:.2f}%{bloco}

Escreve apenas um parágrafo, entre 60 e 100 palavras, que:
- indique claramente a classificação e a confiança desta previsão;
- explique que a decisão foi produzida por um modelo de Machine Learning;
- mencione, só se estiverem listadas acima, as features que mais pesaram;
- indique que a previsão não é uma certeza absoluta;
- não tenha títulos nem listas e não acrescente informação que não esteja nos dados.
Responde apenas com o parágrafo.
"""
    return [{"role": "system", "content": sistema}, {"role": "user", "content": utilizador}]


def relatorio_modelo_fixo(resultado):
    """Relatório determinístico (fallback quando não há LLM)."""
    texto = (
        f"O classificador de Machine Learning atribuiu a esta amostra a classificação "
        f"{resultado['classificacao']}, com {resultado['confianca'] * 100:.2f}% de confiança nesta previsão "
        f"(Benigno: {resultado['probabilidade_benigno'] * 100:.2f}%; "
        f"Ransomware/Malware: {resultado['probabilidade_malware'] * 100:.2f}%)."
    )
    feats = _linhas_features(resultado)
    if feats:
        texto += " Features que mais pesaram: " + "; ".join(feats) + "."
    return texto + " Trata-se de uma estimativa estatística e não de uma certeza absoluta."


def gerar_relatorio(resultado, gerador=None):
    if resultado["sucesso"] is False:
        return "Não foi possível gerar o relatório. " + resultado["mensagem"]
    if gerador is None:
        return relatorio_modelo_fixo(resultado)

    resposta = gerador(criar_mensagens(resultado), max_new_tokens=160, do_sample=False)
    texto = resposta[0]["generated_text"]
    if isinstance(texto, list):  # modo chat: lista de mensagens
        texto = texto[-1]["content"]
    return texto.strip()
