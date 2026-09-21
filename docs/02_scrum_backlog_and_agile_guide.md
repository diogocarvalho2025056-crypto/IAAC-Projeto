# Guia Operacional SCRUM, Product Backlog e Template de Sprints

---

## 1. Definição de Papéis na Equipa (SCRUM Roles)

* **Scrum Master:** Responsável por garantir a aplicação do processo CRISP-ML e agilização das cerimónias.
* **Product Owner / Lead Architect:** Responsável pela definição das métricas de negócio e validação dos modelos com o docente.
* **Developers / Data Engineers:** Elementos do grupo (ex.: Tomás Matos, Diogo Carvalho, José Maria), cada um responsável pela pipeline do seu dataset específico e desenvolvimento colaborativo dos módulos Python (`src/`).

---

## 2. Product Backlog (User Stories & Critérios de Aceitação)

### Epic 1: Preparações de Dados e Engenharia de Atributos (CRISP-ML Phase 2)
* **US01 - Parsing de Atributos Hexadecimais e PE Headers (` ransom.csv `)**
  * *Como:* Data Engineer.
  * *Quero:* Converter as colunas em formato hexadecimal (`0x...`) e listas de flags para valores numéricos inteiros.
  * *Para:* Permitir o treino de algoritmos de aprendizagem automática baseados no `scikit-learn`.
  * *Critérios de Aceitação:* Módulo `src/features/build_features.py` executa sem erros; dataset gerado em `data/processed/` tem 0 colunas do tipo `object` não processadas.

* **US02 - Isolamento de Data Leakage e Split Estratificado**
  * *Como:* Data Scientist.
  * *Quero:* Remover hashes (`md5`, `sha1`) e separar treino/teste com estratificação.
  * *Para:* Garantir avaliação não viesada do modelo com a mesma proporção de 50/50 em ambos os conjuntos.
  * *Critérios de Aceitação:* O split preserva a proporção exata de `Malware` e `Benign` nos conjuntos de treino (80%) e teste (20%).

### Epic 2: Treino e Modelação de Classificadores (CRISP-ML Phase 3)
* **US03 - Treino e Comparação de Classificadores Baseline e Avançados**
  * *Como:* Data Scientist.
  * *Quero:* Treinar `LogisticRegression`, `DecisionTree` e `RandomForest` no conjunto de dados.
  * *Para:* Identificar o modelo com maior $F_1\text{-score}$ e Recall da classe Malware.
  * *Critérios de Aceitação:* O modelo com melhor performance é guardado automaticamente no formato `.pkl` em `models/best_model_ransom.pkl`.

### Epic 3: Sistema Multiagente Generativo e Deployment (CRISP-ML Phase 4)
* **US04 - Integração de Agente Generativo de Segurança (Hugging Face / LLM)**
  * *Como:* Security Automation Engineer.
  * *Quero:* Criar um agente LLM (ex.: `google/flan-t5-base`) que receba a predição do classificador e elabore um relatório sumário de segurança.
  * *Para:* Automatizar a produção de relatórios executivos para o SOC.
  * *Critérios de Aceitação:* O script `src/agents/crew_system.py` lê a amostra, obtém a classificação do `RandomForest` e gera o texto descritivo.

* **US05 - Automação da Pipeline Principal (`main.py`)**
  * *Como:* Lead Developer.
  * *Quero:* Um ficheiro `main.py` executável de ponta a ponta.
  * *Para:* Permitir que todo o ciclo CRISP-ML e inferência do sistema multiagente seja corrido num único comando.
  * *Critérios de Aceitação:* A execução de `python main.py` completa a limpeza, transformação, treino e inferência do agente.

---

## 3. Estrutura dos Sprints

### Sprint 1 (Aulas 18/09 a 21/09): Business Understanding, Data Understanding e Feature Engineering
* **Objetivo:** Mapeamento do Machine Learning Canvas, exploração estatística e criação do pipeline de pré-processamento modular.
* **Atribuições:**
  * Tomás Matos: Módulo de pré-processamento de Hexadecimal e PE Headers (`src/features/build_features.py`).
  * Elemento 2: EDA univariada/bivariada e construção das matrizes de correlação de Pearson/Spearman.
  * Elemento 3: Mapeamento dos requisitos SCRUM, backlog e estruturação do repositório Git.

### Sprint 2: Treino de Classificadores e Sistema Multiagente
* **Objetivo:** Treinar modelos Scikit-Learn, exportar `.pkl` e implementar os agentes generativos.

### Sprint 3: Documentação, Diagramas e Defesa Oral
* **Objetivo:** Elaborar os relatórios e praticar a apresentação individual de 5 a 7 minutos.

---

## 4. Templates para Cerimónias SCRUM

### 4.1. Daily Scrum Meeting Template (Máx 15 min)
A cada reunião rápida, cada elemento responde às 3 perguntas:
1. **O que fiz desde a última aula/reunião?** (ex.: *Implementei o parsing de hexadecimais em `build_features.py`*).
2. **O que vou fazer até à próxima aula?** (ex.: *Criar a classe `ModelTrainer` no `train_model.py`*).
3. **Existe algum bloqueador?** (ex.: *Aviso de deprecation da Hugging Face no Windows*).

### 4.2. Sprint Review Template
* **Amostra Demonstrada:** Execução funcional do `python main.py` mostrando a limpeza, treino e output do LLM.
* **Feedback do PO/Professor:** Validação do formato das métricas de Recall e F1-score.

### 4.3. Sprint Retrospective Template
* **O que correu bem:** Automação modular em ficheiros `.py` reutilizáveis.
* **O que pode ser melhorado:** Fazer pull request com mais frequência para evitar conflitos de rebase no Git.
* **Plano de Ação:** Garantir que cada elemento trabalha estritamente na sua branch individual (ex.: `Tomas-Matos`) antes da fusão.