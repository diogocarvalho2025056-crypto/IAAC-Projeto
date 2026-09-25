import os
from pathlib import Path
import joblib
import pandas as pd
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


class CybersecurityMultiAgentSystem:
    def __init__(self, model_path: str = None, llm_model: str = "google/flan-t5-base"):
        if model_path is None:
            root_dir = Path(__file__).resolve().parent.parent.parent
            model_path = root_dir / "models" / "best_model_ransom.pkl"

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo não encontrado em '{model_path}'. Treina o modelo executando 'main.py' primeiro!")

        # 1. Carregar o melhor classificador treinado
        data = joblib.load(model_path)
        self.classifier = data["model"]
        self.feature_names = data["features"]
        self.model_name = data.get("model_name", "RandomForest")

        print(f"[Agente Classificador] Modelo ML '{self.model_name}' carregado com sucesso.")

        # 2. Carregar a LLM (Flan-T5) explicitamente com AutoModelForSeq2SeqLM
        print(f"[Agente Generativo] A carregar a LLM ({llm_model})...")
        tokenizer = AutoTokenizer.from_pretrained(llm_model)
        model = AutoModelForSeq2SeqLM.from_pretrained(llm_model)
        
        self.report_generator = pipeline(
            "text2text-generation", 
            model=model, 
            tokenizer=tokenizer
        )
        print("[Agente Generativo] Agente pronto a operar.")

    def analyze_sample(self, sample_series: pd.Series) -> dict:
        """
        Interage entre o Agente Classificador (ML) e o Agente Generativo (LLM)
        para produzir uma análise conclusiva.
        """
        # Preparar a amostra com as mesmas features do treino
        input_data = pd.DataFrame([sample_series])[self.feature_names].fillna(0.0)

        # AGENTE 1: Previsão e Probabilidade
        prediction_code = self.classifier.predict(input_data)[0]
        confidence = self.classifier.predict_proba(input_data).max()
        label = "Malware (Ameaça Detetada)" if prediction_code == 1 else "Benign (Ficheiro Seguro)"

        # AGENTE 2: Elaboração do Relatório por IA
        prompt = (
            f"Generate a concise cybersecurity incident report.\n"
            f"Verdict: {label}\n"
            f"Model Confidence: {confidence:.2%}\n"
            f"Detection Algorithm: {self.model_name}\n"
            f"Provide an executive summary and key security mitigation steps."
        )

        llm_out = self.report_generator(prompt, max_new_tokens=150, do_sample=False)
        report_text = llm_out[0]["generated_text"]

        return {
            "prediction": label,
            "confidence": confidence,
            "classifier_used": self.model_name,
            "executive_report": report_text,
        }


if __name__ == "__main__":
    import sys

    # Adicionar a raiz do projeto ao sys.path para reconhecer a pasta 'src'
    root_dir = Path(__file__).resolve().parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    from src.data.data_prep import RansomDataPipeline

    print("A carregar amostra de teste...")
    data_path = root_dir / "data" / "raw" / "ransom.csv"
    
    if not data_path.exists():
        data_path = root_dir / "data" / "ransom.csv"

    df = pd.read_csv(data_path)

    # Transformar os dados
    prep = RansomDataPipeline(target_col="Class")
    X, y = prep.fit_transform(df)

    # Selecionar uma amostra para teste
    sample_to_test = X.iloc[0]

    # Executar o sistema multiagente
    system = CybersecurityMultiAgentSystem()
    result = system.analyze_sample(sample_to_test)

    print("\n" + "=" * 60)
    print("      RELATÓRIO GERADO PELO SISTEMA MULTIAGENTE")
    print("=" * 60)
    print(f"Resultado Final  : {result['prediction']}")
    print(f"Confiança        : {result['confidence']:.2%}")
    print(f"Classificador    : {result['classifier_used']}")
    print(f"\nRelatório IA (LLM):\n{result['executive_report']}")
    print("=" * 60)