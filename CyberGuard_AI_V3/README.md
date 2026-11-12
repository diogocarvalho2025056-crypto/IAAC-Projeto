# CyberGuard AI V3

**Atualização V3.1:** consulta `V31_ENTREGA.md`. Foram acrescentados modelos específicos para ransomware estático (EXE/DLL, 16 features) e phishing de URL (7 features lexicais), com scripts de treino e métricas. As descrições abaixo do comportamento inicial da V3 ficam subordinadas a essa atualização.

Aplicação local Windows para análise de executáveis PE e inferência com os três modelos do projeto IAAC. O projeto original não é alterado.

## Começar

1. Instalar Python 3.13 com o Python Launcher.
2. Executar `install.bat` para criar um ambiente próprio, instalar dependências e testar.
3. Executar `run.bat` e abrir http://127.0.0.1:8000.

Não é necessário Ollama nem CrewAI para classificar. O servidor está limitado ao computador local. Não há dependências de fontes, scripts ou serviços externos na interface.

## O que funciona

- Upload de EXE/DLL PE32/PE32+: extração estática de 23 features e classificação pelo XGBoost original de malware, sem executar o ficheiro.
- CSV/JSON com features: inferência dos modelos malware, phishing e malware comportamental (até 10 amostras, 12 MiB).
- Triagem lexical de URLs sem acesso à rede. Este modo não utiliza o modelo de phishing.
- Confirmação do carregamento dos modelos e da ordem das features.
- Score da classe ameaça e contribuições SHAP quando disponíveis.
- Histórico SQLite e relatório JSON com features, método, limitações e hash SHA-256 do upload. Os bytes originais não são guardados pela aplicação; o parser de upload pode usar armazenamento temporário.
- Interface responsiva em português de Portugal, com estados de erro e API documentada em `/docs`.

## Limites que fazem parte do resultado

O extrator PE é novo e experimental: a classificação é real, mas a equivalência com o extrator original do dataset ainda não foi comprovada com pares de ficheiros/features. As métricas do treino não devem ser apresentadas como desempenho deste novo pipeline. As definições estão em `backend/pe_features.py`.

O modelo chamado ransomware aprende benigno vs malware em geral, incluindo outras famílias. Requer 165 features completas, incluindo dados de sandbox. Esta V3 não executa binários nem preenche medições de comportamento com zeros. Para ransomware específico, é necessário treinar e validar um target específico.

O modelo de phishing exige 30 indicadores codificados em -1, 0 e 1. Não é aplicado a URLs brutos: não existe ainda um coletor validado de HTML, domínio e reputação equivalente ao treino.

Os scores são saídas do modelo, não probabilidades calibradas de infeção. Benigno não garante segurança. Ficheiros suspeitos devem ser tratados num ambiente de análise isolado.

## Estrutura

`backend/`: API, extrator PE, inferência e histórico. `frontend/`: interface sem build. `models/`: artefactos originais. `src/`: módulos originais preservados como referência, sem ligação obrigatória ao LLM. `legacy_web/`: camada Web v2 de referência. `tests/`: testes funcionais. `runtime/`: criado ao executar, contém dados locais e não deve ser versionado.

## Evolução seguinte

1. Validar o extrator com ficheiros e features produzidas pelo extrator original.
2. Treinar modelo estático de ransomware com classes adequadas e avaliação externa.
3. Construir coletor de phishing isolado e protegido contra SSRF, ou treinar um modelo lexical com URLs rotulados.
4. Exportar manifesto assinado dos modelos. As dependências da V3 estão fixadas às versões do ambiente usado na verificação; os relatórios identificam os modelos e esquemas por SHA-256.

Testes sem sockets: `python -m unittest tests.test_v3.PEFeaturesTests tests.test_v3.DirectPipelineTests -v` (executados pelo instalador). Testes HTTP adicionais: `python -m unittest tests.test_v3.IntegrationTests -v`. Os testes utilizam armazenamento temporário. Os modelos `.pkl` são os artefactos locais do projeto; não carregar ficheiros de modelo enviados por terceiros.
