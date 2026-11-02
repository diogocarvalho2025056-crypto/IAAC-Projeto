import os
import sys
from pathlib import Path

import pandas as pd
import pytest


RAIZ = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(RAIZ / "src")
)


os.environ.setdefault(
    "IAAC_SEM_LLM",
    "1"
)


@pytest.fixture(scope="session")
def amostras():

    return pd.read_csv(
        RAIZ
        / "data"
        / "processed"
        / "ransom_cleaned.csv"
    )


def _amostra(
    df,
    classe
):

    return (
        df[
            df["Class"] == classe
        ]
        .drop(
            columns="Class"
        )
        .iloc[0]
        .to_dict()
    )


@pytest.fixture()
def benigna(
    amostras
):

    return _amostra(
        amostras,
        "Benign"
    )


@pytest.fixture()
def malware(
    amostras
):

    return _amostra(
        amostras,
        "Malware"
    )