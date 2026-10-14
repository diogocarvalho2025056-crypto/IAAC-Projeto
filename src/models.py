import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, f1_score

def split_dataset(X, y, train_size=0.70, val_size=0.15, test_size=0.15, random_state=42):
    """
    Divide o dataset em 70% Treino, 15% Validação e 15% Teste mantendo a proporção de classes (stratified).
    """
    # Primeiro corte: separa 70% para treino e 30% para (validação + teste)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(val_size + test_size), random_state=random_state, stratify=y
    )
    
    # Segundo corte: divide os 30% restantes ao meio (50/50 de 30% = 15% e 15%)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=random_state, stratify=y_temp
    )
    
    print(f"🔹 Conjunto de Treino (70%): {X_train.shape[0]} amostras")
    print(f"🔹 Conjunto de Validação (15%): {X_val.shape[0]} amostras")
    print(f"🔹 Conjunto de Teste (15%): {X_test.shape[0]} amostras")
    
    return X_train, X_val, X_test, y_train, y_val, y_test

def train_and_evaluate_models(X_train, X_val, y_train, y_val):
    """
    Treina os modelos no conjunto de Treino e valida no conjunto de Validação.
    """
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(eval_metric='logloss', random_state=42)
    }
    
    best_model = None
    best_f1 = 0.0
    best_name = ""
    
    for name, model in models.items():
        print(f"\n--- A Treinar {name} ---")
        model.fit(X_train, y_train)
        
        # Avaliar no conjunto de Validação (15%)
        val_preds = model.predict(X_val)
        score = f1_score(y_val, val_preds, average='weighted')
        
        print(f"Resultados no Validation Set:")
        print(classification_report(y_val, val_preds))
        
        if score > best_f1:
            best_f1 = score
            best_model = model
            best_name = name
            
    # Guardar o melhor modelo obtido na validação
    model_path = f'../models/{best_name.lower()}_ransomware_model.pkl'
    joblib.dump(best_model, model_path)
    print(f"\n✅ Melhor modelo ({best_name}) guardado com F1-Score na Validação de {best_f1:.4f} em '{model_path}'")
    
    return best_model