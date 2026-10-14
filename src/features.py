import pandas as pd
import numpy as np
import ast
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder

def clean_and_transform_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e transforma os recursos brutos do dataset de Ransomware.
    """
    df_clean = df.copy()
    
    # 1. Eliminar identificadores unívocos
    drop_cols = ['md5', 'sha1', 'file_extension']
    
    # 2. Eliminar colunas nulas ou constantes (como network_threats se estiver a 0/NaN)
    # e redundantes (ex: registry_total)
    redundant_cols = ['registry_total']
    
    df_clean = df_clean.drop(columns=[col for col in drop_cols + redundant_cols if col in df_clean.columns])
    
    # Remover colunas que só têm 1 único valor ou são 100% NaN
    for col in df_clean.columns:
        if df_clean[col].nunique() <= 1 or df_clean[col].isnull().all():
            df_clean = df_clean.drop(columns=[col])

    # Tratar eventuais NAs restantes preenchendo com 0 nas variáveis numéricas
    num_cols = df_clean.select_dtypes(include=[np.number]).columns
    df_clean[num_cols] = df_clean[num_cols].fillna(0)
            
    # 3. Processar listas em texto (ex: DllCharacteristics)
    if 'DllCharacteristics' in df_clean.columns:
        def parse_list(val):
            try:
                return ast.literal_eval(val) if isinstance(val, str) and val.startswith('[') else []
            except:
                return []
        
        parsed_series = df_clean['DllCharacteristics'].apply(parse_list)
        mlb = MultiLabelBinarizer()
        dll_encoded = pd.DataFrame(
            mlb.fit_transform(parsed_series), 
            columns=[f"dll_{c}" for c in mlb.classes_], 
            index=df_clean.index
        )
        df_clean = pd.concat([df_clean.drop(columns=['DllCharacteristics']), dll_encoded], axis=1)
        
    return df_clean

def prepare_datasets(df: pd.DataFrame, target_col: str = 'Class'):
    """
    Prepara matriz de features X e vetor target y para treino.
    """
    df_processed = clean_and_transform_features(df)
    
    # Separar X e targets
    X = df_processed.drop(columns=['Class', 'Category', 'Family'], errors='ignore')
    
    # Manter apenas colunas numéricas
    X = X.select_dtypes(include=[np.number])
    
    le = LabelEncoder()
    y = le.fit_transform(df_processed[target_col])
    
    return X, y, le