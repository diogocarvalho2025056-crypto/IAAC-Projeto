# Machine Learning Canvas: Deteção e Classificação de Ransomware

## 1. Value Proposition (Proposta de Valor)
Fornecer um sistema automático de deteção preventiva capaz de classificar ficheiros executáveis PE (Portable Executable) em milissegundos, distinguindo software benigno de malware/ransomware antes da execução de rotinas prejudiciais no sistema.

## 2. ML Task (Tarefa de Machine Learning)
- **Tipo:** Classificação Supervisionada Binária (`Class`: Benign vs Malware).
- **Algoritmo Escolhido:** XGBoost / Random Forest Classifier.

## 3. Data Collection & Features (Dados e Variáveis)
- **Dataset:** `ransom.csv` contendo 21.752 amostras.
- **Divisão de Dados:** 70% Treino (~15.226) / 15% Validação (~3.263) / 15% Teste (~3.263).
- **Atributos Estáticos:** Cabeçalho PE (`SizeOfCode`, `ImageBase`, `EntryPoint`, `DllCharacteristics`).
- **Atributos Dinâmicos:** Atividades no sistema (`registry_write`, `network_connections`, `apis`, `processes_malicious`).

## 4. Evaluation Metrics (Métricas de Avaliação)
- **Recall (Métrica Primária):** Maximizar a deteção de Ransomware para mitigar o risco de Falsos Negativos (um ransomware passar despercebido).
- **Precision & F1-Score (Métricas Secundárias):** Garantir que ficheiros benignos não sejam bloqueados incorretamente.
- **ROC-AUC Score:** Avaliar a capacidade de separação global do modelo.

## 5. Model Deployment & Usage (Utilização do Modelo)
- O modelo treinado e serializado (`xgboost_ransomware_model.pkl`) é carregado via pipeline Python.
- Pode ser integrado em agentes de EDR/Antivírus ou sistemas de análise em *Sandbox*.