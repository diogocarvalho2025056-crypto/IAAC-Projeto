import pandas as pd

def load_raw_data(filepath: str = "data/raw/ransom.csv") -> pd.DataFrame:
    df = pd.read_csv(filepath)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica limpeza e remove atributos irrelevantes/constantes."""
    df_clean = df.copy()
    
    # Identificadores de ficheiro sem valor preditivo
    hashes = ["md5", "sha1"]
    
    # Deteta automaticamente qualquer coluna com variância zero (ex: file_extension, network_threats)
    zero_variance_cols = [col for col in df_clean.columns if df_clean[col].nunique() <= 1]
    
    # Junta todas as colunas a remover
    cols_to_drop = list(set(hashes + zero_variance_cols))
    
    df_clean = df_clean.drop(columns=cols_to_drop, errors='ignore')
    df_clean = df_clean.fillna(0)
    
    print(f"Removidas {len(cols_to_drop)} colunas: {cols_to_drop}")
    return df_clean

if __name__ == "__main__":
    df_raw = load_raw_data()
    df_clean = clean_data(df_raw)
    
    df_clean.to_csv("data/interim/ransom_clean.csv", index=False)
    print("Dados limpos guardados em 'data/interim/ransom_clean.csv'")