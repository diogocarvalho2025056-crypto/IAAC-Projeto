# IAAC-Projeto

Projeto desenvolvido no âmbito da unidade curricular de **Inteligência Artificial Aplicada à Cibersegurança**, aplicando Machine Learning e agentes de IA a três áreas de cibersegurança:

- **Malware** — José Maria Alves
- **Ransomware** — Tomás Matos
- **Phishing** — Diogo Carvalho

A gestão do projeto segue **SCRUM** e a implementação técnica segue **CRISP-ML**, desde a compreensão do problema até à fase de deployment.

---

## Objetivos

Os principais objetivos do projeto são:

- analisar datasets relacionados com ameaças de cibersegurança;
- realizar Business Understanding, Data Understanding e EDA;
- preparar os dados de forma reprodutível;
- treinar e comparar vários modelos de classificação;
- avaliar os modelos com métricas adequadas ao contexto;
- aplicar cross-validation e otimização de hiperparâmetros;
- selecionar e persistir o melhor modelo de cada tema;
- criar módulos de inferência reutilizáveis;
- integrar classificadores com agentes especializados;
- utilizar um agente generativo para produzir relatórios;
- preparar uma arquitetura multiagente extensível a OpenClaw, CrewAI, n8n e interfaces como Telegram.

---

## Temas

### Malware

Classificação binária de ficheiros executáveis em:

- `0` — Benigno
- `1` — Malware

Dataset utilizado:

**Malware Detection Dataset with New Malware Info**  
Kaggle: `aashishzzz/malware-detection-dataset-with-new-malware-info`

Ficheiro principal:

```text
Malware_and_benign_recognition.csv
```

### Ransomware

Classificação de amostras associadas a ransomware.

### Phishing

Classificação de websites como legítimos ou phishing.

---

## Metodologia

O projeto segue as fases principais do CRISP-ML:

1. Business Understanding
2. Data Understanding
3. Exploratory Data Analysis
4. Data Preparation
5. Model Building
6. Model Evaluation & Optimization
7. Deployment
8. Integração com agentes

Na fase de modelação foram definidos três algoritmos comuns ao grupo:

- Decision Tree
- Random Forest
- XGBoost

---

## Estrutura atual do projeto

```text
IAAC-Projeto/
│
├── Business_understanding/
│
├── Data_Preparation/
│
├── dataset/
│   ├── Malware_and_benign_recognition.csv
│   └── Malware_prepared.csv
│
├── models/
│   ├── malware_xgboost.json
│   ├── malware_features.json
│   └── malware_model.md
│
├── notebooks/
│   ├── data_understanding.ipynb
│   ├── data_preparation.ipynb
│   ├── model_building.ipynb
│   └── deployment_malware.ipynb
│
├── src/
│   ├── data_preparation_utils.py
│   ├── eda_utils.py
│   ├── model_utils.py
│   ├── malware_inference.py
│   ├── malware_agent.py
│   ├── report_agent.py
│   └── orchestrator.py
│
├── tests/
│   ├── test_malware_inference.py
│   ├── test_malware_agent.py
│   ├── test_report_agent.py
│   └── test_orchestrator.py
│
├── main.py
├── requirements.txt
├── LICENSE
└── README.md
```

---

# Malware

## Data Preparation

O dataset original contém:

```text
1156 registos
27 colunas
```

Foram removidas:

```text
File
SuspiciousSectionNames
SectionCount
```

Depois da remoção de duplicados:

```text
1148 registos
24 colunas
```

A modelação utiliza:

```text
23 features
1 target: Malicious
```

Divisão estratificada:

```text
70% treino
15% validação
15% teste
```

Dimensões:

```text
Treino:     803
Validação:  172
Teste:      173
```

---

## Model Building

Foram treinados:

- Decision Tree
- Random Forest
- XGBoost

No conjunto de validação, os três modelos apresentaram:

| Métrica | Resultado |
|---|---:|
| Accuracy | 98,26% |
| Precision | 97,67% |
| Recall | 98,82% |
| F1-score | 98,25% |

Como os três modelos ficaram empatados, foi utilizada **Stratified 5-Fold Cross-Validation**.

### Cross-validation

| Modelo | Recall médio | F1-score médio |
|---|---:|---:|
| Decision Tree | 98,99% | 98,99% |
| Random Forest | 99,75% | 99,12% |
| XGBoost | 99,75% | 99,37% |

O **XGBoost** foi selecionado como melhor baseline.

---

## Hyperparameter Tuning

Foram testadas três estratégias:

1. GridSearchCV original
2. RandomizedSearchCV
3. GridSearchCV refinado

Todas atingiram o mesmo melhor Recall médio em cross-validation:

```text
99,7468%
```

Também apresentaram exatamente as mesmas métricas do baseline no conjunto de validação.

Por esse motivo, foi mantido:

```text
XGBoost Baseline
```

A decisão segue o princípio **Keep it simple**: se uma configuração mais complexa não melhora o desempenho, mantém-se a solução mais simples.

---

## Overfitting

| Modelo | Accuracy treino | Accuracy validação | Gap |
|---|---:|---:|---:|
| Decision Tree | 100,00% | 98,26% | 1,74 p.p. |
| Random Forest | 100,00% | 98,26% | 1,74 p.p. |
| XGBoost Baseline | 100,00% | 98,26% | 1,74 p.p. |
| GridSearch Original | 99,25% | 98,26% | 1,00 p.p. |
| RandomizedSearch | 98,88% | 98,26% | 0,62 p.p. |
| GridSearch Refinado | 98,63% | 98,26% | 0,37 p.p. |

As versões otimizadas reduziram o gap treino-validação, mas não melhoraram as métricas de validação.

---

## Resultados finais

No conjunto de teste reservado:

| Métrica | Resultado |
|---|---:|
| Accuracy | 97,69% |
| Precision | 95,51% |
| Recall | 100% |
| F1-score | 97,70% |
| ROC-AUC | 0,9981 |

Matriz de confusão:

```text
                 Previsto
               Benigno  Malware

Real Benigno      84       4
Real Malware       0      85
```

Resultados:

- 85 amostras de malware corretamente detetadas;
- 0 falsos negativos;
- 4 falsos positivos.

---

# Deployment — Malware

## Persistência do modelo

O modelo final é guardado em:

```text
models/malware_xgboost.json
```

A lista ordenada das 23 features é guardada em:

```text
models/malware_features.json
```

A ficha técnica do modelo encontra-se em:

```text
models/malware_model.md
```

---

## Inferência

O módulo:

```text
src/malware_inference.py
```

é responsável por:

- carregar o modelo persistido;
- carregar as features esperadas;
- validar novas amostras;
- garantir a ordem das features;
- executar a previsão;
- devolver classe, confiança e probabilidades.

O modelo não é treinado novamente durante a inferência.

---

## Validação de entradas

Antes da previsão são validados:

- tipo da entrada;
- features obrigatórias;
- features inesperadas;
- valores não numéricos;
- valores NaN.

Testes implementados:

| Teste | Comportamento |
|---|---|
| Amostra benigna válida | Classificação normal |
| Amostra malware válida | Classificação normal |
| Feature em falta | Erro controlado |
| Valor não numérico | Erro controlado |
| Feature extra | Erro controlado |
| NaN | Erro controlado |
| Entrada inválida | Erro controlado |

---

## Agente de Malware

O módulo:

```text
src/malware_agent.py
```

encapsula a inferência e transforma o resultado técnico numa resposta estruturada.

Responsabilidades:

```text
XGBoost
→ decide a classe

Malware Agent
→ organiza e apresenta o resultado
```

---

## Agente generativo

O módulo:

```text
src/report_agent.py
```

utiliza:

```text
Transformers / Hugging Face
Qwen2.5-1.5B-Instruct
```

O LLM recebe o resultado já produzido pelo classificador e gera um pequeno relatório em linguagem natural.

O agente generativo não decide a classificação.

Fluxo:

```text
XGBoost
   ↓
classificação + probabilidades
   ↓
Malware Agent
   ↓
Report Agent
   ↓
relatório
```

O prompt inclui regras para evitar que o modelo:

- altere a classificação;
- invente features;
- invente métricas;
- confunda confiança de uma previsão com Accuracy global;
- apresente a previsão como uma certeza absoluta.

---

## Orquestrador

O módulo:

```text
src/orchestrator.py
```

coordena o fluxo entre agentes.

Arquitetura atual:

```text
Utilizador
   ↓
main.py
   ↓
orchestrator.py
   ↓
malware_agent.py
   ↓
malware_inference.py
   ↓
XGBoost
   ↓
resultado técnico
   ↓
report_agent.py
   ↓
relatório
```

A arquitetura foi preparada para adicionar posteriormente:

```text
Ransomware Agent
Phishing Agent
```

---

## Interface de demonstração

O ficheiro:

```text
main.py
```

disponibiliza um menu de terminal:

```text
1 - Malware
2 - Ransomware
3 - Phishing
0 - Sair
```

Nesta fase, apenas Malware está totalmente integrado.

Para Malware é possível testar amostras benignas ou maliciosas e visualizar:

- classificação;
- confiança;
- probabilidade Benigno;
- probabilidade Malware;
- relatório gerado pelo agente.

---

## Notebooks

### Model Building

```text
notebooks/model_building.ipynb
```

Inclui:

- importação direta do Kaggle;
- Data Preparation;
- treino;
- validação;
- cross-validation;
- tuning;
- seleção final;
- teste reservado;
- ROC-AUC;
- gráficos;
- persistência do modelo.

### Deployment Malware

```text
notebooks/deployment_malware.ipynb
```

Inclui:

- carregamento do modelo persistido;
- inferência;
- testes de robustez;
- Malware Agent;
- agente generativo;
- orquestrador.

Mais tarde será criado um notebook global semelhante a:

```text
notebooks/multiagent_system.ipynb
```

para integrar os três temas.

---

## Instalação

```bash
git clone https://github.com/diogocarvalho2025056-crypto/IAAC-Projeto.git
cd IAAC-Projeto
pip install -r requirements.txt
```

Dependências principais desta fase:

```bash
pip install pandas scikit-learn xgboost matplotlib
pip install kagglehub[pandas-datasets]
pip install transformers torch accelerate
```

---

## Executar o sistema

Na raiz do projeto:

```bash
python main.py
```

No Windows, dependendo da instalação de Python:

```bash
py -3.14 main.py
```

---

## Tecnologias

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Matplotlib
- KaggleHub
- Jupyter Notebook
- Google Colab
- Transformers
- Hugging Face
- PyTorch
- Git
- GitHub

---

## Próximos passos

- integrar o modelo de Ransomware;
- integrar o modelo de Phishing;
- completar o orquestrador multiagente;
- criar `multiagent_system.ipynb`;
- implementar uma segunda versão com OpenClaw, CrewAI, n8n ou ferramenta equivalente;
- avaliar integração com Telegram;
- criar diagramas de arquitetura e caso de uso;
- consolidar a documentação final.

---

## Limitações

O modelo de Malware foi treinado e avaliado com o dataset selecionado para o projeto.

O desempenho obtido não garante o mesmo comportamento em:

- amostras externas;
- novas famílias de malware;
- variantes futuras;
- ambientes reais.

A avaliação com dados externos deverá ser considerada antes de uma utilização real.

---

## Autores

- **José Maria Alves** — Malware
- **Tomás Matos** — Ransomware
- **Diogo Carvalho** — Phishing

Unidade Curricular: **Inteligência Artificial Aplicada à Cibersegurança**

CTeSP em Cibersegurança — ISTEC Porto
