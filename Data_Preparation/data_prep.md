### 1. Enquadramento e Objetivo

A fase de **Data Preparation** tem como objetivo transformar o conjunto de dados analisado na fase de _Data Understanding_ num conjunto estruturado, limpo e adequado ao treino e à avaliação de modelos de Machine Learning. As decisões tomadas nesta etapa resultam diretamente das conclusões obtidas na análise exploratória dos dados (EDA).

O dataset de partida é o ficheiro `ransom.csv`, contendo **21.752 registos e 77 colunas**. Cada registo representa um ficheiro executável Windows (PE - _Portable Executable_), e a variável de interesse principal é a coluna `Class`, que identifica o tipo de ficheiro: `Benign` para ficheiros legítimos e `Malware` para executáveis maliciosos.

Nesta fase foram realizadas tarefas de:

- Remoção de identificadores não preditivos e sub-classes.
- Conversão de valores em notação hexadecimal para representações numéricas.
- Codificação de caraterísticas categóricas e extração de métricas de _flags_.
- Verificação de qualidade, valores em falta e tratamento de duplicados.
- Separação entre variáveis de entrada e _target_.
- Divisão estratificada (_train-validation-test split_).
- Avaliação de _scaling_, _feature selection_, _feature engineering_ e balanceamento de classes.

---

### 2. Remoção de Variáveis Não Preditivas e Sub-Target

A EDA identificou quatro colunas que não devem permanecer como caraterísticas preditivas do modelo de classificação binária:

| Coluna     | Decisão  | Justificação                                                                                                       |
| :--------- | :------- | :----------------------------------------------------------------------------------------------------------------- |
| `md5`      | Removida | Hash MD5 do ficheiro. Identificador único que não representa uma propriedade estrutural do executável.             |
| `sha1`     | Removida | Hash SHA-1 do ficheiro. Identificador único que causaria _overfitting_ se mantido no conjunto.                     |
| `Category` | Removida | Rotulagem secundária (ex.: _Ransomware_, _RAT_, _Stealer_, _Trojan_). Não faz parte das caraterísticas da amostra. |
| `Family`   | Removida | Nome da família específica do malware (ex.: _WannaCry_, _LockBit_, _Phobos_). Variável de sub-classe.              |

Após esta remoção inicial, o dataset manteve os 21.752 registos e passou de 77 para 73 colunas (72 _features_ de entrada + a variável-alvo `Class`).

---

### 3. Tratamento e Formatação de Atributos PE

Ao contrário de datasets puramente numéricos, o cabeçalho PE de ficheiros executáveis contém atributos codificados em diferentes formatos que exigem pré-processamento específico:

1. **Atributos em Notação Hexadecimal:**
   - Atributos como `EntryPoint`, `SizeOfCode`, `ImageBase`, `AddressOfEntryPoint`, `text_VirtualAddress`, entre outros, apresentam-se representados em hexadecimal (ex.: `0x108ec`, `0x00011200`).
   - Foi implementada uma função de parsing para converter estes valores para inteiros/floats decimais de forma a permitir a computação matemática pelos algoritmos.

2. **Atributos de Lista de Flags (_Characteristics_):**
   - As colunas `DllCharacteristics`, `text_Characteristics` e `rdata_Characteristics` contêm listas de definições (ex.: `['IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE', 'IMAGE_DLLCHARACTERISTICS_NX_COMPAT']`).
   - Foi realizada _Feature Engineering_ para extrair o número total de _flags_ ativas em cada secção (`*_count`), transformando listas textuais em indicadores numéricos quantitativos.

3. **Atributos Categóricos em Texto:**
   - Atributos categóricos estruturais (`file_extension`, `PEType`, `MachineType`, `magic_number`, `Subsystem`) foram transformados utilizando _Label Encoding_, atribuindo um identificador inteiro único a cada categoria.

---

### 4. Verificação de Qualidade e Duplicados

Foi efetuada a verificação da integridade do dataset após as transformações de formato e a remoção dos identificadores unívocos (`md5`, `sha1`):

| Verificação                                    | Resultado                                                         |
| :--------------------------------------------- | :---------------------------------------------------------------- |
| **Valores em falta (Missing Values)**          | 0 (Não foi necessária imputação)                                  |
| **Dimensão após pré-processamento**            | 21.752 registos × 73 colunas                                      |
| **Duplicados completos pós-remoção de Hashes** | Identificados e tratados para evitar contaminação entre conjuntos |
| **Perfis com rótulos contraditórios**          | 0 (Nenhuma combinação de _features_ idêntica com classes opostas) |

---

### 5. Separação entre Features e Target

O conjunto de dados preparado foi separado entre a matriz de caraterísticas de entrada ($X$) e o vetor do rótulo-alvo ($y$):

| Conjunto | Conteúdo                                               | Dimensão    |
| :------- | :----------------------------------------------------- | :---------- |
| **$X$**  | Caraterísticas estruturais PE e comportamento dinâmico | 21.752 × 72 |
| **$y$**  | Variável-alvo `Class` (`Malware` = 1, `Benign` = 0)    | 21.752      |

A variável $y$ foi codificada em formato binário (1 para `Malware` e 0 para `Benign`).

---

### 6. Divisão do Conjunto de Dados (Train / Validation / Test)

Para garantir uma avaliação imparcial dos modelos e permitir a afinação de hiperparâmetros sem _data leakage_, os dados foram divididos em **três subconjuntos independentes** utilizando amostragem estratificada (`stratify=y`) e reprodutível (`random_state=42`):

| Subconjunto                         | Proporção | N.º de Registos | Função no Projeto                                         |
| :---------------------------------- | :-------- | :-------------- | :-------------------------------------------------------- |
| **Treino ($X_{train}, y_{train}$)** | 70%       | 15.226          | Treino dos classificadores scikit-learn.                  |
| **Validação ($X_{val}, y_{val}$)**  | 15%       | 3.263           | Afinação de hiperparâmetros e validação de _overfitting_. |
| **Teste ($X_{test}, y_{test}$)**    | 15%       | 3.263           | Avaliação final e simulação do ambiente de produção.      |

---

### 7. Preservação do Balanceamento de Classes

Devido à utilização de amostragem estratificada (`stratify=y`), a proporção exata entre amostras benignas e maliciosas foi preservada ao longo de todas as fases da pipeline:

| Conjunto                  | Classe Benign (0) | Classe Malware (1) |
| :------------------------ | :---------------- | :----------------- |
| **Dataset Original**      | 10.876 (50,00%)   | 10.876 (50,00%)    |
| **Conjunto de Treino**    | 7.613 (50,00%)    | 7.613 (50,00%)     |
| **Conjunto de Validação** | 1.631 (50,00%)    | 1.632 (50,00%)     |
| **Conjunto de Teste**     | 1.632 (50,00%)    | 1.631 (50,00%)     |

Como o dataset se apresenta **perfeitamente equilibrado** (50% / 50%), não foi necessária a aplicação de técnicas de _oversampling_ (ex.: SMOTE) ou _undersampling_.

---

### 8. Scaling e Normalização

O dataset integra caraterísticas com ordens de grandeza muito díspares:

- Valores reduzidos: métricas de chamadas de API ou contagem de DLLs (ex.: `dlls_calls`, `apis`).
- Valores elevados: offsets de memória e dimensões de secção (ex.: `ImageBase`, `SizeOfCode`).

Para garantir a compatibilidade com algoritmos sensíveis à escala das variáveis (como _Regressão Logística_ e _SVM_), foi aplicada a transformação **StandardScaler**.

> **Garantia Anti-Data Leakage:** O objeto `StandardScaler` foi ajustado (_fitted_) **exclusivamente com os dados de treino ($X_{train}$)**. As transformações subsequentes nos conjuntos de validação ($X_{val}$) e teste ($X_{test}$) utilizaram apenas a média e o desvio-padrão calculados no treino.

As versões originais não escaladas das _features_ foram igualmente mantidas para alimentar algoritmos baseados em árvores de decisão (_Decision Tree_, _Random Forest_, _XGBoost_), que são invariantes a transformações de escala.

---

### 9. Resumo do Resultado da Data Preparation

| Etapa                                    | Resultado / Dimensão                                                         |
| :--------------------------------------- | :--------------------------------------------------------------------------- |
| **Dataset Inicial**                      | 21.752 registos × 77 colunas                                                 |
| **Após remoção de Hashes e Sub-targets** | 21.752 registos × 73 colunas                                                 |
| **Features ($X$) / Target ($y$)**        | 72 caraterísticas / 1 alvo binário (`Class`)                                 |
| **Divisão - Conjunto de Treino**         | 15.226 registos (70%)                                                        |
| **Divisão - Conjunto de Validação**      | 3.263 registos (15%)                                                         |
| **Divisão - Conjunto de Teste**          | 3.263 registos (15%)                                                         |
| **Valores em falta / Imputação**         | 0 valores em falta                                                           |
| **StandardScaler**                       | Aplicado e preservado separadamente para $X_{train}$, $X_{val}$ e $X_{test}$ |
| **Balanceamento de Classes**             | Perfeitamente equilibrado (50% Benign / 50% Malware)                         |

---

### 10. Conclusão

A fase de **Data Preparation** transformou com sucesso os dados brutos do executável `ransom.csv` num pipeline estruturado e pronto a ser utilizado na fase de treino de modelos do CRISP-ML. Foram eliminadas variáveis irrelevantes, efetuada a conversão correta de atributos em notação hexadecimal e tratadas caraterísticas categóricas e em lista.

A divisão em três subconjuntos estratificados (Treino, Validação e Teste) assegura que a comparação de modelos scikit-learn e a subsequente integração com o **Sistema Multiagente (LLM)** ocorram sem qualquer risco de _data leakage_, garantindo rigor científico na avaliação do projeto.
