ProjetoIAAC/
├── data/
│   ├── raw/                  # Coloca aqui o teu ransom.csv original
│   ├── interim/              # Dados limpos intermédios
│   └── processed/            # Dados finais transformados
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── make_dataset.py   # Limpeza e tratamento inicial
│   ├── features/
│   │   ├── __init__.py
│   │   └── build_features.py # Tratamento de Hexadecimais e PE Headers
│   ├── models/
│   │   ├── __init__.py
│   │   └── train_model.py    # Treino com scikit-learn (RandomForest, etc.)
│   └── agents/
│       ├── __init__.py
│       └── crew_system.py    # Sistema Multiagente (Classificador + LLM)
├── models/                   # Onde o melhor modelo .pkl é guardado
├── notebooks/                # Notebooks de suporte
├── reports/figures/          # Diagramas de arquitetura e casos de uso
├── requirements.txt
└── main.py                   # Script Python principal que une tudo