# Data Understanding — PE Malware & Ransomware Detector

## 1. Dataset Overview
- **Dataset:** `data/raw/ransom.csv`
- **Área do problema:** Deteção de Malware e Ransomware através de Análise Estática (Headers PE) e Análise Dinâmica/Comportamental (Sandboxing).
- **Base metodológica:** Deteção de ficheiros executáveis maliciosos em ecossistemas Windows através de caraterísticas de Portable Executable (PE) e rastos de execução.
- **Número de amostras:** 21.752 observações.
- **Número de colunas:** 77 (`md5`, `sha1` + 72 features técnicas + `Class`, `Category`, `Family`).
- **Valores em falta (Missing Values):** 0
- **Linhas duplicadas:** 0
- **Tipos de dados originais:**
  - `float64` (18 colunas): métricas comportamentais (registo, processos, chamadas de rede, API e DLLs).
  - `object` (59 colunas): identificadores únicos (`md5`, `sha1`), variáveis estruturais de PE Headers (em formato hexadecimal `0x...` e listas de atributos/flags) e alvos de classificação (`Class`, `Category`, `Family`).

---

## 2. Objetivo do Projeto
O objetivo principal é desenvolver e comparar modelos de classificação capazes de identificar se um ficheiro executável (`.exe`) é **seguro (Benign)** ou **malicioso (Malware)**, com base nas suas propriedades estruturais (PE Headers) e comportamentais.

O problema é formulado como uma **classificação binária**:
- `1` → Malware
- `0` → Benign

Para a avaliação do modelo no contexto de cibersegurança, será dada especial prioridade à **minimização dos Falsos Negativos** (classificar um Malware/Ransomware como Benign), evitando depender exclusivamente de *Accuracy*.

---

## 3. Variável-Alvo (`Class`)

| Classe | Significado | Nº de amostras | Percentagem |
| :--- | :--- | ---: | ---: |
| `Benign` | Ficheiro legítimo / seguro (`0`) | 10.876 | 50,0% |
| `Malware` | Ficheiro malicioso (`1`) | 10.876 | 50,0% |

A distribuição da variável-alvo é **perfeitamente equilibrada** (50/50), o que elimina a necessidade de aplicar técnicas de reamostragem ou balanceamento (como SMOTE ou undersampling).

Métricas principais consideradas para avaliação:
- **Recall da classe Malware:** Mede a proporção de ameaças efetivamente detetadas.
- **Precision:** Mede a exatidão das alertas geradas (evitando falsos alarmes no SOC).
- **F1-Score:** Balanço harmónico entre Precision e Recall.
- **ROC-AUC:** Capacidade de discriminação global do modelo.
- **Accuracy:** Métrica complementar.

---

## 4. Características do Dataset
O dataset contém 74 atributos preditivos divididos em duas categorias principais:

### 4.1. Análise Dinâmica (Métricas Comportamentais)
Variáveis numéricas que registam as ações do ficheiro durante a execução em ambiente de *Sandbox*:
- **Ações no Registo:** `registry_read`, `registry_write`, `registry_delete`, `registry_total`.
- **Atividade de Rede:** `network_dns`, `network_http`, `network_connections`, `network_threats`.
- **Processos e Ficheiros:** `total_procsses`, `processes_malicious`, `processes_suspicious`, `processes_monitored`, `files_malicious`, `files_suspicious`, `files_text`, `files_unknown`.
- **Interações de Sistema:** `dlls_calls`, `apis`.

### 4.2. Análise Estática (Estrutura do Header PE)
Variáveis estruturais do ficheiro Windows PE (representadas maioritariamente em hexadecimal):
- **Campos de Header:** `EntryPoint`, `ImageBase`, `SizeOfCode`, `SizeOfImage`, `SectionAlignment`, `FileAlignment`, `OperatingSystemVersion`, `Checksum`, `Subsystem`, etc.
- **Secções Técnicas:** Tamanhos e endereços virtuais das secções `.text` (código executável) e `.rdata` (dados de leitura).
- **Atributos de Compilação:** Listas de flags em `DllCharacteristics`, `text_Characteristics` e `rdata_Characteristics`.

### 4.3. Correlação de Pearson com a Variável-Alvo
Entre as features numéricas com maior correlação linear de Pearson com o target (`Malware = 1`):

| Feature | Correlação de Pearson | Categoria |
| :--- | ---: | :--- |
| `total_procsses` | +0,206 | Comportamental (Processos) |
| `files_text` | +0,186 | Comportamental (Ficheiros) |
| `files_malicious` | +0,182 | Comportamental (Ficheiros) |
| `files_suspicious` | +0,180 | Comportamental (Ficheiros) |
| `processes_monitored` | +0,133 | Comportamental (Processos) |
| `rdata_PointerToRawData` | -0,133 | Estática (PE Header) |
| `text_SizeOfRawData` | -0,129 | Estática (PE Header) |
| `files_unknown` | +0,128 | Comportamental (Ficheiros) |
| `text_VirtualSize` | -0,118 | Estática (PE Header) |
| `processes_malicious` | +0,114 | Comportamental (Processos) |

*Nota:* As correlações lineares no dataset são moderadas ou baixas, demonstrando que **algoritmos não-lineares baseados em árvores (Decision Trees, Random Forest, XGBoost)** serão essenciais para capturar as interações complexas entre as features PE e métricas dinâmicas.

---

## 5. Qualidade dos Dados
A análise inicial revela elevada qualidade estrutural:
- **Zero valores em falta** (`NaN` / `null`).
- **Zero linhas duplicadas**.
- **Necessidade de Transformação Tecnológica:**
  1. **Remoção de Identificadores:** As colunas `md5` e `sha1` são hashes únicas de identificação e devem ser removidas antes da modelação para evitar *overfitting* e memorização.
  2. **Conversão de Hexadecimal:** Os campos de PE Headers codificados como cadeias de texto hexadecimais (ex.: `0x00011200`, `0x108ec`) exigem conversão explícita para valores inteiros/numéricos de base 10.
  3. **Extração de Listas de Flags:** Atributos como `DllCharacteristics` contêm listas de *flags* (ex.: `['IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE', ...]`). Será extraída a contagem destas *flags* ou aplicado *One-Hot Encoding*.
  4. **Features Constantes:** Detetou-se que atributos como `network_threats`, `PEType` e `magic_number` possuem variância nula ou quase nula no dataset e serão candidatas a remoção na fase de *Feature Selection*.

---

## 6. Análise Exploratória a Realizar (EDA)
A fase de EDA irá aprofundar os seguintes pontos:
- **Diferenciação Estática vs. Dinâmica:** Comparação visual do impacto de caraterísticas estruturais do PE em contraste com ações cometidas em tempo de execução.
- **Análise das Famílias de Malware:** Mapeamento secundário da variável `Family` (ex.: *WannaCry*, *Phobos*, *LockBit*, *RedLine*) para compreender os padrões comportamentais de diferentes categorias de ransomware.
- **Distribuição de Tamanhos de Secção:** Histogramas das secções `.text` e `.rdata` para identificar técnicas de *packing* e ofuscação comuns em malwares.
- **Feature Selection:** Aplicação de métricas de Importância de Atributos (*Tree-based Feature Importances* e *Permutation Importance*) para selecionar os preditores mais relevantes.

---

## 7. Data Leakage & Isolamento na Pipeline
Para garantir rigor metodológico segundo o **CRISP-ML**:
1. Os identificadores de hash (`md5`, `sha1`) e as variáveis sub-alvo (`Category`, `Family`) serão isoladas antes de qualquer processamento.
2. Todas as transformações numéricas (conversão hex, parsing de listas) e codificação de rótulos serão encapsuladas num transformador reutilizável (`RansomDataPipeline` em `src/features/build_features.py`).
3. O ajuste de qualquer pré-processamento será efetuado **exclusivamente no conjunto de treino** e aplicado sequencialmente ao conjunto de teste.

---

## 8. Considerações para Produção e Deteção de Malware
### 8.1. Evasão e Concept Drift
Atacantes e criadores de ransomware alteram frequentemente o seu código fonte, compiladores e técnicas de ofuscação (ex.: alteração do *EntryPoint*, *Packing*, encriptação de secções `.text`).
- O modelo treinado em dados históricos está sujeito a degradação (*Concept Drift*) quando confrontado com novas famílias de ransomware (*Zero-Day Attacks*).
- Em produção, o sistema exige **re-treino periódico** e integração com *Feeds de Threat Intelligence*.

### 8.2. Custo de Análise Dinâmica em Tempo Real
Métricas comportamentais (como `registry_read`, `processes_malicious`) dependem da execução prévia do ficheiro numa *Sandbox* isolada (o que introduz latência de minutos).
- **Viabilidade Operacional:** O pipeline deve ser capaz de realizar uma primeira triagem ultrarrápida apenas com as caraterísticas estáticas do PE Header antes de enviar amostras duvidosas para análise dinâmica completa.

---

## 9. Estratégia de Modelação
A estratégia seguirá uma gradação de complexidade incremental utilizando a biblioteca `scikit-learn`:

### Baseline
- **Logistic Regression:** Para estabelecer a fasquia mínima de desempenho linear.

### Modelos Avançados
- **Decision Tree Classifier:** Para avaliar o ganho de regras de decisão não-lineares.
- **Random Forest Classifier:** Modelo principal candidato para captura de interações complexas sem *overfitting*.
- **XGBoost / Gradient Boosting:** Para maximização do F1-score e Recall.

---

## 10. Estratégia de Avaliação
O modelo final será avaliado segundo o seguinte rigor técnico:
- **Matriz de Confusão:** Monitorização estrita dos Falsos Negativos (Ransomware classificado como Benign).
- **Recall da classe Malware:** Métrica prioritária do projeto.
- **F1-Score Global:** Avaliação do equilíbrio operacional.
- **Amostragem Stratified Split (80/20):** Para preservar o equilíbrio perfeito de classes nos conjuntos de treino e teste.

---

## 11. Próximos Passos
1. Executar a pipeline de pré-processamento (`RansomDataPipeline`) para converter os valores Hex e estruturar as 74 features numéricas.
2. Gerar o split treino/teste (80/20) estratificado.
3. Treinar os modelos baseline (`LogisticRegression`, `DecisionTree`, `RandomForest`).
4. Selecionar o melhor modelo preditivo e exportá-lo para a pasta `models/best_model_ransom.pkl`.
5. Integrar o modelo no **Sistema Multiagente Generativo** para consumo das previsões e geração automatizada de relatórios de incidentes.

---

## 12. Limitações
- **Natureza Estática do Dataset:** Os registos representam uma fotografia temporal de amostras de malware e binários legítimos.
- **Evasão por Packing/Encriptação:** Binários com compiladores customizados ou *packers* avançados podem ocultar os headers PE reais.
- **Inexistência de Causalidade Direta:** A correlação entre uma chamada de API e a classe Malware reflete um padrão estatístico da amostra, não garantindo comportamento malicioso em todas as circunstâncias.

---

## 13. Conclusão
A análise inicial ao dataset `ransom.csv` confirma a existência de **21.752 observações perfeitamente equilibradas** (50% Benign / 50% Malware) e **77 colunas**, sem valores em falta ou linhas duplicadas. 

Embora exija uma fase dedicada de engenharia de atributos para conversão de valores hexadecimais e extração de atributos PE, a riqueza combinada de dados estáticos de compilação e dados comportamentais de sandbox fornece uma base sólida para a construção de classificadores de alta precisão e a subsequente integração com o **Sistema Multiagente Generativo**.