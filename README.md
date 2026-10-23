# IAAC-Projeto

Projeto desenvolvido no âmbito da unidade curricular de **Inteligência Artificial Aplicada à Cibersegurança**, aplicando Machine Learning e agentes de IA a três áreas de cibersegurança:

- **Malware** — José Maria Alves
- **Ransomware** — Tomás Matos
- **Phishing** — Diogo Carvalho

A gestão do projeto segue **SCRUM** e a implementação técnica segue **CRISP-ML**.

---

## Estado atual

- Malware — integrado
- Ransomware — integrado
- Phishing — pendente

---

## Estrutura principal

```text
IAAC-Projeto/
├── data/
│   ├── raw/ransom.csv
│   └── processed/
├── dataset/
│   ├── Malware_and_benign_recognition.csv
│   └── Malware_prepared.csv
├── models/
│   ├── modeling_malware.py
│   ├── modeling_ransomware.py
│   ├── malware_xgboost.json
│   ├── malware_features.json
│   ├── malware_model.md
│   ├── ransomware_model.pkl
│   ├── ransomware_features.json
│   ├── ransomware_metrics.json
│   ├── ransomware_cv_results.csv
│   └── ransomware_model.md
├── notebooks/
├── src/
│   ├── malware_inference.py
│   ├── malware_agent.py
│   ├── ransomware_inference.py
│   ├── ransomware_agent.py
│   ├── report_agent.py
│   └── orchestrator.py
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

---

# Malware

## Dataset e preparação

Dataset: **Malware Detection Dataset with New Malware Info**.

```text
Dataset original: 1156 registos, 27 colunas
Após preparação: 1148 registos, 24 colunas
Features: 23
Target: Malicious
```

Divisão estratificada:

```text
70% treino
15% validação
15% teste
```

## Model Building

Foram comparados:

- Decision Tree
- Random Forest
- XGBoost

Validação:

| Métrica | Resultado |
|---|---:|
| Accuracy | 98,26% |
| Precision | 97,67% |
| Recall | 98,82% |
| F1-score | 98,25% |

Cross-validation:

| Modelo | Recall médio | F1-score médio |
|---|---:|---:|
| Decision Tree | 98,99% | 98,99% |
| Random Forest | 99,75% | 99,12% |
| XGBoost | 99,75% | 99,37% |

O XGBoost foi selecionado como melhor baseline.

## Hyperparameter Tuning

Foram testados:

1. GridSearchCV original
2. RandomizedSearchCV
3. GridSearchCV refinado

As três estratégias atingiram aproximadamente 99,75% de Recall médio em cross-validation e não melhoraram as métricas de validação. Foi mantido o **XGBoost Baseline**.

## Resultados finais

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

---

# Ransomware

## Dataset e preparação

O dataset principal encontra-se em:

```text
data/raw/ransom.csv
```

Contém aproximadamente:

```text
21 752 registos
13 903 ficheiros únicos (md5)
```

O pré-processamento inclui:

- conversão de valores hexadecimais e decimais;
- transformação de listas em flags binárias;
- codificação de variáveis categóricas;
- aproximadamente 165 features finais.

A divisão é 70/15/15, estratificada e agrupada por `md5`.

## Model Building

Foram utilizados vários classificadores, com:

- conjunto de validação;
- Stratified Group 5-Fold Cross-Validation;
- GridSearchCV para XGBoost;
- análise de overfitting.

A métrica principal é o **Recall**.

## Resultados finais

No Test Set, o XGBoost baseline apresentou aproximadamente:

| Métrica | Resultado |
|---|---:|
| Accuracy | 99,54% |
| Precision | 99,21% |
| Recall | 99,88% |
| F1-score | 99,54% |
| ROC-AUC | 0,9993 |

Foram observados 2 falsos negativos e 13 falsos positivos.

A feature `processes_malicious` apresenta elevada importância no modelo.

---

# Deployment e sistema multiagente

## Modelos persistidos

### Malware

```text
models/malware_xgboost.json
models/malware_features.json
models/malware_model.md
```

### Ransomware

```text
models/ransomware_model.pkl
models/ransomware_features.json
models/ransomware_metrics.json
models/ransomware_model.md
```

## Inferência

```text
src/malware_inference.py
src/ransomware_inference.py
```

## Agentes

```text
src/malware_agent.py
src/ransomware_agent.py
src/report_agent.py
src/orchestrator.py
```

O LLM não decide a classificação. O classificador toma a decisão e o agente generativo apenas explica o resultado.

O `report_agent.py` utiliza:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

Se o LLM não estiver disponível, existe fallback para relatório determinístico.

Para forçar execução sem LLM:

```powershell
$env:IAAC_SEM_LLM="1"
```

## Arquitetura atual

```text
                    Utilizador
                        |
                      main.py
                        |
                  orchestrator.py
                    /       \
                   /         \
        Malware Agent      Ransomware Agent
             |                    |
        XGBoost Malware      Modelo Ransomware
                   \         /
                    \       /
                   report_agent.py
                        |
                 Qwen2.5-1.5B
                        |
                     Relatório
```

Phishing será integrado posteriormente.

---

# Execução

## Instalação

```bash
pip install -r requirements.txt
```

## Pipeline Malware

```bash
python models/modeling_malware.py
```

## Pipeline Ransomware

```bash
python models/modeling_ransomware.py
```

Modo rápido:

```bash
python models/modeling_ransomware.py --quick
```

## Sistema multiagente

```bash
python main.py
```

## Testes

```bash
pytest
```

---

# Próximos passos

- integrar Phishing;
- completar o orquestrador com os três agentes;
- criar `multiagent_system.ipynb`;
- testar Malware + Ransomware em conjunto;
- implementar versão com OpenClaw, CrewAI, n8n ou equivalente;
- avaliar integração com Telegram;
- consolidar diagramas e documentação final.

---

# Limitações

Os resultados são específicos dos datasets utilizados e devem ser validados com dados externos e recentes antes de qualquer utilização real.

O modelo de Malware não garante deteção de todas as variantes futuras.

O modelo de Ransomware classifica benigno/malicioso, não identificando necessariamente a família específica.

---

# Autores

- **José Maria Alves** — Malware
- **Tomás Matos** — Ransomware
- **Diogo Carvalho** — Phishing

Unidade Curricular: **Inteligência Artificial Aplicada à Cibersegurança**

CTeSP em Cibersegurança — ISTEC Porto
