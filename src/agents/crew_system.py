import os
import joblib
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class CybersecurityMultiAgentSystem:
    def __init__(
        self,
        model_path: str = "models/best_model_ransom.pkl",
        llm_model: str = "google/flan-t5-base",
    ):
        # 1. Agente 1: Classificador ML (RandomForest)
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modelo não encontrado em '{model_path}'. Executa o train_model.py primeiro!"
            )

        data = joblib.load(model_path)
        self.classifier = data["model"]
        self.feature_names = data["features"]
        self.model_name = data.get("model_name", "RandomForest")

        print(f"[Agente 1] Classificador ML '{self.model_name}' carregado com sucesso.")

        # 2. Agente 2: Gerador de Relatórios via Flan-T5
        print(f"[Agente 2] A carregar o modelo de linguagem (LLM: {llm_model})...")
        self.tokenizer = AutoTokenizer.from_pretrained(llm_model)
        self.llm = AutoModelForSeq2SeqLM.from_pretrained(llm_model)
        print("[Agente 2] Agente Generativo pronto.")

    def analyze_sample(self, sample_series: pd.Series) -> dict:
        """Recebe as caraterísticas de um ficheiro e gera o relatório do sistema multiagente."""
        input_data = pd.DataFrame([sample_series])[self.feature_names].fillna(0)

        # AGENTE 1: Previsão do Classificador ML
        prediction_code = self.classifier.predict(input_data)[0]
        confidence = self.classifier.predict_proba(input_data).max()
        label = "Malware (Ameaça Detetada)" if prediction_code == 1 else "Benign (Ficheiro Seguro)"

        # AGENTE 2: Elaboração do Relatório com o modelo de linguagem (Prompt focado)
        if prediction_code == 1:
            prompt = (
                f"Security Alert: High risk file detected! "
                f"Status: {label} with {confidence:.2%} confidence using {self.model_name}. "
                f"Action required: Quarantining file and isolating system."
            )
        else:
            prompt = (
                f"Security Assessment: Clean file. "
                f"Status: {label} with {confidence:.2%} confidence using {self.model_name}. "
                f"Action required: File approved for execution."
            )

        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.llm.generate(**inputs, max_new_tokens=80)
        report_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {
            "prediction": label,
            "confidence": confidence,
            "classifier_used": self.model_name,
            "executive_report": report_text,
        }


if __name__ == "__main__":
    df_proc = pd.read_csv("data/processed/ransom_processed.csv")
    sample = df_proc.drop(columns=["Class"]).iloc[0]

    system = CybersecurityMultiAgentSystem()
    result = system.analyze_sample(sample)

    print("\n" + "=" * 50)
    print("      RELATÓRIO DO SISTEMA MULTIAGENTE")
    print("=" * 50)
    print(f"Resultado  : {result['prediction']}")
    print(f"Confiança  : {result['confidence']:.2%}")
    print(f"Modelo ML  : {result['classifier_used']}")
    print(f"\nRelatório IA:\n{result['executive_report']}")
    print("=" * 50)
