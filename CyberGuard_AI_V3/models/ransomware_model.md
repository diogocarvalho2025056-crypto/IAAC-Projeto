# Ransomware/Malware Classification Model

## Identificação
- Nome: XGBoost Ransomware/Malware Classifier (baseline)
- Responsável: Tomás Matos
- Ficheiro do modelo: `models/ransomware_model.pkl` (joblib)
- Features: `models/ransomware_features.json` (165 features, ordem fixa)
- Métricas: `models/ransomware_metrics.json`

## Objetivo
Classificar ficheiros executáveis PE como:
- `0` — Benigno
- `1` — Ransomware/Malware

O target é `Class` (Benign / Malware). Os 10.876 exemplos de malware incluem Ransomware (4.762), RAT (2.647), Stealer (2.018) e Trojan (1.449); o modelo **não distingue a família**: só separa benigno de malicioso.

## Dados
- 21.752 linhas, 13.903 ficheiros distintos (`md5`): o mesmo ficheiro aparece em várias execuções.
- Divisão 70/15/15 estratificada e **agrupada por md5**: Treino 15.220, Validação 3.267, Teste 3.265 (50% malware em cada).
- Features: cabeçalho PE (estáticas) + comportamento em sandbox (dinâmicas: registo, rede, processos, ficheiros, APIs).
- `Category` e `Family` nunca entram nas features (revelam o target).

## Seleção do modelo
Sete classificadores comparados (validação + Stratified Group 5-Fold CV). Critério: maior Recall em CV entre os modelos com CV F1 ≥ 0,95 (sem este piso o Naive Bayes seria escolhido: Recall 99,8% mas Precision 53%). Resultado completo em `models/ransomware_cv_results.csv`.

O GridSearchCV do XGBoost (recall) não melhorou o baseline na validação (Recall 0,9963 vs 0,9969; F1 0,9921 vs 0,9951), por isso ficou o **XGBoost baseline**.

## Resultados no Test Set
| Métrica | Valor |
|---|---:|
| Accuracy | 99,54% |
| Precision | 99,21% |
| Recall | 99,88% |
| F1-score | 99,54% |
| ROC-AUC | 0,9993 |

| | Previsto Benigno | Previsto Malware |
|---|---:|---:|
| Real Benigno | 1620 | 13 |
| Real Malware | 2 | 1630 |

## Dependência de uma feature (importante)
`processes_malicious` concentra ~79% da importância: é > 0 em 99,8% do malware e em 1,9% do benigno. Ablação no Test Set:

| Features usadas | Recall | Precision | F1 |
|---|---:|---:|---:|
| Todas (165) | 0,9988 | 0,9921 | 0,9954 |
| Sem `processes_malicious` | 0,9884 | 0,9865 | 0,9875 |
| Só estáticas (149, sem sandbox) | 0,9467 | 0,9549 | 0,9508 |

## Inferência
Módulo `src/ransomware_inference.py`:
1. recebe um `dict` com as 165 features (`prever_ransomware`) ou uma linha bruta do `ransom.csv` (`prever_ransomware_bruto`);
2. valida features em falta/extra, valores não numéricos e NaN;
3. garante a ordem das features;
4. devolve classe, probabilidades e as 5 features que mais pesaram (contribuições SHAP do XGBoost).

## Regras para agentes
- Usar sempre o módulo de inferência; nunca inventar valores para features em falta.
- Não classificar com dados inválidos: devolver o erro.
- Apresentar a confiança como a **desta previsão**, nunca como precisão global do modelo.
- O LLM só explica o resultado; nunca altera a classificação.

## Limitações
- Resultados específicos deste dataset; não garantem desempenho com variantes novas ou amostras externas.
- Sem sandbox (features dinâmicas) o desempenho desce para F1 ≈ 0,95.
- Distingue benigno vs malware, não identifica ransomware em particular.
- O `.pkl` depende das versões de xgboost/scikit-learn; se der erro ao carregar, correr `python models/modeling.py`.
