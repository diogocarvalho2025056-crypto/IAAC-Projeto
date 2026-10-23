"""Agente generativo de relatórios técnicos de cibersegurança."""

import os


# --------------------------------------------------
# MODELO GENERATIVO
# --------------------------------------------------

NOME_MODELO = "Qwen/Qwen2.5-1.5B-Instruct"


# --------------------------------------------------
# CARREGAR MODELO
# --------------------------------------------------

def carregar_gerador():

    # Permite executar o sistema sem LLM,
    # por exemplo em testes ou em máquinas mais limitadas.
    if os.environ.get(
        "IAAC_SEM_LLM"
    ) == "1":

        return None


    try:

        from transformers import pipeline

        gerador = pipeline(
            "text-generation",
            model=NOME_MODELO,
            device_map="auto",
            dtype="auto"
        )

        return gerador


    except Exception as erro:

        print(
            "[aviso] LLM indisponível "
            f"({type(erro).__name__}). "
            "Será utilizado um relatório determinístico."
        )

        return None


# --------------------------------------------------
# FORMATAR FEATURES IMPORTANTES
# --------------------------------------------------

def _linhas_features(
    resultado
):

    linhas = []


    for feature in resultado.get(
        "top_features",
        []
    ):

        if feature[
            "contribuicao"
        ] > 0:

            efeito = (
                "aumenta a probabilidade "
                "de malware"
            )

        else:

            efeito = (
                "reduz a probabilidade "
                "de malware"
            )


        linhas.append(
            f"{feature['feature']} = "
            f"{feature['valor']:g} "
            f"({efeito})"
        )


    return linhas


# --------------------------------------------------
# CRIAR MENSAGENS PARA O LLM
# --------------------------------------------------

def criar_mensagens(
    resultado
):

    classificacao = resultado[
        "classificacao"
    ]

    confianca = (
        resultado[
            "confianca"
        ]
        * 100
    )

    prob_benigno = (
        resultado[
            "probabilidade_benigno"
        ]
        * 100
    )

    prob_malware = (
        resultado[
            "probabilidade_malware"
        ]
        * 100
    )


    mensagem_sistema = """
És um analista de cibersegurança.

A tua função é transformar o resultado de um
classificador de Machine Learning num pequeno
relatório técnico.

O classificador já tomou a decisão.

Nunca alteres a classificação.
Nunca inventes características do ficheiro.
Nunca inventes métricas.
Nunca apresentes a confiança desta previsão
como sendo a precisão global do modelo.

Escreve sempre em português de Portugal.

Usa "ficheiro" e nunca "arquivo".

Não digas que tu próprio analisaste o ficheiro.
Explica apenas o resultado produzido pelo
classificador.
"""


    features_importantes = _linhas_features(
        resultado
    )


    bloco_features = ""


    if features_importantes:

        bloco_features = (
            "\nFeatures que mais pesaram "
            "nesta previsão:\n- "
            + "\n- ".join(
                features_importantes
            )
        )


    mensagem_utilizador = f"""
Resultado fornecido pelo classificador:

Classificação: {classificacao}
Confiança desta previsão: {confianca:.2f}%
Probabilidade Benigno: {prob_benigno:.2f}%
Probabilidade Malware: {prob_malware:.2f}%
{bloco_features}

Escreve apenas um parágrafo em português
de Portugal.

O parágrafo deve:

- ter entre 60 e 100 palavras;
- indicar claramente a classificação;
- mencionar a confiança desta previsão;
- explicar que a decisão foi produzida
  por um modelo de Machine Learning;
- mencionar as features importantes apenas
  se tiverem sido fornecidas;
- indicar que a previsão não representa
  uma certeza absoluta;
- não incluir títulos;
- não usar listas;
- não fazer recomendações;
- não acrescentar informação que não esteja
  nos dados fornecidos.

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
# RELATÓRIO DETERMINÍSTICO
# --------------------------------------------------

def relatorio_modelo_fixo(
    resultado
):

    classificacao = resultado[
        "classificacao"
    ]

    confianca = (
        resultado[
            "confianca"
        ]
        * 100
    )

    prob_benigno = (
        resultado[
            "probabilidade_benigno"
        ]
        * 100
    )

    prob_malware = (
        resultado[
            "probabilidade_malware"
        ]
        * 100
    )


    texto = (
        "O classificador de Machine Learning "
        "atribuiu a esta amostra a classificação "
        f"{classificacao}, com {confianca:.2f}% "
        "de confiança nesta previsão. "
        f"A probabilidade de Benigno foi "
        f"{prob_benigno:.2f}% e a probabilidade "
        f"de Malware foi {prob_malware:.2f}%."
    )


    features_importantes = _linhas_features(
        resultado
    )


    if features_importantes:

        texto += (
            " As features com maior influência "
            "nesta previsão foram: "
            + "; ".join(
                features_importantes
            )
            + "."
        )


    texto += (
        " O resultado representa uma estimativa "
        "estatística e não uma certeza absoluta."
    )


    return texto


# --------------------------------------------------
# GERAR RELATÓRIO
# --------------------------------------------------

def gerar_relatorio(
    resultado,
    gerador=None
):

    if resultado[
        "sucesso"
    ] is False:

        return (
            "Não foi possível gerar o relatório. "
            + resultado[
                "mensagem"
            ]
        )


    # ----------------------------------------------
    # FALLBACK SEM LLM
    # ----------------------------------------------

    if gerador is None:

        return relatorio_modelo_fixo(
            resultado
        )


    # ----------------------------------------------
    # RELATÓRIO COM LLM
    # ----------------------------------------------

    mensagens = criar_mensagens(
        resultado
    )


    resposta = gerador(
        mensagens,
        max_new_tokens=160,
        do_sample=False
    )


    texto_gerado = resposta[
        0
    ][
        "generated_text"
    ]


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