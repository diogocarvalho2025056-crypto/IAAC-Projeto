import os
import pandas as pd
from src.data.make_dataset import clean_data, load_raw_data
from src.features.build_features import FeatureBuilder
from src.models.train_model import ModelTrainer
from src.agents.crew_system import CybersecurityMultiAgentSystem


def main():
    print("=" * 65)
    print(" PIPELINE CRISP-ML & SISTEMA MULTIAGENTE DE CIBERSEGURANÇA ")
    print("=" * 65)

    # 1. CRISP-ML: Data Understanding & Preparation
    print("\n[1/4] A carregar e limpar dados brutos...")
    df_raw = load_raw_data("data/raw/ransom.csv")
    df_clean = clean_data(df_raw)
    os.makedirs("data/interim", exist_ok=True)
    df_clean.to_csv("data/interim/ransom_clean.csv", index=False)

    # 2. CRISP-ML: Feature Engineering
    print("\n[2/4] A transformar atributos e codificar Hex/PE Headers...")
    builder = FeatureBuilder(target_col="Class")
    X, y = builder.transform(df_clean)
    os.makedirs("data/processed", exist_ok=True)
    processed_df = pd.concat([X, y], axis=1)
    processed_df.to_csv("data/processed/ransom_processed.csv", index=False)

    # 3. CRISP-ML: Model Training & Evaluation
    print("\n[3/4] A treinar classificadores no Scikit-Learn...")
    trainer = ModelTrainer()
    trainer.run("data/processed/ransom_processed.csv")

    # 4. CRISP-ML: Deployment & Invocação Multiagente
    print("\n[4/4] A iniciar o Sistema Multiagente Generativo...")
    agent_system = CybersecurityMultiAgentSystem(
        model_path="models/best_model_ransom.pkl"
    )

    # Amostra de teste
    sample = X.iloc[0]
    output = agent_system.analyze_sample(sample)

    print("\n" + "=" * 30 + " RESULTADO FINAL " + "=" * 30)
    print(f"Classificação : {output['prediction']}")
    print(f"Confiança     : {output['confidence']:.2%}")
    print(f"Classificador : {output['classifier_used']}")
    print(f"\nRelatório do Agente Generativo:\n{output['executive_report']}")
    print("=" * 67)


if __name__ == "__main__":
    main()
