import json
import sys

from pathlib import Path

import pandas as pd


# --------------------------------------------------
# CONFIGURAR CAMINHO DO PROJETO
# --------------------------------------------------

pasta_projeto = Path(__file__).resolve().parent

if str(pasta_projeto) not in sys.path:

    sys.path.insert(
        0,
        str(pasta_projeto)
    )


# --------------------------------------------------
# IMPORTAR ORQUESTRADOR
# --------------------------------------------------

from src.orchestrator import processar_pedido


# ==================================================
# MALWARE
# ==================================================

ficheiro_malware = (
    pasta_projeto
    / "dataset"
    / "Malware_prepared.csv"
)

df_malware = pd.read_csv(
    ficheiro_malware
)


def obter_amostra_malware(
    classe
):

    amostra = (
        df_malware[
            df_malware["Malicious"] == classe
        ]
        .iloc[0]
        .drop("Malicious")
        .to_dict()
    )

    return amostra


def menu_malware():

    print("\n======================================")
    print("ANÁLISE DE MALWARE")
    print("======================================")

    print("\nEscolha uma amostra de teste:")

    print("1 - Benigna")
    print("2 - Malware")


    opcao = input(
        "\nOpção: "
    ).strip()


    if opcao == "1":

        amostra = obter_amostra_malware(
            0
        )

    elif opcao == "2":

        amostra = obter_amostra_malware(
            1
        )

    else:

        print(
            "\nOpção inválida."
        )

        return


    print(
        "\nA processar análise..."
    )


    resultado = processar_pedido(
        "malware",
        amostra
    )


    if resultado["sucesso"] is False:

        print(
            "\nErro:"
        )

        print(
            resultado["erro"]
        )

        return


    resultado_tecnico = resultado[
        "resultado"
    ]


    print("\n======================================")
    print("RESULTADO TÉCNICO")
    print("======================================")

    print(
        "Classificação:",
        resultado_tecnico[
            "classificacao"
        ]
    )

    print(
        "Confiança:",
        f"{resultado_tecnico['confianca'] * 100:.2f}%"
    )

    print(
        "Probabilidade Benigno:",
        f"{resultado_tecnico['probabilidade_benigno'] * 100:.2f}%"
    )

    print(
        "Probabilidade Malware:",
        f"{resultado_tecnico['probabilidade_malware'] * 100:.2f}%"
    )


    print("\n======================================")
    print("RELATÓRIO GERADO")
    print("======================================")

    print(
        resultado["relatorio"]
    )


# ==================================================
# RANSOMWARE
# ==================================================

ficheiro_demo_ransomware = (
    pasta_projeto
    / "data"
    / "processed"
    / "ransom_demo_samples.csv"
)

ficheiro_ransomware_limpo = (
    pasta_projeto
    / "data"
    / "processed"
    / "ransom_cleaned.csv"
)

caminho_features_ransomware = (
    pasta_projeto
    / "models"
    / "ransomware_features.json"
)


with open(
    caminho_features_ransomware,
    "r",
    encoding="utf-8"
) as ficheiro:

    features_ransomware = json.load(
        ficheiro
    )


rotulos_ransomware = {
    "benign": 0,
    "benigno": 0,
    "malware": 1,
    "0": 0,
    "1": 1
}


def carregar_amostras_ransomware():

    if ficheiro_demo_ransomware.exists():

        df = pd.read_csv(
            ficheiro_demo_ransomware
        )


    elif ficheiro_ransomware_limpo.exists():

        from src.features import prepare_datasets
        from src.models import split_dataset


        print(
            "\nA preparar amostras de teste "
            "a partir de ransom_cleaned.csv..."
        )


        X, y, _, grupos = prepare_datasets(
            pd.read_csv(
                ficheiro_ransomware_limpo
            ),
            return_groups=True
        )


        (
            _,
            _,
            X_test,
            _,
            _,
            y_test,
            _
        ) = split_dataset(
            X,
            y,
            grupos,
            verbose=False
        )


        df = X_test.copy()

        df[
            "Class"
        ] = y_test


    else:

        print(
            "\nNão foram encontradas amostras "
            "de Ransomware."
        )

        return None


    df[
        "Class"
    ] = (
        df["Class"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(
            rotulos_ransomware
        )
    )


    if df["Class"].isna().any():

        print(
            "\nA coluna Class contém "
            "valores inválidos."
        )

        return None


    return df


df_ransomware = carregar_amostras_ransomware()


def obter_amostra_ransomware(
    classe,
    indice=0
):

    if df_ransomware is None:

        return None


    linhas = df_ransomware[
        df_ransomware["Class"] == classe
    ]


    features_em_falta = [
        feature
        for feature in features_ransomware
        if feature not in linhas.columns
    ]


    if features_em_falta:

        print(
            "\nFaltam features no dataset "
            "de Ransomware:"
        )

        print(
            features_em_falta[:5]
        )

        return None


    amostra = (
        linhas
        .iloc[
            indice % len(linhas)
        ][
            features_ransomware
        ]
        .to_dict()
    )


    return amostra


def menu_ransomware():

    print("\n======================================")
    print("ANÁLISE DE RANSOMWARE")
    print("======================================")

    print("\nEscolha uma amostra de teste:")

    print(
        "1 - Amostra benigna"
    )

    print(
        "2 - Amostra de malware"
    )


    opcao = input(
        "\nOpção: "
    ).strip()


    if opcao == "1":

        amostra = obter_amostra_ransomware(
            0
        )

    elif opcao == "2":

        amostra = obter_amostra_ransomware(
            1
        )

    else:

        print(
            "\nOpção inválida."
        )

        return


    if amostra is None:

        return


    print(
        "\nA processar análise..."
    )


    resultado = processar_pedido(
        "ransomware",
        amostra
    )


    if resultado["sucesso"] is False:

        print(
            "\nErro:"
        )

        print(
            resultado["erro"]
        )

        return


    resultado_tecnico = resultado[
        "resultado"
    ]


    print("\n======================================")
    print("RESULTADO TÉCNICO")
    print("======================================")

    print(
        "Classificação:",
        resultado_tecnico[
            "classificacao"
        ]
    )

    print(
        "Confiança:",
        f"{resultado_tecnico['confianca'] * 100:.2f}%"
    )

    print(
        "Probabilidade Benigno:",
        f"{resultado_tecnico['probabilidade_benigno'] * 100:.2f}%"
    )

    print(
        "Probabilidade Malware:",
        f"{resultado_tecnico['probabilidade_malware'] * 100:.2f}%"
    )


    if "top_features" in resultado_tecnico:

        print(
            "\nFeatures com maior contribuição:"
        )

        for feature in resultado_tecnico[
            "top_features"
        ]:

            print(
                f"- {feature['feature']} = "
                f"{feature['valor']:g} "
                f"(contribuição "
                f"{feature['contribuicao']:+.2f})"
            )


    print("\n======================================")
    print("RELATÓRIO GERADO")
    print("======================================")

    print(
        resultado["relatorio"]
    )


# ==================================================
# MENU PRINCIPAL
# ==================================================

def mostrar_menu():

    print("\n======================================")
    print("SISTEMA MULTIAGENTE DE CIBERSEGURANÇA")
    print("======================================")

    print("\nEscolha o tipo de análise:")

    print("1 - Malware")
    print("2 - Ransomware")
    print("3 - Phishing")
    print("0 - Sair")


# ==================================================
# FUNÇÃO PRINCIPAL
# ==================================================

def main():

    while True:

        mostrar_menu()


        opcao = input(
            "\nOpção: "
        ).strip()


        if opcao == "1":

            menu_malware()


        elif opcao == "2":

            menu_ransomware()


        elif opcao == "3":

            print(
                "\nO agente de Phishing "
                "ainda não está integrado."
            )


        elif opcao == "0":

            print(
                "\nA terminar o sistema."
            )

            break


        else:

            print(
                "\nOpção inválida."
            )


# ==================================================
# EXECUTAR PROGRAMA
# ==================================================

if __name__ == "__main__":

    main()