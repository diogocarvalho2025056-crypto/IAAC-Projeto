import json
from crewai_version.tools.ransomware_tool import (
    definir_amostra_ransomware
)
from pathlib import Path
from crewai_version.tools.malware_tool import (
    definir_amostra_malware
)
from crewai_version.tools.phishing_tool import (
    definir_amostra_phishing
)
from crewai_version.tools.phishing_tool import (
    definir_amostra_phishing,
    obter_ultimo_resultado_phishing
)
from crewai_version.tools.malware_tool import (
    definir_amostra_malware,
    obter_ultimo_resultado_malware
)
from crewai_version.tools.ransomware_tool import (
    definir_amostra_ransomware,
    obter_ultimo_resultado_ransomware
)
from src.visual_report import gerar_relatorio_visual
from src.malware_agent import analisar_malware
from src.ransomware_agent import analisar_ransomware
from src.phishing_agent import analisar_phishing
import pandas as pd

from crewai_version.crew import (
    criar_crew,
    criar_task_malware,
    criar_task_ransomware,
    criar_task_phishing
)


# ==================================================
# CAMINHO DO PROJETO
# ==================================================

pasta_projeto = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


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

    return (
        df_malware[
            df_malware["Malicious"] == classe
        ]
        .iloc[0]
        .drop(
            "Malicious"
        )
        .to_dict()
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


df_ransomware = None


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
            "de Ransomware..."
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


def obter_amostra_ransomware(
    classe
):

    global df_ransomware


    if df_ransomware is None:

        df_ransomware = carregar_amostras_ransomware()


    if df_ransomware is None:

        return None


    linhas = df_ransomware[
        df_ransomware["Class"] == classe
    ]


    return (
        linhas
        .iloc[0][
            features_ransomware
        ]
        .to_dict()
    )


# ==================================================
# PHISHING
# ==================================================

ficheiro_phishing = (
    pasta_projeto
    / "dataset"
    / "phishing_prepared.csv"
)


df_phishing = pd.read_csv(
    ficheiro_phishing
)


def obter_amostra_phishing(
    classe
):

    return (
        df_phishing[
            df_phishing["class"] == classe
        ]
        .iloc[0]
        .drop(
            "class"
        )
        .to_dict()
    )


# ==================================================
# EXECUTAR CREW
# ==================================================

def executar_crew(
    task
):

    crew = criar_crew(
        task
    )

    print(
        "\nA executar análise através "
        "do CrewAI + Qwen3.5 via Ollama..."
    )

    resultado = crew.kickoff()

    print("\n======================================")
    print("RESULTADO CREWAI")
    print("======================================")

    print(
        resultado
    )


# ==================================================
# MENUS
# ==================================================


def menu_malware():

    print("\n======================================")
    print("CREWAI - MALWARE")
    print("======================================")

    print("\n1 - Amostra benigna")
    print("2 - Amostra Malware")

    opcao = input("\nOpção: ").strip()

    if opcao == "1":
        amostra = obter_amostra_malware(0)

    elif opcao == "2":
        amostra = obter_amostra_malware(1)

    else:
        print("\nOpção inválida.")
        return

       # Preparar a amostra
    definir_amostra_malware(amostra)

    # Criar Task com guardrail
    task = criar_task_malware()

    try:
        executar_crew(task)

    except Exception as erro:
        print("\n[AVISO] A validação CrewAI falhou.")
        print(f"Detalhes: {erro}")
        return

    # Recuperar o resultado validado
    resultado_tecnico = obter_ultimo_resultado_malware()

    if (
        resultado_tecnico is not None
        and resultado_tecnico.get("sucesso") is True
    ):
        ficheiro = gerar_relatorio_visual(
            resultado_tecnico,
            "Malware"
        )

        print(f"\nRelatório visual: {ficheiro}")

    else:
        print(
            "\nNão existe resultado técnico válido "
            "para gerar o relatório de Malware."
        )

def menu_ransomware():

    print("\n======================================")
    print("CREWAI - RANSOMWARE")
    print("======================================")

    print("\n1 - Amostra benigna")
    print("2 - Amostra Ransomware")

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

    
    # Preparar a amostra para a Tool
    definir_amostra_ransomware(amostra)

    # Criar a Task com guardrail
    task = criar_task_ransomware()

    try:
        executar_crew(task)

    except Exception as erro:
        print("\n[AVISO] A validação CrewAI falhou.")
        print(f"Detalhes: {erro}")
        return

    # Recuperar o resultado já calculado pela Tool
    resultado_tecnico = obter_ultimo_resultado_ransomware()

    # Gerar relatório apenas com resultado técnico válido
    if (
        resultado_tecnico is not None
        and resultado_tecnico.get("sucesso") is True
    ):
        ficheiro = gerar_relatorio_visual(
            resultado_tecnico,
            "Ransomware"
        )

        print(f"\nRelatório visual: {ficheiro}")

    else:
        print(
            "\nNão existe resultado técnico válido "
            "para gerar o relatório de Ransomware."
        )



def menu_phishing():

    print("\n======================================")
    print("CREWAI - PHISHING")
    print("======================================")

    print("\n1 - Website legítimo")
    print("2 - Website de phishing")

    opcao = input("\nOpção: ").strip()

    if opcao == "1":
        amostra = obter_amostra_phishing(1)

    elif opcao == "2":
        amostra = obter_amostra_phishing(-1)

    else:
        print("\nOpção inválida.")
        return

    # Preparar a amostra para a Tool
    definir_amostra_phishing(amostra)

    # Criar a Task com validação
    task = criar_task_phishing()

    # Executar a Crew e validar o resultado
    try:
        executar_crew(task)

    except Exception as erro:
        print("\n[AVISO] A validação CrewAI falhou.")
        print(f"Detalhes: {erro}")
        return

    # Recuperar o resultado calculado pela Tool
    # sem executar novamente o modelo XGBoost
    resultado_tecnico = obter_ultimo_resultado_phishing()

    # Gerar o relatório visual apenas com resultado válido
    if (
        resultado_tecnico is not None
        and resultado_tecnico.get("sucesso") is True
    ):
        ficheiro = gerar_relatorio_visual(
            resultado_tecnico,
            "Phishing"
        )

        print(f"\nRelatório visual: {ficheiro}")

    else:
        print(
            "\nNão existe resultado técnico válido "
            "para gerar o relatório de Phishing."
        )


# ==================================================
# MENU PRINCIPAL
# ==================================================

def mostrar_menu():

    print("\n======================================")
    print("SISTEMA MULTIAGENTE - CREWAI")
    print("======================================")

    print("\n1 - Malware")
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

            menu_phishing()

        elif opcao == "0":

            print(
                "\nA terminar sistema CrewAI."
            )

            break

        else:

            print(
                "\nOpção inválida."
            )


# ==================================================
# EXECUTAR
# ==================================================

if __name__ == "__main__":

    main()