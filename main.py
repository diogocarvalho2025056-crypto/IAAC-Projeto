import sys
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# CONFIGURAR CAMINHO DO PROJETO
# --------------------------------------------------

pasta_projeto = Path(__file__).resolve().parent

if str(pasta_projeto) not in sys.path:

    sys.path.append(
        str(pasta_projeto)
    )


# --------------------------------------------------
# IMPORTAR ORQUESTRADOR
# --------------------------------------------------

from src.orchestrator import processar_pedido


# --------------------------------------------------
# CARREGAR DATASET DE MALWARE
# --------------------------------------------------

ficheiro_malware = (
    pasta_projeto
    / "dataset"
    / "Malware_prepared.csv"
)

df_malware = pd.read_csv(
    ficheiro_malware
)


# --------------------------------------------------
# OBTER AMOSTRA DE TESTE
# --------------------------------------------------

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


# --------------------------------------------------
# MENU
# --------------------------------------------------

def mostrar_menu():

    print("\n======================================")
    print("SISTEMA MULTIAGENTE DE CIBERSEGURANÇA")
    print("======================================")

    print("\nEscolha o tipo de análise:")

    print("1 - Malware")
    print("2 - Ransomware")
    print("3 - Phishing")
    print("0 - Sair")


# --------------------------------------------------
# ANALISAR MALWARE
# --------------------------------------------------

def menu_malware():

    print("\n======================================")
    print("ANÁLISE DE MALWARE")
    print("======================================")

    print("\nEscolha uma amostra de teste:")

    print("1 - Benigna")
    print("2 - Malware")

    opcao = input(
        "\nOpção: "
    )


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


# --------------------------------------------------
# FUNÇÃO PRINCIPAL
# --------------------------------------------------

def main():

    while True:

        mostrar_menu()

        opcao = input(
            "\nOpção: "
        )


        if opcao == "1":

            menu_malware()


        elif opcao == "2":

            print(
                "\nO agente de Ransomware "
                "ainda não está integrado."
            )


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


# --------------------------------------------------
# EXECUTAR PROGRAMA
# --------------------------------------------------

if __name__ == "__main__":

    main()