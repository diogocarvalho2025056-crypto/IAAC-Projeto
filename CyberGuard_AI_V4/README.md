# CyberGuard AI V5 Web

**Relatórios HTML:** já disponíveis nos resultados e no histórico, com abertura no browser, download e estilos de impressão para guardar como PDF. Consulta `RELATORIOS_HTML.md`.

Os classificadores de ransomware estático e phishing de URL estão descritos em `V31_ENTREGA.md`, com os dados e métricas usados na avaliação.

Aplicação local para análise de ficheiros e URLs com classificadores do projeto IAAC, reputação VirusTotal e síntese técnica com CrewAI.

Para a entrega, consulta [o guia para o professor](ENTREGA_PROFESSOR.md) e [o registo de validação](VALIDACAO.md).

## Começar

1. Instala Python 3.13 com o Python Launcher e instala o Ollama.
2. Abre o Ollama e executa `ollama pull qwen2.5:3b` no PowerShell.
3. Executa `install.bat` para instalar os classificadores e o CrewAI.
4. Executa `run.bat` e abre http://127.0.0.1:8000.

A página indica se o CrewAI e o modelo estão disponíveis. Podes escolher outro modelo local com a variável `CYBERGUARD_OLLAMA_MODEL`. O servidor Ollama deve responder em `127.0.0.1:11434`.

## Fluxo de análise

O servidor reúne a inferência local e a reputação no VirusTotal. O CrewAI interpreta essas evidências e escolhe a ordem em que o resumo apresenta os resultados registados. O histórico, o JSON e o HTML incluem a síntese e identificam o modelo local e os agentes usados.

A classificação continua a vir do classificador. Os agentes recebem resultados técnicos estruturados, sem o ficheiro original ou o URL introduzido. As tarefas de interpretação funcionam sem ferramentas de execução ou navegação. Se o CrewAI ou o Ollama falhar, o relatório técnico é guardado e indica que a síntese está indisponível. Os relatórios antigos podem ser consultados através do histórico.

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

## Evidências no CyberGuard AI V5 Web

No Windows, a partir desta pasta, executa `cmd /c run.bat` e abre
http://127.0.0.1:8000. Se a instalação local ainda não existir, executa
`install.bat`. Copia `.env.example` para `.env` e configura
`VIRUSTOTAL_API_KEY` no backend. A variável de ambiente com o mesmo nome
tem precedência. O CrewAI usa Ollama em 127.0.0.1:11434, com
`qwen2.5:3b` por omissão. Uma falha na síntese preserva o relatório técnico.

- Ficheiros brutos usam apenas a consulta de reputação pelo SHA-256.
  CSV/JSON de features usa o classificador selecionado e o hash do upload
  identifica apenas o contentor de dados. Seleciona a caixa correspondente.
- O URL usa o classificador lexical treinado com 7 colunas pré-codificadas
  em −1, 0 ou 1. O modelo de 30 features continua disponível para vetores
  completos. O dataset lexical não contém os URLs originais para validação
  pareada. A consulta de reputação é GET e a aplicação não visita a página.
  Endereços locais, consultas e fragmentos exigem consentimento por análise.
  Desmarca a consulta de reputação para qualquer endereço cujo caminho
  inclua informação privada que não queiras partilhar.
- A opção comportamental procura `runtime/behavior/<sha256>.json` com o
  objeto `{"sha256":"<sha256>","features":{...}}`. A sandbox externa deve
  fornecer um export de confiança ligado ao ficheiro e com as 165 features
  já transformadas conforme `models/ransomware_features.json`.
  Nenhum executável é corrido pela aplicação. Falta uma ligação a uma
  sandbox e um mapeamento validado da sua telemetria para o esquema de treino.
  O relatório inclui os vereditos de sandbox já presentes na resposta
  VirusTotal quando disponíveis. Esses vereditos não fornecem o vetor de 165 features.
- `src/features.py` documenta a conversão hex/decimal e a codificação
  binária de categorias e flags. O treino remove colunas constantes e
  aplica `fillna(0)` nas linhas do dataset. O Web exige valores numéricos
  finitos para todas as colunas do export e não aplica esse preenchimento a
  medições de sandbox ausentes. Confirma os nomes e a ordem com o artefacto. Os metadados do XGBoost identificam 104 colunas inteiras e 61 de ponto flutuante.
- O estado completo indica cobertura pelo modelo selecionado e pelo
  VirusTotal. O relatório mostra respostas pendentes e indisponíveis
  como parciais. Repete a consulta após o processamento ou a reposição da
  quota. A divergência compara a classe 1 do modelo com a presença de
  deteções maliciosas ou suspeitas. Para ransomware estático, os motores
  podem sinalizar ameaças de outro tipo.
