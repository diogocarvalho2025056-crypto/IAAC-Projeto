from transformers import pipeline


# --------------------------------------------------
# MODELO GENERATIVO
# --------------------------------------------------

NOME_MODELO = "Qwen/Qwen2.5-1.5B-Instruct"


# --------------------------------------------------
# CARREGAR MODELO
# --------------------------------------------------

def carregar_gerador():

    gerador = pipeline(
        "text-generation",
        model=NOME_MODELO,
        device_map="auto",
        dtype="auto"
    )

    return gerador


# --------------------------------------------------
# CRIAR MENSAGENS PARA O MODELO
# --------------------------------------------------

def criar_mensagens(
    resultado
):

    classificacao = resultado[
        "classificacao"
    ]

    confianca = (
        resultado["confianca"]
        * 100
    )

    prob_benigno = (
        resultado["probabilidade_benigno"]
        * 100
    )

    prob_malware = (
        resultado["probabilidade_malware"]
        * 100
    )


    mensagem_sistema = """
És um analista de cibersegurança.

A tua função é transformar resultados de um classificador
de Machine Learning num pequeno relatório técnico.

O classificador já tomou a decisão.

Nunca alteres a classificação.
Nunca inventes características do ficheiro.
Nunca inventes métricas.
Nunca apresentes a confiança da previsão como sendo
a precisão global do modelo.
Escreve sempre em português de Portugal.
Não digas que tu próprio analisaste o ficheiro.
Explica apenas o resultado produzido pelo classificador.
"""


    mensagem_utilizador = f"""
Resultado fornecido pelo classificador:

Classificação: {classificacao}
Confiança desta previsão: {confianca:.2f}%
Probabilidade Benigno: {prob_benigno:.2f}%
Probabilidade Malware: {prob_malware:.2f}%

Escreve apenas um parágrafo em português de Portugal.

O parágrafo deve:

- ter entre 50 e 90 palavras;
- indicar claramente a classificação;
- mencionar a confiança desta previsão;
- explicar que a decisão foi produzida por um modelo
  de Machine Learning;
- indicar que a previsão não representa uma certeza absoluta;
- não incluir títulos;
- não usar listas;
- não fazer recomendações;
- não acrescentar informação que não esteja nos dados fornecidos
Evita expressões em português do Brasil.
Usa "ficheiro" em vez de "arquivo".

Responde apenas com o parágrafo.
"""


    mensagens = [
        {
            "role": "system",
            "content": mensagem_sistema
        },
        {
            "role": "user",
            "content": mensagem_utilizador
        }
    ]


    return mensagens


# --------------------------------------------------
# GERAR RELATÓRIO
# --------------------------------------------------

def gerar_relatorio(
    resultado,
    gerador
):

    if resultado["sucesso"] is False:

        return (
            "Não foi possível gerar o relatório. "
            + resultado["mensagem"]
        )


    mensagens = criar_mensagens(
        resultado
    )


    resposta = gerador(
        mensagens,
        max_new_tokens=130,
        do_sample=False
    )


    texto_gerado = resposta[
        0
    ][
        "generated_text"
    ]


    # Quando o modelo trabalha em modo chat,
    # generated_text contém as mensagens.
    if isinstance(
        texto_gerado,
        list
    ):

        texto = texto_gerado[
            -1
        ][
            "content"
        ]

    else:

        texto = texto_gerado


    return texto.strip()