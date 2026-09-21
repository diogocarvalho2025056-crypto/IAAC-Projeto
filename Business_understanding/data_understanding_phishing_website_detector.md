# Data Understanding — Phishing Website Detector

## 1. Dataset Overview

- **Dataset:** `data/raw/phishing.csv`
- **Fonte:** [Kaggle — Phishing Website Detector](https://www.kaggle.com/datasets/eswarchandt/phishing-website-detector)
- **Base metodológica:** Mohammad, Thabtah & McCluskey (2015)
- **Número de amostras:** 11.054
- **Número de colunas:** 32 (`Index` + 30 features + `class`)
- **Valores em falta:** 0
- **Linhas duplicadas:** 0
- **Tipo de dados:** todas as colunas são `int64`
- **Codificação:** features codificadas em `-1 / 0 / 1`

---

## 2. Objetivo do Projeto

O objetivo é desenvolver um modelo de classificação capaz de distinguir websites legítimos de websites de phishing utilizando as características disponíveis no dataset.

O problema é formulado como uma **classificação binária**:

- `1` → website legítimo
- `-1` → website de phishing

Para a avaliação do modelo, será dada especial atenção à capacidade de identificar corretamente websites de phishing, evitando depender exclusivamente de accuracy.

---

## 3. Variável-Alvo

| Classe | Significado | Nº de amostras | Percentagem |
|---|---|---:|---:|
| `1` | Website legítimo | 6.157 | 55,7% |
| `-1` | Website de phishing | 4.897 | 44,3% |

A distribuição das classes apresenta um desequilíbrio moderado. Não será aplicado balanceamento automaticamente na primeira iteração. A decisão será baseada no comportamento dos modelos e nas métricas obtidas.

Para este problema, serão consideradas principalmente:

- Recall da classe phishing
- Precision
- F1-score
- ROC-AUC
- Accuracy como métrica complementar

---

## 4. Características do Dataset

O dataset contém 30 features relacionadas com características dos websites.

Entre as features com maior correlação de Pearson com a variável-alvo encontram-se:

| Feature | Correlação de Pearson |
|---|---:|
| `HTTPS` | 0,71 |
| `AnchorURL` | 0,69 |
| `PrefixSuffix-` | 0,35 |
| `WebsiteTraffic` | 0,35 |
| `SubDomains` | 0,30 |
| `RequestURL` | 0,25 |
| `LinksInScriptTags` | 0,25 |
| `DomainRegLen` | -0,23 |
| `ServerFormHandler` | 0,22 |
| `GoogleIndex` | 0,13 |

Features com correlação linear muito baixa incluem:

- `Favicon`
- `UsingPopupWindow`
- `IframeRedirection`
- `StatusBarCust`

Estas features serão consideradas candidatas a análise de feature selection, mas não serão removidas apenas com base na correlação de Pearson.

Uma baixa correlação linear não significa necessariamente que uma feature não tenha capacidade preditiva para modelos não lineares.

---

## 5. Qualidade dos Dados

A análise inicial indica:

- Não existem valores em falta.
- Não existem linhas duplicadas.
- As features já se encontram codificadas numericamente.
- Não é necessário aplicar encoding adicional nesta fase.
- As features são discretas e assumem valores `-1`, `0` ou `1`.

Antes do treino dos modelos será ainda importante verificar:

- Features constantes ou quase constantes.
- Distribuição dos valores de cada feature.
- Possíveis inconsistências nos valores.
- Relações entre features.
- Possível data leakage.

---

## 6. Análise Exploratória a Realizar

A fase de EDA deverá complementar este Data Understanding com:

### Distribuição da variável-alvo

Visualização da proporção entre websites legítimos e phishing.

### Distribuição das features

Análise da frequência dos valores `-1`, `0` e `1` para cada feature.

### Matriz de correlação

Avaliação das relações entre as diferentes features e a variável-alvo.

### Relações entre features

Identificação de features potencialmente redundantes ou altamente relacionadas.

### Feature selection

A seleção de features não será baseada exclusivamente em correlação. Serão posteriormente considerados métodos como:

- importância das features;
- Recursive Feature Elimination;
- importância baseada em árvores;
- análise de desempenho com diferentes subconjuntos de features.

---

## 7. Data Leakage

Antes do treino será necessário verificar se alguma feature contém informação que, na utilização real do modelo, apenas estaria disponível depois do momento em que a previsão deveria ser realizada.

Além disso, qualquer transformação baseada nos dados deverá ser ajustada exclusivamente no conjunto de treino e posteriormente aplicada aos restantes conjuntos.

Isto é particularmente importante para:

- feature selection;
- normalização/transformações;
- cálculo de estatísticas;
- seleção de hiperparâmetros.

---

## 8. Considerações para Produção

### 8.1 Concept Drift

O dataset é estático e representa características de websites de phishing recolhidas num determinado contexto temporal.

As técnicas utilizadas por atacantes podem mudar ao longo do tempo. Consequentemente, um modelo treinado neste dataset pode perder desempenho quando aplicado a dados futuros.

Num ambiente de produção deverá existir:

- monitorização do desempenho;
- acompanhamento da distribuição das features;
- deteção de concept drift;
- retreino periódico quando necessário.

### 8.2 Dependências externas

Algumas features podem depender de informação ou serviços externos, nomeadamente:

- `WebsiteTraffic`
- `PageRank`
- `GoogleIndex`
- `DomainRegLen`

Antes de uma implementação real será necessário verificar se estas informações continuam disponíveis, qual a sua latência e se podem ser obtidas de forma consistente.

### 8.3 Disponibilidade das features

Uma feature pode apresentar elevado poder preditivo no dataset, mas ser pouco adequada para produção se:

- for demasiado cara de calcular;
- depender de serviços instáveis;
- tiver elevada latência;
- não estiver disponível no momento da previsão.

Por isso, a seleção final das features deverá considerar não apenas o desempenho preditivo, mas também a sua viabilidade operacional.

---

## 9. Estratégia de Modelação

A estratégia inicial será comparar modelos de complexidade crescente.

### Baseline

**Logistic Regression**

Servirá como referência para determinar se modelos mais complexos apresentam ganhos significativos.

### Modelos adicionais

- Random Forest
- XGBoost

Dependendo dos resultados, poderão posteriormente ser testados outros algoritmos.

A comparação deverá utilizar o mesmo conjunto de treino/teste e, quando apropriado, validação cruzada.

---

## 10. Estratégia de Avaliação

As principais métricas serão:

### Recall — classe phishing

Mede a proporção de websites de phishing que foram corretamente identificados.

Esta métrica é particularmente relevante porque um falso negativo corresponde a um website de phishing classificado como legítimo.

### Precision

Mede a proporção das previsões de phishing que são realmente phishing.

### F1-score

Combina precision e recall numa única métrica.

### ROC-AUC

Permite avaliar a capacidade discriminativa do modelo considerando diferentes thresholds.

### Accuracy

Será utilizada como métrica complementar, mas não como único critério de avaliação.

Além das métricas agregadas, será analisada a **matriz de confusão** para compreender os tipos de erro cometidos pelos modelos.

---

## 11. Próximos Passos

1. Realizar análise exploratória dos dados.
2. Verificar a distribuição das 30 features.
3. Analisar correlações e possíveis redundâncias.
4. Verificar possíveis problemas de data leakage.
5. Criar um split treino/teste.
6. Criar um baseline com Logistic Regression.
7. Treinar Random Forest.
8. Treinar XGBoost.
9. Comparar os modelos através das métricas definidas.
10. Analisar a matriz de confusão.
11. Avaliar a importância das features.
12. Testar feature selection.
13. Avaliar a robustez dos resultados através de validação cruzada.
14. Considerar limitações relacionadas com concept drift e disponibilidade das features.

---

## 12. Limitações

Este dataset apresenta algumas limitações que devem ser consideradas na interpretação dos resultados:

- É um dataset estático.
- Os resultados obtidos no dataset não garantem o mesmo desempenho em websites futuros.
- Algumas features podem depender de informação externa.
- A correlação entre uma feature e o target não representa causalidade.
- O desempenho de um modelo neste dataset não é suficiente, por si só, para validar uma implementação de segurança em produção.

Consequentemente, os resultados devem ser interpretados como uma avaliação experimental do problema de classificação e não como uma garantia de deteção de phishing em ambiente real.

---

## 13. Conclusão

A análise inicial mostra que o dataset possui 11.054 observações, 30 features e uma variável-alvo binária, sem valores em falta ou duplicados.

A distribuição das classes é relativamente equilibrada, com 55,7% de websites legítimos e 44,3% de websites de phishing.

As correlações exploratórias indicam que algumas features, como `HTTPS` e `AnchorURL`, apresentam uma relação linear mais forte com a variável-alvo. No entanto, a seleção definitiva das features será realizada através de métodos específicos de feature selection e da avaliação do desempenho dos modelos.

A próxima fase será a realização da EDA e preparação dos dados, seguida da construção de um baseline e da comparação entre diferentes modelos de classificação.
