from pathlib import Path
import pandas as pd
from src.data.data_prep import RansomDataPipeline
from src.models.model_trainer import ModelTrainer


def main():
    root_path = Path(__file__).resolve().parent
    data_path = root_path / "data" / "raw" / "ransom.csv"

    if not data_path.exists():
        data_path = root_path / "data" / "ransom.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Ficheiro de dados não encontrado em {data_path}")

    print(f"A carregar dataset de: {data_path}")
    df = pd.read_csv(data_path)

    # 1. Instanciar e executar a pipeline de dados
    prep = RansomDataPipeline(target_col="Class")
    X, y = prep.fit_transform(df)

    # 2. Divisão em 3 conjuntos (70% Treino, 15% Validação, 15% Teste)
    X_train, X_val, X_test, y_train, y_val, y_test = prep.split_data_3way(X, y)

    print(f"Distribuição dos dados:")
    print(f" - Treino    (70%): {X_train.shape[0]} amostras")
    print(f" - Validação  (15%): {X_val.shape[0]} amostras")
    print(f" - Teste      (15%): {X_test.shape[0]} amostras\n")

    # 3. Treinar e avaliar modelos
    trainer = ModelTrainer()
    results = trainer.train_and_evaluate_3way(
        X_train, X_val, X_test, y_train, y_val, y_test
    )

    # 4. Guardar o melhor modelo na pasta /models
    models_dir = root_path / "models"
    models_dir.mkdir(exist_ok=True)
    trainer.save_best_model(models_dir / "best_model_ransom.pkl", prep.feature_names)


if __name__ == "__main__":
    main()
