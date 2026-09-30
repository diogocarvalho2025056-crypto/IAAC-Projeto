# Phishing Website Detector — Diogo Carvalho

Projeto de Machine Learning para deteção de websites de phishing, seguindo a metodologia CRISP-ML(Q).

## Estrutura do Projeto

```
Phishing-Diogo-Carvalho/
├── Business_understanding/
│   ├── Business and Data Understanding - Phishing Website Detector.docx
│   ├── EAD_phishing.py
│   └── Machine Learning Canvas DiogoCarvalho.docx.pdf
├── Data_Preparation/
│   ├── Data Preparation — Phishing Website Detector.docx
│   └── data_preparation.py
├── models/
│   ├── Model_Building_Phishing.docx
│   ├── modeling.py
│   ├── comparacao_modelos.csv
│   ├── graficos/
│   │   ├── matrizes_confusao.png
│   │   ├── comparacao_accuracy.png
│   │   ├── comparacao_precision.png
│   │   ├── comparacao_recall.png
│   │   ├── comparacao_f1-score.png
│   │   ├── curvas_roc.png
│   │   ├── curvas_precision_recall.png
│   │   ├── feature_importance_logistic_regression.png
│   │   ├── feature_importance_decision_tree.png
│   │   ├── feature_importance_random_forest.png
│   │   └── feature_importance_xgboost.png
│   ├── logistic_regression.joblib
│   ├── decision_tree.joblib
│   ├── random_forest.joblib
│   └── xgboost.joblib
├── dataset/
│   ├── phishing.csv
│   └── phishing_prepared.csv
├── notebooks/
│   ├── data_understanding.ipynb
│   ├── data_preparation.ipynb
│   └── model_building.ipynb
└── src/
    ├── __init__.py
    ├── eda_utils.py
    ├── data_preparation_utils.py
    └── model_utils.py
```

## Descrição das Pastas

### Business_understanding/
Contém os documentos da fase de Business e Data Understanding e o script de EDA.
- **Business and Data Understanding - Phishing Website Detector.docx** — Documento com a análise do problema, dos dados e critérios de sucesso.
- **EAD_phishing.py** — Script Python com a Análise Exploratória de Dados (EDA).
- **Machine Learning Canvas DiogoCarvalho.docx.pdf** — Machine Learning Canvas do projeto.

### Data_Preparation/
Contém o documento e o script da fase de Data Preparation.
- **Data Preparation — Phishing Website Detector.docx** — Documento com todas as decisões de preparação dos dados.
- **data_preparation.py** — Script que executa a preparação completa dos dados (remoção de Index, perfis contraditórios, duplicados, divisão treino/teste, etc.).

### dataset/
Contém o dataset original e o dataset preparado.
- **phishing.csv** — Dataset original com 11.054 registos × 32 colunas.
- **phishing_prepared.csv** — Dataset preparado com 5.721 registos × 31 colunas (após limpeza).

### notebooks/
Notebooks Jupyter com a análise e preparação interativa dos dados.
- **data_understanding.ipynb** — EDA completa do dataset (distribuições, correlações, gráficos).
- **data_preparation.ipynb** — Execução passo a passo da preparação dos dados.

### src/
Módulos utilitários reutilizáveis.
- **__init__.py** — Inicializador do pacote.
- **eda_utils.py** — Funções para análise exploratória (carregamento, distribuições, correlações, gráficos).
- **data_preparation_utils.py** — Funções para preparação de dados (remoção de colunas, perfis contraditórios, duplicados, divisão treino/teste).
- **model_utils.py** — Funções para modelação (criar modelos, treinar, prever, avaliar, comparar, feature importance, gráficos).

### models/
Contém os ficheiros da fase de Model Building.
- **Model_Building_Phishing.docx** — Documento com a descrição completa da fase de modelação.
- **modeling.py** — Script que treina e avalia os 4 modelos (Logistic Regression, Decision Tree, Random Forest, XGBoost).
- **comparacao_modelos.csv** — Tabela comparativa dos resultados.
- **graficos/** — Gráficos gerados (matrizes de confusão, curvas ROC, PR, feature importance, comparação de métricas).
- ***.joblib** — Modelos treinados guardados.

## Como Executar

1. **EDA (script):**
   ```bash
   cd Business_understanding
   python EAD_phishing.py
   ```

2. **Data Preparation (script):**
   ```bash
   cd Data_Preparation
   python data_preparation.py
   ```

3. **Model Building (script):**
   ```bash
   cd models
   python modeling.py
   ```

4. **Notebooks:**
   Abrir os ficheiros `.ipynb` na pasta `notebooks/` com Jupyter Notebook ou VS Code.

## Resumo do Dataset

| Indicador | Valor |
|-----------|-------|
| Dataset original | 11.054 registos × 32 colunas |
| Após remoção do Index | 11.054 × 31 |
| Perfis contraditórios removidos | 64 perfis (357 registos) |
| Após remoção de duplicados | 5.721 × 31 |
| Treino | 4.576 registos (80%) |
| Teste | 1.145 registos (20%) |
| Classes | Legítimo (1): 48,35% / Phishing (-1): 51,65% |
| Scaling | Não aplicado (features em [-1, 0, 1]) |

## Próximos Passos
- Otimização de hiperparâmetros (GridSearchCV ou RandomizedSearchCV)
- Avaliação do impacto da remoção de features altamente correlacionadas
- Interpretação dos modelos e conclusões finais
- Protótipo funcional: receber características de um website e devolver classificação
