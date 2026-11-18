# Relatórios HTML

A aplicação gera relatórios autónomos com o estilo dos exemplos IAAC enviados: fundo escuro, classificação, confiança nesta previsão, barras dos scores e tabela das principais features com contribuições SHAP.

Após analisar, usa **Descarregar relatório HTML** ou **Abrir relatório**. O histórico disponibiliza HTML e JSON. Os relatórios HTML também funcionam sem ligação à Internet. Para guardar como PDF, abre o HTML no browser e usa Ctrl+P → Guardar como PDF; existe uma folha de estilo de impressão.

Incluem recomendações baseadas no resultado técnico, limitações, features utilizadas, identificação e SHA-256 do modelo e do upload, quando registados. Não usam um LLM para inventar evidências ou alterar o diagnóstico.

Os HTML podem ser gerados para análises antigas presentes na base de dados SQLite. Campos não registados são omitidos ou apresentados como indisponíveis. Para inspeções sem modelo, não são inventados scores. Não ransomware não é apresentado como benigno.

API: `/api/reports/{id}/html` descarrega; `?download=false` abre no browser. A rota JSON original mantém-se em `/api/reports/{id}`. Conteúdo de entrada é escapado e scripts estão bloqueados por CSP.

Os relatórios incluem as features e os hashes da análise. Trata-os como informação técnica do projeto ao partilhá-los.


## Cobertura das evidências na V5 Web

O relatório apresenta o veredito e o estado da análise, os scores do
classificador, as deteções do VirusTotal e os dados comportamentais
disponíveis. Evidências em falta ficam registadas com o motivo da análise
parcial. Fontes divergentes ficam identificadas. O relatório técnico continua
disponível quando o CrewAI ou o Ollama não consegue produzir a síntese.
