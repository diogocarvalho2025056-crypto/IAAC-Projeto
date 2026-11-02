import sys
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# CONFIGURAR CAMINHO DO PROJETO
# --------------------------------------------------

pasta_projeto = Path(__file__).resolve().parent.parent

if str(pasta_projeto) not in sys.path:

    sys.path.append(
        str(pasta_projeto)
    )


# --------------------------------------------------
# IMPORTAR AGENTES
# --------------------------------------------------

from src.malware_agent import analisar_malware

from src.report_agent import (
    carregar_gerador,
    gerar_relatorio
)


# --------------------------------------------------
# CARREGAR DATASET
# --------------------------------------------------

ficheiro_csv = (
    pasta_projeto
    / "dataset"
    / "Malware_prepared.csv"
)

df = pd.read_csv(
    ficheiro_csv
)


# --------------------------------------------------
# ESCOLHER AMOSTRA MALWARE
# --------------------------------------------------

amostra = (
    df[df["Malicious"] == 1]
    .iloc[0]
    .drop("Malicious")
    .to_dict()
)


# --------------------------------------------------
# CLASSIFICAR COM O AGENTE DE MALWARE
# --------------------------------------------------

resultado = analisar_malware(
    amostra
)


print("\n======================================")
print("RESULTADO DO CLASSIFICADOR")
print("======================================")

print(
    resultado
)


# --------------------------------------------------
# CARREGAR MODELO GENERATIVO
# --------------------------------------------------

print("\nA carregar modelo generativo...")

gerador = carregar_gerador()


# --------------------------------------------------
# GERAR RELATÓRIO
# --------------------------------------------------

relatorio = gerar_relatorio(
    resultado,
    gerador
)


print("\n======================================")
print("RELATÓRIO GERADO")
print("======================================")

print(
    relatorio
)