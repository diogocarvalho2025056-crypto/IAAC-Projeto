import ast
import pandas as pd
from sklearn.preprocessing import LabelEncoder


class FeatureBuilder:
    def __init__(self, target_col: str = "Class"):
        self.target_col = target_col
        self.label_encoders = {}
        self.feature_names = []

    def _parse_hex(self, val):
        if pd.isna(val):
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).strip()
        if val_str.startswith("0x") or val_str.startswith("0X"):
            try:
                return float(int(val_str.split()[0], 16))
            except ValueError:
                return 0.0
        try:
            return float(val_str)
        except ValueError:
            return 0.0

    def _count_flags(self, val):
        if pd.isna(val):
            return 0
        try:
            parsed = ast.literal_eval(str(val))
            return len(parsed) if isinstance(parsed, list) else 0
        except (ValueError, SyntaxError):
            return 0

    def transform(self, df: pd.DataFrame):
        data = df.copy()

        # Separar alvos e metas
        ignore = ["Category", "Family", self.target_col]
        cols = [c for c in data.columns if c not in ignore]

        # 1. Contagem de elementos em colunas com listas de flags
        list_cols = ["DllCharacteristics", "text_Characteristics", "rdata_Characteristics"]
        for c in list_cols:
            if c in cols:
                data[f"{c}_count"] = data[c].apply(self._count_flags)
                cols.append(f"{c}_count")
                cols.remove(c)

        # 2. Encoding de variáveis categóricas
        cat_cols = ["PEType", "MachineType", "magic_number", "Subsystem"]
        for c in cat_cols:
            if c in cols:
                le = LabelEncoder()
                data[c] = le.fit_transform(data[c].astype(str))
                self.label_encoders[c] = le

        # 3. Conversão de Hexadecimal/String para Float
        for c in [x for x in cols if x not in cat_cols]:
            data[c] = data[c].apply(self._parse_hex)

        X = data[cols].fillna(0.0)
        y = (data[self.target_col] == "Malware").astype(int) if self.target_col in data else None

        self.feature_names = cols
        return X, y


if __name__ == "__main__":
    df_interim = pd.read_csv("data/interim/ransom_clean.csv")
    builder = FeatureBuilder(target_col="Class")
    X, y = builder.transform(df_interim)

    processed_df = pd.concat([X, y], axis=1)
    processed_df.to_csv("data/processed/ransom_processed.csv", index=False)
    print("Dados processados salvos com sucesso em 'data/processed/ransom_processed.csv'")