# Phishing Classification Model

## Identificação

Nome do modelo: XGBoost Phishing Classifier (otimizado)

Tema: Phishing Website Detection

Responsável: Diogo Carvalho

## Objetivo

Este modelo classifica um website como:

- `0` — Legítimo
- `1` — Phishing

A classificação é feita a partir de **30 características já extraídas** de cada website (por exemplo `HTTPS`, `PrefixSuffix-`, `AnchorURL`, `SubDomains`). O modelo **não visita URLs nem analisa websites em tempo real**.

## Convenção de classes

Segue a convenção dos módulos de Malware e Ransomware (1 = ameaça).

No dataset original a coluna `class` usa `-1 = phishing` e `1 = legítimo`. No pipeline final isto é convertido para `1 = Phishing` e `0 = Legítimo`.

As features usam os valores `-1`, `0` e `1`. Em geral, `-1` indica um sinal típico de phishing, `0` um sinal suspeito/neutro e `1` um sinal típico de website legítimo.

## Modelo utilizado

Algoritmo: XGBoost Classifier

Ficheiro do modelo: `models/phishing_xgboost.json`

Lista de features (ordem obrigatória): `models/phishing_features.json`

Métricas e parâmetros: `models/phishing_metrics.json`

Comparação de modelos: `models/phishing_cv_results.csv`

Hiperparâmetros finais: `n_estimators=300`, `max_depth=5`, `learning_rate=0.2`, `subsample=0.9`, `colsample_bytree=0.8`, `min_child_weight=5`, `reg_lambda=3`.

## Dados e divisão

- Dataset original: 11.054 registos, 32 colunas.
- Após preparação (remoção de `Index`, duplicados e perfis contraditórios): **5.721 registos**, 30 features + classe.
- Classes equilibradas: 51,7% phishing / 48,3% legítimo (não foi necessário tratamento de desequilíbrio).
- Sem valores em falta. Sem scaling: todas as features usam já a escala {-1, 0, 1}.
- Divisão estratificada **70% treino (4.004) / 15% validação (858) / 15% teste (859)**.

## Seleção do modelo

Foram comparados 8 algoritmos (Logistic Regression, k-NN, Naive Bayes, SVM, Decision Tree, Random Forest, Gradient Boosting e XGBoost) com métricas na validação e validação cruzada estratificada de 5 folds no treino.

| Modelo | Recall (val.) | F1 (val.) | Recall médio (CV) |
|---|---:|---:|---:|
| Logistic Regression | 91,20% | 91,09% | 93,52% |
| k-NN | 93,45% | 92,00% | 93,91% |
| Naive Bayes | 100,00% | 74,33% | 99,95% |
| SVM (RBF) | 92,78% | 93,52% | 94,39% |
| Decision Tree | 94,13% | 93,29% | 94,53% |
| Random Forest | 93,45% | 93,98% | 94,49% |
| Gradient Boosting | 94,58% | 94,58% | 95,79% |
| XGBoost (baseline) | 95,49% | 96,25% | 95,99% |
| **XGBoost (otimizado)** | **95,71%** | **96,15%** | **96,23%** |

O Naive Bayes tem Recall quase perfeito, mas F1 muito baixo (classifica quase tudo como phishing). Por isso só concorrem a modelo final os modelos com F1 de validação ≥ 0,90. O critério de escolha é o **maior Recall de phishing** na validação.

O tuning foi feito com `RandomizedSearchCV` (20 combinações, 5 folds, métrica Recall) apenas sobre o conjunto de treino.

Overfitting: nenhum modelo apresenta diferença treino–validação superior a 5% (XGBoost final: treino 98,78%, validação 96,04%, teste 95,93%).

## Resultados finais (conjunto de teste, 859 amostras)

| Métrica | Resultado |
|---|---:|
| Accuracy | 95,93% |
| Precision | 96,37% |
| Recall | 95,72% |
| F1-score | 96,05% |
| ROC-AUC | 0,9928 |
| PR-AUC | 0,9941 |

Matriz de confusão:

| | Previsto Legítimo | Previsto Phishing |
|---|---:|---:|
| Real Legítimo | 399 | 16 |
| Real Phishing | 19 | 425 |

Foram registados 19 falsos negativos (phishing não detetado) e 16 falsos positivos.

Features mais importantes: `PrefixSuffix-` (35,6%), `AnchorURL` (21,0%) e `HTTPS` (15,9%). Estas três concentram mais de 70% da importância total.

## Inferência

O modelo deve ser utilizado através do módulo `src/phishing_inference.py`, que:

1. recebe um dicionário com as 30 features;
2. valida que estão todas presentes, sem features extra, numéricas e com valores -1, 0 ou 1;
3. garante a ordem correta das features;
4. carrega o modelo XGBoost;
5. devolve a classe, a confiança, as duas probabilidades e as 5 features que mais contribuíram para a previsão (contribuições SHAP).

O agente `src/phishing_agent.py` encapsula este módulo e é chamado pelo orquestrador (`processar_pedido("phishing", amostra)`).

## Regras para utilização por agentes

Um agente que utilize este modelo deverá:

- utilizar o módulo de inferência para realizar previsões;
- verificar se as 30 features estão presentes e com valores válidos;
- não inventar valores para features em falta;
- não realizar uma classificação com dados inválidos (devolver erro);
- interpretar corretamente as classes 0 (Legítimo) e 1 (Phishing);
- apresentar a confiança como a da previsão individual, nunca como a precisão global do modelo;
- não afirmar que visitou ou analisou o website.

## Limitações

- O modelo foi treinado com um único dataset público; os resultados não garantem o mesmo desempenho em campanhas novas ou com técnicas de evasão.
- A remoção de duplicados e de perfis contraditórios reduziu o dataset de 11.054 para 5.721 registos.
- Depende de poucas features (três concentram >70% da importância).
- Para uso real seriam necessários dados recentes e independentes, e um passo de extração automática das features a partir do URL.
- Falsos negativos (19 no teste) significam phishing não detetado: o limiar de decisão pode ser reduzido para ganhar Recall, à custa de mais falsos positivos (ver `notebooks/model_evaluation.ipynb`).
