import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split


class ModelTrainer:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models = {
            "LogisticRegression": LogisticRegression(max_iter=1000, random_state=random_state),
            "DecisionTree": DecisionTreeClassifier(random_state=random_state),
            "RandomForest": RandomForestClassifier(n_estimators=100, random_state=random_state),
        }
        self.best_model = None
        self.best_model_name = ""
        self.best_f1_score = 0.0

    def run(self, data_path: str = "data/processed/ransom_processed.csv"):
        df = pd.read_csv(data_path)
        X = df.drop(columns=["Class"])
        y = df["Class"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=y
        )

        results = {}
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)
            f1 = f1_score(y_test, preds)

            results[name] = {"accuracy": acc, "f1_score": f1, "report": classification_report(y_test, preds)}

            if f1 > self.best_f1_score:
                self.best_f1_score = f1
                self.best_model = model
                self.best_model_name = name

        os.makedirs("models", exist_ok=True)
        model_path = "models/best_model_ransom.pkl"
        joblib.dump({"model": self.best_model, "features": X.columns.tolist(), "model_name": self.best_model_name}, model_path)
        print(f"Melhor modelo ({self.best_model_name}) guardado em '{model_path}' com F1-Score: {self.best_f1_score:.4f}")
        return results


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run()