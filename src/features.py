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
    df_clean = df_clean.drop(columns=[col for col in drop_cols if col in df_clean.columns])
    
    # 2. Converter valores hexadecimais para inteiros decimais
    hex_cols = ['EntryPoint', 'SizeOfCode', 'SizeOfInitializedData', 'SizeOfUninitializedData', 
                'AddressOfEntryPoint', 'BaseOfCode', 'BaseOfData', 'ImageBase', 'SectionAlignment', 
                'FileAlignment', 'SizeOfImage', 'SizeOfHeaders', 'Checksum']
    
    for col in hex_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).apply(
                lambda x: int(x.split()[0], 16) if (isinstance(x, str) and (x.startswith('0x') or x.startswith('0X'))) 
                else (int(x) if str(x).isdigit() else 0)
            )
            
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