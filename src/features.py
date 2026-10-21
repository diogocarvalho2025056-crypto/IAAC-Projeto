"""Pré-processamento e engenharia de features do dataset de Ransomware/Malware (PE).

Decisões principais (ver README):
- Campos hexadecimais ("0x00008600") e decimais ("34304") convivem na mesma coluna
  do dataset original -> convertidos para número valor a valor.
- Listas em texto (DllCharacteristics, text_Characteristics, rdata_Characteristics)
  -> uma coluna binária por flag.
- Categorias pequenas (PEType, MachineType, Subsystem, ...) -> one-hot.
- md5 NÃO é feature, mas é guardado para dividir os dados POR FICHEIRO
  (o mesmo md5 aparece várias vezes no dataset: evita fuga de informação treino/teste).
"""
import ast
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

ID_COLS = ["sha1", "file_extension"]          # eliminados (identificadores/constante)
GROUP_COL = "md5"                              # usado apenas para agrupar amostras
TARGET_COLS = ["Class", "Category", "Family"]  # nunca entram em X (Category/Family revelam o target)
REDUNDANT_COLS = ["registry_total"]            # soma de registry_read/write/delete
LIST_COLS = {                                  # coluna -> prefixo das flags
    "DllCharacteristics": "dll",
    "text_Characteristics": "text",
    "rdata_Characteristics": "rdata",
}
CATEGORICAL_COLS = ["PEType", "MachineType", "magic_number", "Magic", "Subsystem"]

_HEX = re.compile(r"^0x[0-9a-fA-F]+$")


def _to_number(value):
    """'0x00008600' -> 34304.0 ; '34304' -> 34304.0 ; '5.2' -> 5.2 ; inválido -> NaN."""
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    if not isinstance(value, str):
        return np.nan
    value = value.strip()
    if _HEX.match(value):
        return float(int(value, 16))
    try:
        return float(value)
    except ValueError:
        return np.nan


def _parse_list(value):
    if isinstance(value, str) and value.startswith("["):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return []
    return []


def clean_and_transform_features(df: pd.DataFrame) -> pd.DataFrame:
    """Devolve o dataset totalmente numérico (mais md5 e as colunas de target)."""
    out = df.copy()
    out = out.drop(columns=[c for c in ID_COLS + REDUNDANT_COLS if c in out.columns])

    # 1. Listas -> flags binárias
    for col, prefix in LIST_COLS.items():
        if col in out.columns:
            lists = out[col].apply(_parse_list)
            flags = sorted({f for lst in lists for f in lst})
            new = pd.DataFrame(
                {f"{prefix}_{f}": lists.apply(lambda lst, f=f: int(f in lst)) for f in flags},
                index=out.index,
            )
            out = pd.concat([out.drop(columns=[col]), new], axis=1)

    # 2. Categorias pequenas -> one-hot
    cats = [c for c in CATEGORICAL_COLS if c in out.columns]
    out = pd.get_dummies(out, columns=cats, dtype=int)

    # 3. Restantes colunas de texto (hex/decimal) -> número
    protected = set(TARGET_COLS + [GROUP_COL])
    for col in out.columns:
        if col in protected or pd.api.types.is_numeric_dtype(out[col]):
            continue
        out[col] = out[col].apply(_to_number)

    # 4. NaN -> 0 e remoção de colunas constantes
    feat = [c for c in out.columns if c not in protected]
    out[feat] = out[feat].fillna(0)
    constant = [c for c in feat if out[c].nunique() <= 1]
    return out.drop(columns=constant)


def prepare_datasets(df: pd.DataFrame, target_col: str = "Class", return_groups: bool = False):
    """X (features numéricas), y (0=Benign, 1=Malware), LabelEncoder [, groups (md5)].

    Aceita o dataset bruto ou já transformado (a transformação é idempotente).
    """
    processed = clean_and_transform_features(df)
    groups = processed[GROUP_COL].values if GROUP_COL in processed.columns else None
    X = processed.drop(columns=[c for c in TARGET_COLS + [GROUP_COL] if c in processed.columns])
    le = LabelEncoder()
    y = le.fit_transform(processed[target_col])
    if return_groups:
        return X, y, le, groups
    return X, y, le


# ---------------------------------------------------------------- inferência
def save_feature_list(columns, path) -> None:
    Path(path).write_text(json.dumps(list(columns), indent=2), encoding="utf-8")


def load_feature_list(path) -> list:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def raw_sample_to_features(raw_sample: dict, feature_list: list) -> dict:
    """Converte UMA amostra bruta (colunas do ransom.csv) no vetor de features do modelo.

    Flags/one-hot ausentes ficam a 0 (normal quando a categoria não ocorre).
    Não usa clean_and_transform_features porque, com uma só linha, todas as colunas
    seriam "constantes"; o resultado é alinhado à lista de features do modelo.
    """
    return _single_row_features(pd.DataFrame([raw_sample]), feature_list)


def _single_row_features(row: pd.DataFrame, feature_list: list) -> dict:
    out = row.drop(columns=[c for c in ID_COLS + REDUNDANT_COLS if c in row.columns]).copy()
    values = {}
    for col, prefix in LIST_COLS.items():
        if col in out.columns:
            for f in _parse_list(out[col].iloc[0]):
                values[f"{prefix}_{f}"] = 1.0
            out = out.drop(columns=[col])
    for col in CATEGORICAL_COLS:
        if col in out.columns:
            values[f"{col}_{out[col].iloc[0]}"] = 1.0
            out = out.drop(columns=[col])
    for col in out.columns:
        if col in TARGET_COLS or col == GROUP_COL:
            continue
        values[col] = _to_number(out[col].iloc[0])
    return {
        c: (0.0 if pd.isna(values.get(c, 0.0)) else float(values.get(c, 0.0)))
        for c in feature_list
    }
