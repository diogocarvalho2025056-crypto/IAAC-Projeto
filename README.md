# ProjetoIAAC: Sistema Inteligente de Deteção de Ransomware

> Um pipeline de Machine Learning combinado com um sistema multiagente (CrewAI / LLM) para a análise e classificação avançada de ransomware, focando-se no tratamento de dados binários, extração de características (PE Headers) e tomada de decisão automatizada.

---

## 🏗️ Estrutura do Projeto

A arquitetura do projeto segue as boas práticas de organização de código para ciência de dados:

```text
ProjetoIAAC/
├── data/
│   ├── raw/                # Dados brutos originais (ex: ransom.csv)
│   ├── interim/            # Dados intermédios após limpeza inicial
│   └── processed/          # Dados finais transformados prontos para modelação
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── make_dataset.py     # Scripts de ingestão, limpeza e tratamento inicial
│   ├── features/
│   │   ├── __init__.py
│   │   └── build_features.py   # Engenharia de características (Hexadecimais e PE Headers)
│   ├── models/
│   │   ├── __init__.py
│   │   └── train_model.py      # Treino e avaliação de modelos (RandomForest, etc.)
│   └── agents/
│       ├── __init__.py
│       └── crew_system.py      # Sistema Multiagente (Classificador + LLM)
├── models/                     # Armazenamento dos modelos treinados (.pkl)
├── notebooks/                  # Jupyter Notebooks para exploração e prototipagem
├── reports/figures/            # Diagramas de arquitetura, gráficos e casos de uso
├── requirements.txt            # Dependências do projeto
└── main.py                     # Script principal que orquestra todo o pipeline
```

---

## 🚀 Começar Rápido

### 1. Pré-requisitos
Certifica-te de que tens o **Python 3.8+** instalado no teu sistema.

### 2. Instalação
Clona o repositório e instala as dependências necessárias:

```bash
git clone <url-do-teu-repositorio>
cd ProjetoIAAC
pip install -r requirements.txt
```

### 3. Configuração de Dados
Coloca o teu ficheiro de dados original (`ransom.csv`) dentro da pasta `data/raw/`.

---

## ⚙️ Execução do Projeto

O projeto pode ser executado de forma unificada através do script principal:

```bash
python main.py
```

Em alternativa, podes executar os módulos individualmente conforme o fluxo de trabalho:
1. **Processamento de dados:** `python src/data/make_dataset.py`
2. **Engenharia de features:** `python src/features/build_features.py`
3. **Treino do modelo:** `python src/models/train_model.py`
4. **Execução do sistema multiagente:** `python src/agents/crew_system.py`

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Machine Learning:** Scikit-Learn (RandomForest, etc.)
* **Análise de Dados:** Pandas, NumPy
* **Inteligência Artificial / Agentes:** CrewAI / LLM
* **Engenharia de Software:** Estrutura modular orientada a pipelines

---

## 📄 Licença

Distribuído sob a licença MIT. Consulta o ficheiro `LICENSE` para mais detalhes.