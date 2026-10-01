import os
import sys
from pathlib import Path

# Adiciona a pasta raiz do projeto ao sys.path do Python
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
import pandas as pd
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from src.data.data_prep import RansomDataPipeline


class CybersecurityMultiAgentSystem:
    def __init__(
        self,
        model_path: str = None,
        llm_model_name: str = "google/flan-t5-base",
    ):
        if model_path is None:
            model_path = ROOT_DIR / "models" / "best_model_ransom.pkl"

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modelo ML não encontrado em '{model_path}'. Executa primeiro o treino!"
            )

        # 1. Agente Classificador (Scikit-Learn)
        data = joblib.load(model_path)
        self.classifier = data["model"]
        self.feature_names = data["features"]
        self.model_name = data.get("model_name", "RandomForest")
        print(f"[Agente Classificador] Modelo ML '{self.model_name}' carregado com sucesso.")

        # Pipeline para transformar amostras brutas
        self.prep_pipeline = RansomDataPipeline(target_col="Class")

        # 2. Agente Generativo (Hugging Face - Seq2Seq)
        print(f"[Agente Generativo] A carregar a LLM ({llm_model_name})...")
        self.tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
        self.llm_model = AutoModelForSeq2SeqLM.from_pretrained(llm_model_name)
        print("[Agente Generativo] Agente pronto a operar.")

    def analyze_raw_df(self, raw_df: pd.DataFrame, sample_index: int = 0) -> dict:
        """Processa uma amostra bruta do dataset executando a pipeline de pré-processamento."""
        X_prep, _ = self.prep_pipeline.fit_transform(raw_df)
        input_sample = X_prep.reindex(columns=self.feature_names, fill_value=0).iloc[[sample_index]]

        # Previsão do modelo
        pred_code = self.classifier.predict(input_sample)[0]
        confidence = float(self.classifier.predict_proba(input_sample).max())
        label = "Malware (Ameaça Detetada)" if pred_code == 1 else "Benign (Ficheiro Seguro)"

        # Relatório IA
        prompt = (
            f"Write a concise cybersecurity threat status report:\n"
            f"- File Status: {label}\n"
            f"- Detection Confidence: {confidence:.2%}\n"
            f"- Model Used: {self.model_name}\n\n"
            f"Provide a brief executive summary and security action step:"
        )

        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.llm_model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False
        )
        report_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {
            "prediction": label,
            "confidence": confidence,
            "classifier_used": self.model_name,
            "executive_report": report_text,
        }


if __name__ == "__main__":
    print("A carregar amostra de teste...")
    
    # Procura o ficheiro de dados
    data_path = ROOT_DIR / "data" / "raw" / "ransom.csv"
    if not data_path.exists():
        data_path = ROOT_DIR / "data" / "ransom.csv"
    if not data_path.exists():
        data_path = ROOT_DIR / "ransom.csv"

    if not data_path.exists():
        raise FileNotFoundError("Dataset ransom.csv não foi encontrado.")

    df = pd.read_csv(data_path)

    system = CybersecurityMultiAgentSystem()
    result = system.analyze_raw_df(df, sample_index=10877)

    print("\n" + "=" * 60)
    print("      RELATÓRIO GERADO PELO SISTEMA MULTIAGENTE")
    print("=" * 60)
    print(f"Resultado Final  : {result['prediction']}")
    print(f"Confiança        : {result['confidence']:.2%}")
    print(f"Classificador    : {result['classifier_used']}")
    print(f"\nRelatório IA (LLM):\n{result['executive_report']}")
    print("=" * 60)