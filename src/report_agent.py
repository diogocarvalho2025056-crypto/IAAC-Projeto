"""Agente generativo de relatórios técnicos de cibersegurança."""

import os


# --------------------------------------------------
# MODELO GENERATIVO
# --------------------------------------------------

NOME_MODELO = "Qwen/Qwen2.5-1.5B-Instruct"


# --------------------------------------------------
# RÓTULOS POR TIPO DE ANÁLISE
# --------------------------------------------------
# Malware e Ransomware: Benigno (0) / Malware (1).
# Phishing: Legítimo (0) / Phishing (1).

ROTULOS_PADRAO = {
    "negativa": "Benigno",
    "positiva": "Malware",
    "prob_negativa": "probabilidade_benigno",
    "prob_positiva": "probabilidade_malware",
    "objeto": "ficheiro",
}

ROTULOS_PHISHING = {
    "negativa": "Legítimo",
    "positiva": "Phishing",
    "prob_negativa": "probabilidade_legitimo",
    "prob_positiva": "probabilidade_phishing",
    "objeto": "website",
}


def _rotulos(resultado):

    if resultado.get("tipo") == "Phishing":

        return ROTULOS_PHISHING

    return ROTULOS_PADRAO


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

    classe_positiva = _rotulos(
        resultado
    )["positiva"].lower()


    for feature in resultado.get(
        "top_features",
        []
    ):

        if feature[
            "contribuicao"
        ] > 0:

            efeito = (
                "aumenta a probabilidade "
                f"de {classe_positiva}"
            )

        else:

            efeito = (
                "reduz a probabilidade "
                f"de {classe_positiva}"
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

    rotulos = _rotulos(
        resultado
    )

    classificacao = resultado[
        "classificacao"
    ]

    confianca = (
        resultado[
            "confianca"
        ]
        * 100
    )

    prob_negativa = (
        resultado[
            rotulos["prob_negativa"]
        ]
        * 100
    )

    prob_positiva = (
        resultado[
            rotulos["prob_positiva"]
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
Nunca inventes características da amostra ou do ficheiro.
Nunca inventes métricas.
Nunca apresentes a confiança desta previsão
como sendo a precisão global do modelo.
Nunca uses a palavra "malwares".
Usa sempre "malware".
Nunca uses "benéfico" para representar a classe Benigno.
Usa sempre "benigno".
Usa sempre "ficheiro" em vez de "arquivo".
Quando não souberes se a entrada representa diretamente um ficheiro,
usa a palavra "amostra".
Não afirmes que conheces características que não foram fornecidas.
Escreve sempre em português de Portugal.
Não digas que tu próprio analisaste o ficheiro.
Explica apenas o resultado produzido pelo
classificador.
"""

    if rotulos is ROTULOS_PHISHING:

        mensagem_sistema = """
És um analista de cibersegurança.

A tua função é transformar o resultado de um
classificador de Machine Learning num pequeno
relatório técnico sobre phishing.

O classificador já tomou a decisão.

Nunca alteres a classificação.
Nunca inventes características do website.
Nunca inventes métricas.
Nunca apresentes a confiança desta previsão
como sendo a precisão global do modelo.
Usa sempre "phishing" para a classe Phishing
e "legítimo" para a classe Legítimo.
Nunca uses "benigno" para a classe Legítimo.
Usa sempre "website" ou "amostra".
Não afirmes que visitaste ou analisaste o website.
Não afirmes que conheces características que não foram fornecidas.
Escreve sempre em português de Portugal.
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
Probabilidade {rotulos['negativa']}: {prob_negativa:.2f}%
Probabilidade {rotulos['positiva']}: {prob_positiva:.2f}%
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

    rotulos = _rotulos(
        resultado
    )

    classificacao = resultado[
        "classificacao"
    ]

    confianca = (
        resultado[
            "confianca"
        ]
        * 100
    )

    prob_negativa = (
        resultado[
            rotulos["prob_negativa"]
        ]
        * 100
    )

    prob_positiva = (
        resultado[
            rotulos["prob_positiva"]
        ]
        * 100
    )


    texto = (
        "O classificador de Machine Learning "
        "atribuiu a esta amostra a classificação "
        f"{classificacao}, com {confianca:.2f}% "
        "de confiança nesta previsão. "
        f"A probabilidade de {rotulos['negativa']} foi "
        f"{prob_negativa:.2f}% e a probabilidade "
        f"de {rotulos['positiva']} foi {prob_positiva:.2f}%."
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
# NORMALIZAR TEXTO
# --------------------------------------------------

def normalizar_portugues(
    texto
):

    substituicoes = {
        "malwares": "malware",
        "Malwares": "Malware",
        "arquivo": "ficheiro",
        "Arquivo": "Ficheiro",
        "arquivos": "ficheiros",
        "Arquivos": "Ficheiros",
        "benéfico": "benigno",
        "Benéfico": "Benigno"
    }


    for origem, destino in substituicoes.items():

        texto = texto.replace(
            origem,
            destino
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


    texto = normalizar_portugues(
    texto
)

    return texto.strip()