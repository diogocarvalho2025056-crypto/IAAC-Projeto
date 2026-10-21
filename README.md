# Deteção de Ransomware/Malware com Machine Learning

Projeto de **Inteligência Artificial Aplicada à Cibersegurança** (CTeSP Cibersegurança, ISTEC Porto) — módulo **Ransomware**, Tomás Matos. Classifica executáveis PE como benignos ou maliciosos com dados estáticos (cabeçalho PE) e dinâmicos (comportamento em sandbox), e integra um agente generativo que explica cada decisão.

## Dados e metodologia (CRISP-DM)
- `data/raw/ransom.csv`: 21.752 linhas, **13.903 ficheiros únicos** (md5), 50% benigno / 50% malware (4.762 ransomware, 2.647 RAT, 2.018 stealer, 1.449 trojan).
- Pré-processamento: hexadecimais e decimais → número; listas → flags binárias; categorias → one-hot; **165 features** finais.
- Divisão **70/15/15 estratificada e agrupada por md5**: um ficheiro nunca está em dois conjuntos.
- 7 classificadores + Stratified Group 5-Fold CV + GridSearchCV (XGBoost) + análise de overfitting.
- Métrica principal: **Recall** (um malware não detetado é o pior erro), entre modelos com CV F1 ≥ 0,95.

## Resultados (Test Set, 3.265 amostras)
XGBoost baseline: Accuracy 99,54% · Precision 99,21% · **Recall 99,88%** · F1 99,54% · ROC-AUC 0,9993 (2 falsos negativos, 13 falsos positivos).

⚠️ `processes_malicious` pesa ~79%; sem ela o F1 é 0,988 e só com features estáticas 0,951. Ver `models/ransomware_model.md`.

## Estrutura
```text
├── Business_understanding/   Canvas, arquitetura, SCRUM
├── data/raw/                 ransom.csv
├── data/processed/           ransom_cleaned.csv (gerado), ransom_demo_samples.csv
├── models/
│   ├── modeling.py           pipeline completo (python models/modeling.py [--quick])
│   ├── ransomware_model.pkl / ransomware_features.json / ransomware_metrics.json
│   ├── ransomware_cv_results.csv
│   └── ransomware_model.md   ficha do modelo
├── notebooks/                01 EDA · 02 pré-processamento · 03 treino · 04 avaliação · 05 pipeline mestre
├── src/
│   ├── features.py           pré-processamento
│   ├── models.py             split, CV, tuning, overfitting, avaliação
│   ├── ransomware_inference.py  validação + previsão
│   ├── ransomware_agent.py   agente de classificação
│   ├── report_agent.py       relatório (LLM Qwen2.5-1.5B ou modelo fixo)
│   └── orchestrator.py       encaminha pedidos
├── tests/                    pytest
└── main.py                   menu interativo
```

## Como executar
```bash
pip install -r requirements.txt
python models/modeling.py     # (re)treina e guarda modelo, features e métricas
python main.py                # menu: 2 - Ransomware
pytest                        # 19 testes
```
Para o relatório por LLM, instalar `transformers`, `accelerate` e `torch` (descarrega o Qwen2.5-1.5B na primeira execução). Sem eles, usa-se um relatório por modelo fixo; `IAAC_SEM_LLM=1` força este modo.

## Limitações
Resultados específicos deste dataset; é necessário testar com amostras externas e recentes antes de qualquer uso real. O modelo separa benigno de malware, não identifica a família.
