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
# IMPORTAR ORQUESTRADOR
# --------------------------------------------------

from src.orchestrator import processar_pedido


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
# PROCESSAR PEDIDO
# --------------------------------------------------

print("\n======================================")
print("TESTE DO ORQUESTRADOR")
print("======================================")

resultado = processar_pedido(
    "malware",
    amostra
)


print(
    "\nResultado técnico:"
)

print(
    resultado["resultado"]
)


print(
    "\nRelatório:"
)

print(
    resultado["relatorio"]
)