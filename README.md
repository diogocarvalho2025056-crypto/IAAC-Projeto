# Deteção e Classificação de Ransomware com Machine Learning

## 📌 Visão Geral
Este projeto aplica técnicas de Aprendizagem Automática para a deteção e prevenção de Ransomware em ficheiros executáveis PE (Portable Executable), utilizando dados estáticos do cabeçalho e métricas comportamentais dinâmicas.

## 📊 Metodologia & Divisão dos Dados
Seguindo a metodologia CRISP-DM, o dataset (`ransom.csv` com 21.752 amostras) foi pré-processado e dividido em:
- **70% Treino** (~15.226 amostras)
- **15% Validação** (~3.263 amostras)
- **15% Teste** (~3.263 amostras)

## 📁 Estrutura do Repositório
- `Business_understanding/`: Documentação de negócio e Machine Learning Canvas.
- `data/`: Datasets brutos (`raw/`) e limpos (`processed/`).
- `notebooks/`:
  - `01_eda_ransomware.ipynb`: Análise exploratória e visualizações.
  - `02_preprocessing.ipynb`: Limpeza, conversão de hexadecimais e binarização.
  - `03_model_training.ipynb`: Divisão 70/15/15 e treino de modelos.
  - `04_model_evaluation.ipynb`: Avaliação final no conjunto de teste (15%) e importância de features.
- `src/`: Módulos Python reutilizáveis (`features.py` e `models.py`).
- `models/`: Modelo otimizado e serializado (`xgboost_ransomware_model.pkl`).

## 🚀 Como Executar
1. Instalar as dependências:
   ```bash
   pip install -r requirements.txt# Deteção e Classificação de Ransomware com Machine Learning

## 📌 Visão Geral
Este projeto aplica técnicas de Aprendizagem Automática para a deteção e prevenção de Ransomware em ficheiros executáveis PE (Portable Executable), utilizando dados estáticos do cabeçalho e métricas comportamentais dinâmicas.

## 📊 Metodologia & Divisão dos Dados
Seguindo a metodologia CRISP-DM, o dataset (`ransom.csv` com 21.752 amostras) foi pré-processado e dividido em:
- **70% Treino** (~15.226 amostras)
- **15% Validação** (~3.263 amostras)
- **15% Teste** (~3.263 amostras)

## 📁 Estrutura do Repositório
- `Business_understanding/`: Documentação de negócio e Machine Learning Canvas.
- `data/`: Datasets brutos (`raw/`) e limpos (`processed/`).
- `notebooks/`:
  - `01_eda_ransomware.ipynb`: Análise exploratória e visualizações.
  - `02_preprocessing.ipynb`: Limpeza, conversão de hexadecimais e binarização.
  - `03_model_training.ipynb`: Divisão 70/15/15 e treino de modelos.
  - `04_model_evaluation.ipynb`: Avaliação final no conjunto de teste (15%) e importância de features.
- `src/`: Módulos Python reutilizáveis (`features.py` e `models.py`).
- `models/`: Modelo otimizado e serializado (`xgboost_ransomware_model.pkl`).

## 🚀 Como Executar
1. Instalar as dependências:
   ```bash
   pip install -r requirements.txt