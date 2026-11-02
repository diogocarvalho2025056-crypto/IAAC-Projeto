# IAAC-Projeto

Projeto desenvolvido no âmbito da unidade curricular de **Inteligência Artificial Aplicada à Cibersegurança**, aplicando Machine Learning e agentes de IA a três áreas de cibersegurança:

- **Malware** — José Maria Alves
- **Ransomware** — Tomás Matos
- **Phishing** — Diogo Carvalho

A gestão do projeto segue **SCRUM** e a implementação técnica segue **CRISP-ML**.

---

## Estado atual

- Malware — integrado e funcional
- Ransomware — integrado e funcional
- Phishing — integrado e funcional
- Orquestrador comum — concluído
- Agente generativo de relatórios — integrado
- Testes automáticos — **29/29 a passar**
- Interface principal — suporta os três tipos de análise

---

## Estrutura principal

```text
IAAC-Projeto/
├── Business_Understanding/
├── Business_understanding/
├── Data_Preparation/
├── data/
│   ├── raw/
│   │   └── ransom.csv
│   └── processed/
│       └── ransom_cleaned.csv
│
├── dataset/
│   ├── Malware_and_benign_recognition.csv
│   ├── Malware_prepared.csv
│   ├── phishing.csv
│   └── phishing_prepared.csv
│
├── models/
│   ├── modeling_malware.py
│   ├── modeling_ransomware.py
│   ├── modeling_phishing.py
│   │
│   ├── malware_xgboost.json
│   ├── malware_features.json
│   ├── malware_model.md
│   │
│   ├── ransomware_model.pkl
│   ├── ransomware_features.json
│   ├── ransomware_metrics.json
│   ├── ransomware_cv_results.csv
│   ├── ransomware_model.md
│   │
│   ├── phishing_xgboost.json
│   ├── phishing_features.json
│   ├── phishing_metrics.json
│   ├── phishing_cv_results.csv
│   └── phishing_model.md
│
├── notebooks/
│
├── src/
│   ├── malware_inference.py
│   ├── malware_agent.py
│   ├── ransomware_inference.py
│   ├── ransomware_agent.py
│   ├── phishing_inference.py
│   ├── phishing_agent.py
│   ├── report_agent.py
│   └── orchestrator.py
│
├── tests/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# Malware

## Dataset e preparação

Dataset utilizado: **Malware Detection Dataset with New Malware Info**.

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

Resultados de validação:

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

Foram avaliadas três estratégias:

1. GridSearchCV original
2. RandomizedSearchCV
3. GridSearchCV refinado

As três estratégias atingiram aproximadamente **99,75% de Recall médio em cross-validation**, mas não melhoraram as métricas de validação.

Foi mantido o **XGBoost Baseline**, por apresentar desempenho equivalente com menor complexidade.

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

O modelo detetou todas as amostras de Malware do conjunto de teste, não apresentando falsos negativos nesse conjunto.

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
- remoção de campos não utilizados diretamente pelo modelo;
- aproximadamente 165 features finais.

A divisão é:

```text
70% treino
15% validação
15% teste
```

A divisão é estratificada e agrupada por `md5`, reduzindo o risco de o mesmo ficheiro aparecer em conjuntos diferentes.

## Model Building

Foram utilizados vários classificadores, com:

- conjunto de validação;
- Stratified Group 5-Fold Cross-Validation;
- tuning de XGBoost;
- análise de overfitting;
- seleção do modelo com foco no Recall.

A métrica principal é o **Recall**, devido à importância de reduzir falsos negativos em contexto de cibersegurança.

## Resultados finais

No conjunto de teste, o XGBoost baseline apresentou aproximadamente:

| Métrica | Resultado |
|---|---:|
| Accuracy | 99,54% |
| Precision | 99,21% |
| Recall | 99,88% |
| F1-score | 99,54% |
| ROC-AUC | 0,9993 |

Foram observados:

```text
2 falsos negativos
13 falsos positivos
```

A feature `processes_malicious` apresenta elevada importância no modelo.

O modelo realiza classificação binária:

```text
0 = Benigno
1 = Ransomware/Malware
```

Não identifica diretamente a família específica de malware.

---

# Phishing

## Dataset e preparação

O dataset preparado encontra-se em:

```text
dataset/phishing_prepared.csv
```

Contém:

```text
5721 registos
30 features
1 variável alvo
```

No dataset original:

```text
-1 = Phishing
 1 = Legítimo
```

Na pipeline final de modelação, a convenção foi uniformizada para:

```text
0 = Legítimo
1 = Phishing
```

A divisão utilizada é:

```text
70% treino
15% validação
15% teste
```

## Model Building

Foram comparados oito classificadores:

- Logistic Regression
- k-NN
- Naive Bayes
- SVM
- Decision Tree
- Random Forest
- Gradient Boosting
- XGBoost

Foi utilizada:

- validação separada;
- 5-Fold Stratified Cross-Validation;
- análise de overfitting;
- RandomizedSearchCV para XGBoost;
- seleção com prioridade ao Recall de Phishing.

O XGBoost foi selecionado para integração no sistema multiagente.

## Resultados finais

No conjunto de teste reservado:

| Métrica | Resultado |
|---|---:|
| Accuracy | 96,39% |
| Precision Phishing | 96,83% |
| Recall Phishing | 96,17% |
| F1 Phishing | 96,50% |
| ROC-AUC Phishing | 0,9946 |

Matriz de confusão:

```text
                 Previsto
               Phishing  Legítimo

Real Phishing      427       17
Real Legítimo       14      401
```

As features com maior importância global incluem:

- HTTPS
- AnchorURL
- PrefixSuffix-
- ServerFormHandler
- AbnormalURL

O módulo de inferência também calcula features com maior contribuição local para cada previsão.

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

### Phishing

```text
models/phishing_xgboost.json
models/phishing_features.json
models/phishing_metrics.json
models/phishing_cv_results.csv
models/phishing_model.md
```

---

## Inferência

Cada domínio possui um módulo próprio de inferência:

```text
src/malware_inference.py
src/ransomware_inference.py
src/phishing_inference.py
```

Estes módulos são responsáveis por:

- carregar o modelo;
- validar os dados de entrada;
- preparar a amostra;
- executar a previsão;
- calcular probabilidades;
- devolver informação relevante para o agente especializado.

---

## Agentes especialistas

```text
src/malware_agent.py
src/ransomware_agent.py
src/phishing_agent.py
```

Cada agente encapsula o respetivo módulo de inferência e produz um resultado estruturado contendo, conforme o domínio:

- classificação;
- confiança da previsão;
- probabilidades;
- features com maior contribuição;
- mensagem técnica.

---

## Orquestrador

O ficheiro:

```text
src/orchestrator.py
```

é responsável por receber o tipo de análise solicitado e encaminhar o pedido para o agente correspondente.

Tipos suportados:

```text
malware
ransomware
phishing
```

Fluxo simplificado:

```text
Utilizador
    |
  main.py
    |
orchestrator.py
    |
    +------------------+
    |        |         |
 Malware  Ransomware  Phishing
 Agent      Agent      Agent
    |        |         |
 Modelo    Modelo     Modelo
    +--------+---------+
             |
      report_agent.py
             |
          Relatório
```

---

# Agente generativo de relatórios

O ficheiro:

```text
src/report_agent.py
```

transforma o resultado técnico dos classificadores num pequeno relatório em linguagem natural.

O modelo utilizado é:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

O LLM **não decide a classificação**.

A decisão é sempre produzida pelo modelo de Machine Learning correspondente.

O agente generativo apenas transforma o resultado técnico numa explicação textual.

## Validação da resposta do LLM

A saída do LLM é validada antes de ser apresentada ao utilizador.

Caso a resposta:

- não respeite o formato esperado;
- produza listas quando é pedido um parágrafo;
- apresente conteúdo incompleto;
- não cumpra determinadas regras de segurança ou consistência;

o sistema utiliza automaticamente um **relatório determinístico**.

Fluxo:

```text
Resultado do classificador
          |
          v
         LLM
          |
          v
  Validação do output
       /       \
    válido    inválido
      |          |
      v          v
 Relatório     Fallback
   LLM       determinístico
       \        /
        \      /
        Relatório final
```

Isto permite manter o componente generativo sem depender cegamente da resposta do LLM.

## Execução sem LLM

É possível desativar o carregamento do modelo generativo:

```powershell
$env:IAAC_SEM_LLM="1"
```

Nesse caso, todos os relatórios são produzidos através do fallback determinístico.

---

# Arquitetura atual

```text
                     Utilizador
                         |
                       main.py
                         |
                  orchestrator.py
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
   MalwareAgent   RansomwareAgent   PhishingAgent
          |              |              |
          v              v              v
 malware_inference  ransomware_    phishing_inference
       .py          inference.py          .py
          |              |              |
          v              v              v
      XGBoost        Modelo ML        XGBoost
          \              |              /
           \             |             /
            +------------+------------+
                         |
                  report_agent.py
                         |
                 Qwen2.5-1.5B
                         |
                validação do output
                         |
              relatório final / fallback
```

---

# Interface principal

A interface de demonstração é executada através de:

```text
main.py
```

Menu atual:

```text
======================================
SISTEMA MULTIAGENTE DE CIBERSEGURANÇA
======================================

1 - Malware
2 - Ransomware
3 - Phishing
0 - Sair
```

Cada opção permite selecionar uma amostra de teste e visualizar:

- classificação;
- confiança;
- probabilidades;
- principais contribuições, quando disponíveis;
- relatório em linguagem natural.

O módulo de Ransomware utiliza lazy loading, preparando as amostras apenas quando a respetiva opção é selecionada.

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

## Pipeline Phishing

```bash
python models/modeling_phishing.py
```

Modo rápido:

```bash
python models/modeling_phishing.py --quick
```

## Sistema multiagente

```bash
python main.py
```

---

# Testes

Para executar todos os testes:

```bash
python -m pytest -v
```

Estado atual:

```text
29 testes
29 passaram
0 falharam
```

Os testes abrangem:

- preparação e validação de dados;
- inferência;
- classificação;
- probabilidades;
- agentes especializados;
- orquestrador;
- tratamento de tipos não suportados;
- geração de relatórios;
- integração do módulo de Phishing;
- tratamento de amostras de Ransomware.

---

# Metodologia

## SCRUM

O projeto utiliza SCRUM para organização do trabalho do grupo, incluindo:

- distribuição de tarefas por domínio;
- acompanhamento de progresso;
- integração gradual dos componentes;
- validação conjunta.

## CRISP-ML

Cada dataset segue, de forma adaptada, as fases:

```text
Business Understanding
        |
Data Understanding
        |
Data Preparation
        |
Model Building
        |
Model Evaluation
        |
Deployment
```

---

# Próximos passos

- criar versão equivalente com CrewAI, n8n, OpenClaw ou ferramenta semelhante;
- criar `multiagent_system.ipynb`;
- consolidar notebooks para reutilização das funções Python;
- finalizar diagramas de arquitetura e casos de uso;
- integrar os diagramas na documentação;
- completar documentação técnica do código;
- avaliar eventual integração com Telegram;
- preparar apresentação individual dos componentes principais.

---

# Limitações

Os resultados são específicos dos datasets utilizados e devem ser validados com dados externos e recentes antes de qualquer utilização real.

O modelo de Malware não garante deteção de todas as variantes futuras.

O modelo de Ransomware realiza classificação binária entre benigno e malicioso, não identificando necessariamente a família específica.

O modelo de Phishing depende das features presentes no dataset utilizado e não substitui mecanismos reais de análise dinâmica ou inspeção direta de websites.

As probabilidades apresentadas correspondem a previsões dos modelos para cada amostra e não representam a precisão global do sistema.

O modelo generativo não participa na decisão de classificação e pode produzir respostas inadequadas. Por esse motivo, existe validação da saída e fallback determinístico.

---

# Autores

- **José Maria Alves** — Malware
- **Tomás Matos** — Ransomware
- **Diogo Carvalho** — Phishing

Unidade Curricular: **Inteligência Artificial Aplicada à Cibersegurança**

CTeSP em Cibersegurança — ISTEC Porto
