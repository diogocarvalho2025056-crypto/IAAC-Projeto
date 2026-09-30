"""
Funções utilitárias para a fase de Model Building
do projeto Phishing Website Detector.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score,
)

# Pasta base do projeto (um nível acima de src/)
PASTA_PROJETO = Path(__file__).parent.parent


# --------------------------------------------------
# 1. CARREGAR DATASET PREPARADO
# --------------------------------------------------

def carregar_dataset_preparado(nome_ficheiro="phishing_prepared.csv"):
    """Carrega o dataset preparado a partir da pasta dataset/ do projeto."""
    caminho = PASTA_PROJETO / "dataset" / nome_ficheiro
    df = pd.read_csv(caminho)
    print(f"Dataset preparado carregado: {df.shape[0]} registos × {df.shape[1]} colunas")
    return df


# --------------------------------------------------
# 2. SEPARAR FEATURES E TARGET
# --------------------------------------------------

def separar_features_target(df, target="class"):
    """Separa as variáveis de entrada (X) da variável alvo (y)."""
    X = df.drop(columns=[target])
    y = df[target]
    print(f"Features (X): {X.shape}")
    print(f"Target (y): {y.shape}")
    return X, y


# --------------------------------------------------
# 3. DIVIDIR TREINO E TESTE
# --------------------------------------------------

def dividir_treino_teste(X, y, test_size=0.20, random_state=42):
    """Divisão estratificada entre treino e teste."""
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"Treino: X_train={X_train.shape}, y_train={y_train.shape}")
    print(f"Teste:  X_test={X_test.shape}, y_test={y_test.shape}")
    return X_train, X_test, y_train, y_test


# --------------------------------------------------
# 4. CRIAR LOGISTIC REGRESSION (baseline)
# --------------------------------------------------

def criar_logistic_regression(random_state=42):
    """Cria um modelo de Regressão Logística (baseline)."""
    from sklearn.linear_model import LogisticRegression

    modelo = LogisticRegression(
        random_state=random_state,
        max_iter=1000,
        solver="lbfgs"
    )
    return modelo


# --------------------------------------------------
# 5. CRIAR DECISION TREE
# --------------------------------------------------

def criar_decision_tree(random_state=42):
    """Cria um modelo de Árvore de Decisão."""
    from sklearn.tree import DecisionTreeClassifier

    modelo = DecisionTreeClassifier(
        random_state=random_state,
        max_depth=10,
        min_samples_split=20,
        min_samples_leaf=10,
        criterion="gini"
    )
    return modelo


# --------------------------------------------------
# 6. CRIAR RANDOM FOREST
# --------------------------------------------------

def criar_random_forest(random_state=42):
    """Cria um modelo de Random Forest."""
    from sklearn.ensemble import RandomForestClassifier

    modelo = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=20,
        min_samples_leaf=5,
        random_state=random_state,
        n_jobs=-1
    )
    return modelo


# --------------------------------------------------
# 7. CRIAR XGBOOST
# --------------------------------------------------

def criar_xgboost(random_state=42):
    """Cria um modelo XGBoost."""
    from xgboost import XGBClassifier

    modelo = XGBClassifier(
        objective="binary:logistic",
        random_state=random_state,
        eval_metric="logloss",
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        n_jobs=-1
    )
    return modelo


# --------------------------------------------------
# 8. TREINAR MODELO
# --------------------------------------------------

def treinar_modelo(modelo, X_train, y_train):
    """Treina o modelo com os dados de treino."""
    modelo.fit(X_train, y_train)
    return modelo


# --------------------------------------------------
# 9. FAZER PREVISÕES
# --------------------------------------------------

def prever(modelo, X_test):
    """Faz previsões com o modelo treinado."""
    y_pred = modelo.predict(X_test)
    return y_pred


def prever_probabilidades(modelo, X_test):
    """Obtém as probabilidades previstas (para curvas ROC/PR)."""
    if hasattr(modelo, "predict_proba"):
        return modelo.predict_proba(X_test)[:, 1]
    elif hasattr(modelo, "decision_function"):
        return modelo.decision_function(X_test)
    return None


# --------------------------------------------------
# 10. AVALIAR MODELO
# --------------------------------------------------

def avaliar_modelo(nome, y_test, y_pred, y_pred_proba=None, nomes_classes=None):
    """
    Avalia o modelo calculando Accuracy, Precision, Recall, F1-score,
    matriz de confusão e relatório de classificação.
    """
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    matriz = confusion_matrix(y_test, y_pred)
    relatorio = classification_report(
        y_test, y_pred,
        target_names=nomes_classes
    )

    # ROC AUC
    roc_auc = None
    if y_pred_proba is not None:
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)

    # PR AUC (Average Precision)
    avg_precision = None
    if y_pred_proba is not None:
        avg_precision = average_precision_score(y_test, y_pred_proba)

    print("\n" + "=" * 50)
    print(nome)
    print("=" * 50)

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")

    if roc_auc is not None:
        print(f"ROC AUC:   {roc_auc:.4f}")
    if avg_precision is not None:
        print(f"PR AUC:    {avg_precision:.4f}")

    print("\nMatriz de confusão:")
    print(matriz)

    print("\nRelatório de classificação:")
    print(relatorio)

    resultados = {
        "Modelo": nome,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-score": f1,
    }

    if roc_auc is not None:
        resultados["ROC AUC"] = roc_auc
    if avg_precision is not None:
        resultados["PR AUC"] = avg_precision

    return resultados, matriz, relatorio


# --------------------------------------------------
# 11. CROSS-VALIDATION
# --------------------------------------------------

def cross_validation(modelo, X_train, y_train, cv_folds=5):
    """Executa validação cruzada estratificada e retorna as métricas."""
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)

    cv_accuracy = cross_val_score(modelo, X_train, y_train, cv=cv, scoring="accuracy")
    cv_precision = cross_val_score(modelo, X_train, y_train, cv=cv, scoring="precision")
    cv_recall = cross_val_score(modelo, X_train, y_train, cv=cv, scoring="recall")
    cv_f1 = cross_val_score(modelo, X_train, y_train, cv=cv, scoring="f1")

    print(f"\n--- CROSS-VALIDATION ({cv_folds}-fold) ---")
    print(f"  Accuracy:  {cv_accuracy.mean():.4f} ± {cv_accuracy.std():.4f}")
    print(f"  Precision: {cv_precision.mean():.4f} ± {cv_precision.std():.4f}")
    print(f"  Recall:    {cv_recall.mean():.4f} ± {cv_recall.std():.4f}")
    print(f"  F1-score:  {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")

    return {
        "cv_accuracy": cv_accuracy,
        "cv_precision": cv_precision,
        "cv_recall": cv_recall,
        "cv_f1": cv_f1,
    }


# --------------------------------------------------
# 12. COMPARAR TREINO VS TESTE (overfitting)
# --------------------------------------------------

def comparar_treino_teste(modelo, X_train, y_train, X_test, y_test):
    """Compara a accuracy de treino vs teste para detetar overfitting."""
    accuracy_treino = modelo.score(X_train, y_train)
    accuracy_teste = modelo.score(X_test, y_test)

    diferenca = accuracy_treino - accuracy_teste

    print(f"  Accuracy treino: {accuracy_treino:.4f}")
    print(f"  Accuracy teste:  {accuracy_teste:.4f}")
    print(f"  Diferença:       {diferenca:.4f}")

    if diferenca > 0.05:
        print("  ⚠ Possível overfitting (diferença > 5%)")
    else:
        print("  ✓ Sem indícios significativos de overfitting")

    return accuracy_treino, accuracy_teste


# --------------------------------------------------
# 13. COMPARAR MODELOS
# --------------------------------------------------

def comparar_modelos(resultados):
    """Cria um DataFrame com a comparação de todos os modelos."""
    tabela = pd.DataFrame(resultados)
    return tabela


# --------------------------------------------------
# 14. IMPORTÂNCIA DAS FEATURES
# --------------------------------------------------

def importancia_features(modelo, nomes_features):
    """Extrai a importância das features de um modelo."""
    importancias = None

    if hasattr(modelo, "feature_importances_"):
        importancias = modelo.feature_importances_
    elif hasattr(modelo, "coef_"):
        importancias = np.abs(modelo.coef_[0])

    if importancias is not None:
        df_imp = pd.DataFrame({
            "Feature": nomes_features,
            "Importância": importancias
        }).sort_values(by="Importância", ascending=False).reset_index(drop=True)
        return df_imp
    return None


# --------------------------------------------------
# 15. GRÁFICO MATRIZ DE CONFUSÃO
# --------------------------------------------------

def grafico_matriz_confusao(matriz, nome, ax=None):
    """Gera um heatmap da matriz de confusão."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 5))

    sns.heatmap(
        matriz, annot=True, fmt="d", cmap="Blues",
        xticklabels=["Phishing", "Legítimo"],
        yticklabels=["Phishing", "Legítimo"],
        ax=ax, cbar=True, square=True, linewidths=0.5
    )
    ax.set_xlabel("Previsto")
    ax.set_ylabel("Real")
    ax.set_title(f"Matriz de Confusão\n{nome}")
    return ax


# --------------------------------------------------
# 16. GRÁFICO COMPARAÇÃO DE MÉTRICAS
# --------------------------------------------------

def grafico_comparacao(resultados, metrica="Accuracy"):
    """Gera um gráfico de barras comparando modelos numa métrica."""
    nomes = [r["Modelo"] for r in resultados]
    valores = [r[metrica] for r in resultados]

    fig, ax = plt.subplots(figsize=(8, 5))
    cores = ["#20808D", "#437A22", "#A13544", "#8B5E3C"]
    barras = ax.bar(
        nomes, valores,
        color=cores[:len(nomes)],
        edgecolor="black", linewidth=0.5
    )

    for barra, valor in zip(barras, valores):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.005,
            f"{valor:.4f}",
            ha="center", va="bottom",
            fontsize=10, fontweight="bold"
        )

    ax.set_ylabel(metrica)
    ax.set_title(f"Comparação de Modelos — {metrica}")
    ax.set_ylim(0, max(valores) * 1.15)
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    return fig


# --------------------------------------------------
# 17. GRÁFICO CURVAS ROC
# --------------------------------------------------

def grafico_curvas_roc(modelos_resultados, y_test):
    """Gera as curvas ROC de todos os modelos num só gráfico."""
    fig, ax = plt.subplots(figsize=(8, 6))
    cores = ["#20808D", "#437A22", "#A13544", "#8B5E3C"]

    for resultado, cor in zip(modelos_resultados, cores):
        if resultado.get("y_pred_proba") is not None:
            fpr, tpr, _ = roc_curve(y_test, resultado["y_pred_proba"])
            auc_val = resultado.get("ROC AUC", 0)
            ax.plot(
                fpr, tpr, color=cor, linewidth=2,
                label=f"{resultado['Modelo']} (AUC = {auc_val:.4f})"
            )

    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Aleatório (AUC = 0.5)")
    ax.set_xlabel("Taxa de Falsos Positivos (1 - Especificidade)")
    ax.set_ylabel("Taxa de Verdadeiros Positivos (Sensibilidade)")
    ax.set_title("Curvas ROC — Comparação de Modelos")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


# --------------------------------------------------
# 18. GRÁFICO CURVAS PRECISION-RECALL
# --------------------------------------------------

def grafico_curvas_pr(modelos_resultados, y_test):
    """Gera as curvas Precision-Recall de todos os modelos."""
    fig, ax = plt.subplots(figsize=(8, 6))
    cores = ["#20808D", "#437A22", "#A13544", "#8B5E3C"]

    for resultado, cor in zip(modelos_resultados, cores):
        if resultado.get("y_pred_proba") is not None:
            precision_vals, recall_vals, _ = precision_recall_curve(
                y_test, resultado["y_pred_proba"]
            )
            ap = resultado.get("PR AUC", 0)
            ax.plot(
                recall_vals, precision_vals, color=cor, linewidth=2,
                label=f"{resultado['Modelo']} (AP = {ap:.4f})"
            )

    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Curvas Precision-Recall — Comparação de Modelos")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


# --------------------------------------------------
# 19. GRÁFICO FEATURE IMPORTANCE
# --------------------------------------------------

def grafico_feature_importance(df_importancia, nome_modelo, top_n=15):
    """Gera um gráfico de barras horizontais com as features mais importantes."""
    df_top = df_importancia.head(top_n).sort_values("Importância")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(
        df_top["Feature"], df_top["Importância"],
        color="#20808D", edgecolor="black", linewidth=0.5
    )
    ax.set_xlabel("Importância")
    ax.set_title(f"Top {top_n} Features — {nome_modelo}")
    plt.tight_layout()
    return fig


# --------------------------------------------------
# 20. GUARDAR MODELO
# --------------------------------------------------

def guardar_modelo(modelo, nome_modelo):
    """Guarda o modelo treinado na pasta models/ do projeto."""
    import joblib

    pasta_models = PASTA_PROJETO / "models"
    pasta_models.mkdir(exist_ok=True)

    caminho = pasta_models / f"{nome_modelo.lower().replace(' ', '_')}.joblib"
    joblib.dump(modelo, caminho)
    print(f"Modelo guardado em: {caminho}")
