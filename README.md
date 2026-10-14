# IAAC-Projeto

Projeto desenvolvido no âmbito da unidade curricular de **Inteligência Artificial Aplicada à Cibersegurança**, com aplicação de técnicas de Machine Learning a três áreas de cibersegurança:

- **Malware** — José Maria Alves
- **Ransomware** — Tomás Matos
- **Phishing** — Diogo Carvalho

O projeto segue uma metodologia estruturada de Machine Learning, desde a compreensão do problema e dos dados até à preparação, construção, avaliação e otimização dos modelos.

---

## Objetivos

Os principais objetivos do projeto são:

- analisar datasets relacionados com ameaças de cibersegurança;
- realizar análise exploratória dos dados;
- identificar problemas de qualidade, redundâncias e relações entre features;
- preparar os dados para modelação;
- treinar e comparar modelos supervisionados;
- avaliar os modelos com métricas adequadas ao contexto;
- aplicar validação cruzada e otimização de hiperparâmetros;
- organizar o código de forma modular e reutilizável;
- garantir execução em ambiente local e em Google Colab.

---

## Temas

### Malware
Classificação binária de ficheiros executáveis em:

- `0` — Benigno
- `1` — Malicioso

Dataset utilizado:

**Malware Detection Dataset with New Malware Info**  
Autor no Kaggle: `aashishzzz`

Ficheiro principal:

```text
Malware_and_benign_recognition.csv
```

O dataset é importado diretamente do Kaggle através de `kagglehub`.

### Ransomware
Análise e classificação de amostras associadas a ransomware.

### Phishing
Classificação de websites como legítimos ou phishing com base nas respetivas características.

---

## Metodologia

O projeto inclui as seguintes fases:

1. **Business Understanding**
2. **Data Understanding**
3. **Exploratory Data Analysis (EDA)**
4. **Data Preparation**
5. **Model Building**
6. **Model Evaluation & Optimization**

Na fase de modelação foram definidos três algoritmos comuns ao grupo:

- Decision Tree
- Random Forest
- XGBoost

---

## Estrutura do projeto

```text
IAAC-Projeto/
│
├── Business_understanding/
│   ├── Business_Understanding_Malware.docx
│   ├── Data_Understanding_Malware.docx
│   ├── Machine Learning Canvas - Malware.docx
│   └── EAD_script.py
│
├── Data_Preparation/
│   ├── Data_Preparation_Malware.docx
│   └── data_preparation.py
│
├── dataset/
│   ├── benign.csv
│   ├── malware.csv
│   ├── Malware_and_benign_recognition.csv
│   └── Malware_prepared.csv
│
├── models/
│   └── model.py
│
├── notebooks/
│   ├── data_understanding.ipynb
│   ├── data_preparation.ipynb
│   └── model_building.ipynb
│
├── src/
│   ├── data_preparation_utils.py
│   ├── eda_utils.py
│   └── model_utils.py
│
├── references/
├── reports/
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Preparação dos dados — Malware

O dataset original contém:

```text
1156 registos
27 colunas
```

Durante a preparação foram removidas as colunas:

```text
File
SuspiciousSectionNames
SectionCount
```

Após a remoção de duplicados completos:

```text
1148 registos
24 colunas
```

A modelação utiliza:

```text
23 features
1 variável target: Malicious
```

Os dados são divididos de forma estratificada em:

```text
70% treino
15% validação
15% teste
```

Dimensões finais:

```text
Treino:     803 amostras
Validação:  172 amostras
Teste:      173 amostras
```

---

## Model Building — Malware

Foram treinados três modelos baseline:

```text
Decision Tree
Random Forest
XGBoost
```

No conjunto de validação, os três modelos apresentaram resultados idênticos:

| Métrica | Resultado |
|---|---:|
| Accuracy | 98,26% |
| Precision | 97,67% |
| Recall | 98,82% |
| F1-score | 98,25% |

Como os modelos ficaram empatados na validação, foi utilizada **Stratified 5-Fold Cross-Validation** sobre o conjunto de treino.

### Cross-validation

| Modelo | Recall médio | F1-score médio |
|---|---:|---:|
| Decision Tree | 98,99% | 98,99% |
| Random Forest | 99,75% | 99,12% |
| XGBoost | 99,75% | 99,37% |

O **XGBoost** foi selecionado por apresentar o maior F1-score médio entre os modelos com melhor Recall.

---

## Hyperparameter Tuning

Foi utilizado `GridSearchCV`, com otimização orientada para o **Recall**.

Os melhores parâmetros encontrados foram:

```python
{
    "learning_rate": 0.05,
    "max_depth": 2,
    "n_estimators": 100,
    "reg_alpha": 0,
    "reg_lambda": 1
}
```

O XGBoost otimizado apresentou os mesmos resultados do baseline no conjunto de validação.

Por esse motivo, foi mantido como modelo final:

```text
XGBoost Baseline
```

---

## Resultados finais — Malware

No conjunto de teste reservado, o modelo final apresentou:

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

Resultados relevantes:

- 85 amostras de malware corretamente detetadas;
- 0 falsos negativos;
- 4 falsos positivos;
- Recall de 100% no conjunto de teste.

Num contexto de deteção de malware, a ausência de falsos negativos é particularmente relevante, uma vez que nenhum ficheiro malicioso do conjunto de teste foi classificado como benigno.

---

## Overfitting

Comparação entre treino e validação:

| Modelo | Accuracy treino | Accuracy validação | Diferença |
|---|---:|---:|---:|
| Decision Tree | 100,00% | 98,26% | 1,74 p.p. |
| Random Forest | 100,00% | 98,26% | 1,74 p.p. |
| XGBoost Baseline | 100,00% | 98,26% | 1,74 p.p. |
| XGBoost Otimizado | 99,25% | 98,26% | 1,00 p.p. |

Os resultados não evidenciam underfitting nem overfitting severo.

---

## Principais features — Malware

Entre as features com maior importância nos modelos encontram-se:

```text
ImageBase
SizeOfHeaders
BaseOfData
Characteristics
DllCharacteristics
ImportedDLLs
SizeOfImage
MaxSectionEntropy
OverlaySize
```

A importância atribuída a cada feature varia consoante o algoritmo utilizado.

---

## Instalação

Recomenda-se a utilização de Python 3 e de um ambiente virtual.

### Clonar o repositório

```bash
git clone https://github.com/diogocarvalho2025056-crypto/IAAC-Projeto.git
cd IAAC-Projeto
```

### Instalar dependências

```bash
pip install -r requirements.txt
```

Nos notebooks poderá também ser necessário:

```python
%pip install -q kagglehub[pandas-datasets]
%pip install -q xgboost
%pip install -q matplotlib
```

---

## Execução

### Notebook

O fluxo completo de modelação de malware pode ser executado em:

```text
notebooks/model_building.ipynb
```

O notebook:

1. importa o dataset diretamente do Kaggle;
2. reaplica a preparação dos dados;
3. divide os dados em treino, validação e teste;
4. treina os três modelos;
5. avalia os modelos;
6. realiza cross-validation;
7. seleciona o melhor modelo;
8. executa Hyperparameter Tuning;
9. compara baseline e versão otimizada;
10. realiza a avaliação final;
11. calcula ROC-AUC;
12. analisa possíveis sinais de overfitting.

### Script

Também pode ser utilizado o script:

```text
models/model.py
```

A lógica reutilizável dos modelos encontra-se em:

```text
src/model_utils.py
```

---

## Google Colab

Os notebooks foram preparados para funcionar também no Google Colab.

Quando executados em Colab, o repositório pode ser clonado automaticamente e o dataset é obtido diretamente através do Kaggle.

---

## Tecnologias utilizadas

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Matplotlib
- KaggleHub
- Jupyter Notebook
- Google Colab
- Git
- GitHub

---

## Métricas de avaliação

Foram utilizadas:

- Accuracy
- Precision
- Recall
- F1-score
- Matriz de Confusão
- ROC-AUC
- Cross-Validation

Neste projeto, o **Recall da classe maliciosa** recebe particular atenção, devido ao impacto dos falsos negativos.

---

## Limitações

Os resultados obtidos são específicos dos datasets utilizados.

Um desempenho elevado nestes dados não significa que os modelos consigam detetar todas as variantes de malware, ransomware ou phishing existentes ou futuras.

A avaliação com datasets externos e amostras mais recentes poderá ser considerada em fases posteriores do projeto.

---

## Autores

Projeto desenvolvido por:

- **José Maria Alves** — Malware
- **Tomás Matos** — Ransomware
- **Diogo Carvalho** — Phishing

Unidade Curricular: **Inteligência Artificial Aplicada à Cibersegurança**

CTeSP em Cibersegurança — ISTEC Porto
