# 🔄 Gestão de Projeto — Artefactos SCRUM (Phishing)

> Rascunho preparado a partir do roadmap do professor. **Ajustar com as datas e notas reais das reuniões do grupo** antes de entregar, e copiar as user stories para o Product Backlog do GitHub (uma issue por US).

## Equipa

| Elemento | Módulo | Branch (indicar a do GitHub) |
|---|---|---|
| José Maria Alves | Malware | _preencher_ |
| Tomás Matos | Ransomware | _preencher_ |
| Diogo Carvalho | Phishing | _preencher_ |

## Product Backlog — User Stories (Phishing)

| ID | User Story | Sprint | Responsável | Estado |
|---|---|---|---|---|
| US-PH01 | Como Analista de Cibersegurança, quero definir o problema de deteção de phishing e preencher o Machine Learning Canvas, para alinhar o objetivo de negócio com o modelo. | 1 | Diogo | Feito |
| US-PH02 | Como Engenheiro de ML, quero fazer a EDA do dataset (univariada, bivariada, multivariada, correlações Pearson/Spearman), para compreender os dados. | 1 | Diogo | Feito |
| US-PH03 | Como Engenheiro de ML, quero limpar o dataset (colunas não preditivas, duplicados, perfis contraditórios, valores em falta e outliers), para treinar com dados fiáveis. | 2 | Diogo | Feito |
| US-PH04 | Como Engenheiro de ML, quero dividir os dados de forma estratificada em 70/15/15, para avaliar sem enviesar o teste. | 2 | Diogo | Feito |
| US-PH05 | Como Engenheiro de ML, quero treinar e comparar vários algoritmos supervisionados (Regressão Logística, k-NN, Naive Bayes, SVM, Árvore de Decisão, Random Forest, Gradient Boosting, XGBoost), para escolher o melhor. | 2 | Diogo | Feito |
| US-PH06 | Como Auditor de Segurança, quero otimizar os hiperparâmetros do XGBoost com foco no Recall de phishing, para reduzir falsos negativos. | 3 | Diogo | Feito |
| US-PH07 | Como Auditor de Segurança, quero avaliar o modelo final com matriz de confusão, Precision, Recall, F1, ROC-AUC e análise de overfitting, para conhecer os seus limites. | 3 | Diogo | Feito |
| US-PH08 | Como Programador, quero guardar o modelo e criar o módulo de inferência com validação de entradas, para que outros agentes o possam usar. | 3 | Diogo | Feito |
| US-PH09 | Como Analista de SOC, quero um agente de phishing ligado ao orquestrador e ao agente de relatórios, para receber uma explicação em português. | 3 | Diogo | Feito |
| US-PH10 | Como Programador, quero testes automáticos (pytest) do módulo de phishing, para garantir que a integração não parte os módulos de Malware e Ransomware. | 3 | Diogo | Feito |
| US-PH11 | Como Equipa, quero um notebook `multiagent_system.ipynb` que demonstre os três agentes em conjunto, para apresentar ao professor. | 3 | Grupo | Feito |

## Sprint Backlog

**Sprint 1 — Business & Data Understanding** (aulas de 18/09 e 21/09)
US-PH01, US-PH02

**Sprint 2 — Data Preparation & Modeling** (a partir de 23/09)
US-PH03, US-PH04, US-PH05

**Sprint 3 — Evaluation & Multi-Agent System** (a partir de 01/10)
US-PH06, US-PH07, US-PH08, US-PH09, US-PH10, US-PH11

## Cerimónias

### Daily Scrum (modelo)

| Data | O que fiz | O que vou fazer | Impedimentos |
|---|---|---|---|
| _preencher_ | _preencher_ | _preencher_ | _preencher_ |

### Sprint Review — Sprint 1/2/3 (rascunho)

- **Entregue (Phishing):** ver tabela de user stories (estado "Feito").
- **Resultado do incremento:** modelo XGBoost com Recall de phishing de 95,7% e ROC-AUC de 0,993 no teste; agente integrado no orquestrador.
- **Feedback a recolher do professor/grupo:** _preencher_.

### Sprint Retrospective (rascunho)

- **O que correu bem:** pipeline organizado por fases CRISP-ML; reutilização da estrutura de inferência/agente dos colegas.
- **O que correu menos bem:** convenção de classes diferente entre módulos (phishing usava -1/1 no dataset); utilitários com nomes iguais nos três projetos (`eda_utils.py`, `model_utils.py`...), que colidiam ao juntar.
- **Ações de melhoria:** convenção única `1 = ameaça`; prefixar utilitários por módulo (`phishing_*_utils.py`); integrar mais cedo e em branches separadas.
