"""Agente generativo de relatórios técnicos de cibersegurança."""

import os


# --------------------------------------------------
# MODELO GENERATIVO
# --------------------------------------------------

NOME_MODELO = "Qwen/Qwen2.5-1.5B-Instruct"


# --------------------------------------------------
# RÓTULOS POR TIPO DE ANÁLISE
# --------------------------------------------------
# Malware e Ransomware:
#   Benigno (0) / Malware (1)
#
# Phishing:
#   Legítimo (0) / Phishing (1)
# --------------------------------------------------

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


# --------------------------------------------------
# OBTER RÓTULOS CORRETOS
# --------------------------------------------------

def _rotulos(resultado):

    if resultado.get("tipo") == "Phishing":

        return ROTULOS_PHISHING

    return ROTULOS_PADRAO


# --------------------------------------------------
# CARREGAR MODELO GENERATIVO
# --------------------------------------------------

def carregar_gerador():

    # Permite executar o sistema sem LLM.
    #
    # Útil para:
    # - testes automáticos;
    # - computadores sem recursos suficientes;
    # - situações em que Transformers não esteja disponível.
    #
    # Exemplo:
    # IAAC_SEM_LLM=1

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

        contribuicao = feature[
            "contribuicao"
        ]


        # ------------------------------------------
        # SENTIDO DA CONTRIBUIÇÃO
        # ------------------------------------------

        if contribuicao > 0:

            sentido = "positiva"

        elif contribuicao < 0:

            sentido = "negativa"

        else:

            sentido = "neutra"


        # ------------------------------------------
        # FORMATAR FEATURE
        # ------------------------------------------
        #
        # Importante:
        #
        # Não interpretamos semanticamente
        # o valor da feature.
        #
        # Exemplo:
        #
        # HTTPS = 1
        #
        # Não significa automaticamente
        # "tem HTTPS" ou "não tem HTTPS".
        #
        # Apenas apresentamos:
        # - nome;
        # - valor;
        # - contribuição local.
        # ------------------------------------------

        linhas.append(
            f"{feature['feature']} = "
            f"{feature['valor']:g} "
            f"(contribuição {sentido}: "
            f"{contribuicao:+.2f})"
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
            rotulos[
                "prob_negativa"
            ]
        ]
        * 100
    )


    prob_positiva = (
        resultado[
            rotulos[
                "prob_positiva"
            ]
        ]
        * 100
    )


    # --------------------------------------------------
    # PROMPT BASE
    # --------------------------------------------------

    mensagem_sistema = """
És um analista de cibersegurança.

A tua função é transformar o resultado de um
classificador de Machine Learning num pequeno
relatório técnico.

O classificador já tomou a decisão.

Nunca alteres a classificação.

Nunca inventes características da amostra,
do ficheiro ou do website.

Nunca inventes métricas.

Nunca apresentes a confiança desta previsão
como sendo a precisão global do modelo.

Nunca uses a palavra "malwares".
Usa sempre "malware".

Nunca uses "benéfico" para representar
a classe Benigno.
Usa sempre "benigno".

Usa sempre "ficheiro" em vez de "arquivo".

Quando não souberes se a entrada representa
diretamente um ficheiro, usa a palavra "amostra".

Não afirmes que conheces características
que não foram fornecidas.

Escreve sempre em português de Portugal.

Não digas que tu próprio analisaste,
abriste ou examinaste o ficheiro ou website.

Explica apenas o resultado produzido
pelo classificador.

Nunca interpretes semanticamente o valor
numérico de uma feature a menos que essa
interpretação seja explicitamente fornecida.

Por exemplo, não afirmes que HTTPS = 1
significa presença ou ausência de HTTPS
sem existir uma descrição explícita
desse valor.

Quando existirem features com contribuição,
apresenta apenas:

- o nome da feature;
- o valor observado;
- o sentido da contribuição;
- o valor da contribuição.

Uma contribuição positiva favorece
a classificação apresentada.

Uma contribuição negativa atua
no sentido contrário à classificação apresentada.

Nunca afirmes que todas as features apresentadas
contribuíram positivamente para a classificação.

Nunca inventes relações causais entre
uma feature e a classificação.

Não digas que uma determinada característica
"significa phishing", "significa malware"
ou "significa legítimo" apenas com base
no seu valor numérico.

Prefere formulações como:

"WebsiteTraffic apresentou valor 0
e contribuição positiva de +1.87."

"HTTPS apresentou valor 1
e contribuição negativa de -1.23."

Não expliques o significado de -1, 0 ou 1
se esse significado não tiver sido
explicitamente fornecido.

As contribuições apresentadas referem-se
à previsão desta amostra.

Não confundas contribuição local
com importância global da feature no modelo.

Não afirmes que uma feature é globalmente
a mais importante do modelo apenas porque
surge entre as maiores contribuições
desta previsão.
"""


    # --------------------------------------------------
    # REGRAS ADICIONAIS PARA PHISHING
    # --------------------------------------------------
    #
    # Importante:
    # usamos += e não =
    #
    # Assim as regras gerais não são apagadas.
    # --------------------------------------------------

    if rotulos is ROTULOS_PHISHING:

        mensagem_sistema += """

Regras adicionais específicas para Phishing:

Usa sempre "phishing" para a classe Phishing
e "legítimo" para a classe Legítimo.

Nunca uses "benigno" para representar
a classe Legítimo.

Quando te referires ao objeto analisado,
usa "website" ou "amostra".

Não afirmes que visitaste, abriste
ou analisaste diretamente o website.

As features fornecidas podem possuir
valores codificados como -1, 0 ou 1.

Nunca interpretes o significado desses
valores sem uma descrição explícita
da respetiva codificação.

Por exemplo:

HTTPS = 1

não permite concluir, por si só,
que existe ou não existe HTTPS.

Quando mencionares uma feature,
limita-te a apresentar:

- o nome;
- o valor observado;
- o sentido da contribuição;
- o valor da contribuição.

Uma contribuição positiva favorece
a classificação apresentada pelo modelo.

Uma contribuição negativa atua
no sentido contrário.

Não transformes o valor da feature
numa explicação semântica.

Não afirmes que todas as features
apresentadas aumentam a probabilidade
de phishing.

Distingue claramente contribuições
positivas de contribuições negativas.
"""


    # --------------------------------------------------
    # FEATURES
    # --------------------------------------------------

    features_importantes = _linhas_features(
        resultado
    )


    bloco_features = ""


    if features_importantes:

        bloco_features = (
            "\nFeatures com maior contribuição local "
            "nesta previsão:\n- "
            + "\n- ".join(
                features_importantes
            )
        )


    # --------------------------------------------------
    # MENSAGEM DO UTILIZADOR
    # --------------------------------------------------

    mensagem_utilizador = f"""
Resultado fornecido pelo classificador:

Classificação: {classificacao}

Confiança desta previsão:
{confianca:.2f}%

Probabilidade {rotulos['negativa']}:
{prob_negativa:.2f}%

Probabilidade {rotulos['positiva']}:
{prob_positiva:.2f}%

{bloco_features}

Escreve apenas um parágrafo curto,
em português de Portugal.

Segue obrigatoriamente esta estrutura:

1. Indica a classificação e a confiança.
2. Refere que a decisão foi produzida
   por um modelo de Machine Learning.
3. Menciona exatamente duas features
   fornecidas:
   - uma com contribuição positiva;
   - uma com contribuição negativa.
4. Para cada feature, apresenta apenas
   o nome, o valor observado e a contribuição.
5. Termina dizendo que a previsão é uma
   estimativa e não uma certeza absoluta.

Não menciones mais de duas features.

Não interpretes o significado dos valores
-1, 0 ou 1.

Não expliques o que uma feature representa.

Não inventes causas ou relações.

Não faças recomendações.

Não uses listas no texto final.

Escreve entre 50 e 75 palavras.

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
            rotulos[
                "prob_negativa"
            ]
        ]
        * 100
    )


    prob_positiva = (
        resultado[
            rotulos[
                "prob_positiva"
            ]
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
        f"de {rotulos['positiva']} foi "
        f"{prob_positiva:.2f}%."
    )


    features_importantes = _linhas_features(
        resultado
    )


    if features_importantes:

        texto += (
            " Entre as features com maior contribuição "
            "local nesta previsão encontram-se: "
            + "; ".join(
                features_importantes
            )
            + "."
        )


    texto += (
        " O resultado representa uma estimativa "
        "estatística produzida pelo modelo "
        "e não uma certeza absoluta."
    )


    return texto


# --------------------------------------------------
# NORMALIZAR PORTUGUÊS
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
        "Benéfico": "Benigno",

        "aprendizado de máquina": "aprendizagem automática",
        "Aprendizado de máquina": "Aprendizagem automática",

        "sua previsão": "a previsão",
        "Sua previsão": "A previsão",
        "aprendizado": "aprendizagem",
        "Aprendizado": "Aprendizagem",

        "predição": "previsão",
        "Predição": "Previsão"
    }

    for origem, destino in substituicoes.items():

        texto = texto.replace(
            origem,
            destino
        )

    return texto

# --------------------------------------------------
# VALIDAR RELATÓRIO GERADO
# --------------------------------------------------

def relatorio_valido(
    texto
):

    if not isinstance(
        texto,
        str
    ):

        return False


    texto = texto.strip()


    if len(
        texto
    ) < 40:

        return False


    # Não queremos listas
    if "\n-" in texto:

        return False


    # Não queremos que o modelo devolva
    # campos do prompt em vez de um parágrafo
    expressoes_invalidas = [
        "Classificação:",
        "Confiança desta previsão:",
        "Decisão foi produzida",
    ]


    for expressao in expressoes_invalidas:

        if expressao in texto:

            return False


    # Deve terminar como uma frase completa
    if not texto.endswith(
        (
            ".",
            "!",
            "?"
        )
    ):

        return False


    return True

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


    if gerador is None:

        return relatorio_modelo_fixo(
            resultado
        )


    mensagens = criar_mensagens(
        resultado
    )


    resposta = gerador(
        mensagens,
        max_new_tokens=200,
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


    # --------------------------------------------------
    # PEQUENA NORMALIZAÇÃO FINAL
    # --------------------------------------------------

    texto = normalizar_portugues(
        texto
    )

    texto = texto.strip()


    # --------------------------------------------------
    # VALIDAR OUTPUT DO LLM
    # --------------------------------------------------

    if not relatorio_valido(
        texto
    ):

        return relatorio_modelo_fixo(
            resultado
        )


    return texto