# CyberGuard AI V4

**Relatórios HTML:** já disponíveis nos resultados e no histórico, com abertura no browser, download e estilos de impressão para guardar como PDF. Consulta `RELATORIOS_HTML.md`.

Os classificadores de ransomware estático e phishing de URL estão descritos em `V31_ENTREGA.md`, com os dados e métricas usados na avaliação.

Aplicação local para análise de ficheiros e URLs com classificadores do projeto IAAC e síntese técnica obrigatória com CrewAI.

## Começar

1. Instala Python 3.13 com o Python Launcher e instala o Ollama.
2. Abre o Ollama e executa `ollama pull qwen2.5:3b` no PowerShell.
3. Executa `install.bat` para instalar os classificadores e o CrewAI.
4. Executa `run.bat` e abre http://127.0.0.1:8000.

A página indica se o CrewAI e o modelo estão disponíveis. Podes escolher outro modelo local com a variável `CYBERGUARD_OLLAMA_MODEL`. O servidor Ollama deve responder em `127.0.0.1:11434`.

## Fluxo de análise

O servidor calcula a classificação ou os indicadores técnicos. Em seguida, o CrewAI executa dois agentes em sequência. O analista interpreta as evidências e o revisor redige a síntese. O histórico, o JSON e o HTML incluem a síntese e identificam o modelo local e os agentes usados.

A classificação continua a vir do classificador. Os agentes recebem resultados técnicos estruturados, sem o ficheiro original ou o URL introduzido. As tarefas de interpretação funcionam sem ferramentas de execução ou navegação. Se o CrewAI ou o Ollama falhar, a API devolve HTTP 503 e a análise não é guardada. Os relatórios antigos podem ser consultados através do histórico.

## O que funciona

- Upload de EXE/DLL PE32/PE32+: extração estática de 23 features e classificação pelo XGBoost original de malware, sem executar o ficheiro.
- CSV/JSON com features: inferência dos modelos malware, phishing e malware comportamental (até 10 amostras, 12 MiB).
- Classificação de phishing com as sete características lexicais do URL e o modelo treinado da V3.1.
- Confirmação do carregamento dos modelos e da ordem das features.
- Score da classe ameaça e contribuições SHAP quando disponíveis.
- Histórico SQLite e relatório JSON com features, método, limitações e hash SHA-256 do upload. Os bytes originais não são guardados pela aplicação; o parser de upload pode usar armazenamento temporário.
- Interface responsiva em português de Portugal, com estados de erro e API documentada em `/docs`.

## Limites que fazem parte do resultado

O extrator PE é novo e experimental: a classificação é real, mas a equivalência com o extrator original do dataset ainda não foi comprovada com pares de ficheiros/features. As métricas do treino não devem ser apresentadas como desempenho deste novo pipeline. As definições estão em `backend/pe_features.py`.

A análise de ransomware em EXE/DLL utiliza o modelo estático de 16 características. O modelo comportamental de 165 características exige dados estruturados de sandbox e classifica malware em geral. A análise de URLs usa o modelo lexical de sete características. O classificador completo de phishing recebe 30 indicadores através de CSV ou JSON.

Os scores são saídas do modelo, não probabilidades calibradas de infeção. Benigno não garante segurança. Ficheiros suspeitos devem ser tratados num ambiente de análise isolado.

## Estrutura

`backend/`: API, extrator PE, inferência e histórico. `frontend/`: interface sem build. `models/`: artefactos originais. `src/`: módulos originais preservados como referência, sem ligação obrigatória ao LLM. `legacy_web/`: camada Web v2 de referência. `tests/`: testes funcionais. `runtime/`: criado ao executar, contém dados locais e não deve ser versionado.

## Testes

Executa `python -m unittest discover -v` com o ambiente virtual ativo. Os testes da API simulam a síntese CrewAI para poderem correr sem um modelo Ollama em memória. Para verificar a integração com o teu modelo, abre a aplicação, confirma o estado do CrewAI e analisa um URL de teste.
