# CyberGuard AI — pacote de integração Web

**Referência histórica.** Para a versão mantida e validada nesta entrega, consulta o [README da V5 Web](../README.md).

Este ZIP é uma **camada de integração Web com uploads reais** para copiar para a raiz de `ProjetoIAAC-main` ou `IAAC-Projeto`. **Não inclui** os modelos originais, datasets, código `src/` ou código `crewai_version/`; estes mantêm-se no projeto principal.

## Instalação no Windows

1. Faz cópia de segurança do projeto atual (especialmente de `backend/` e `frontend/`, se existirem).
2. Extrai o ZIP **sobre a raiz do projeto original** — a pasta que contém `src/`, `models/`, `dataset/` e `crewai_version/`.
3. Executa `install-web.bat` uma vez.
4. Executa `run-web.bat` para iniciar o site em <http://127.0.0.1:8000>.
5. Consulta a API em <http://127.0.0.1:8000/docs>.

Se a Web estiver noutra pasta, podes indicar o projeto principal usando `CYBERGUARD_CORE_PATH` (variável de ambiente do Windows). Quando ambas as pastas estiverem lado a lado e a original se chamar `ProjetoIAAC-main`, a deteção é automática.

**Instalação do CrewAI (opcional):** executa `install-ai.bat` e certifica-te de que o Ollama está ativo e com o modelo Qwen instalado. As funções da ponte CrewAI pressupõem as funções `criar_crew`, `criar_task_*`, `definir_amostra_*` e `obter_ultimo_resultado_*` no código original; se as assinaturas diferirem, será necessário adaptar a ponte.

## O que está integrado

- Dashboard FastAPI com estado dos ficheiros de modelos e relatórios HTML existentes.
- Páginas Web com upload por arrastar e largar, triagem de URLs e execução real de `src.malware_inference.prever_malware`, `src.ransomware_inference.prever_ransomware` e `src.phishing_inference.prever_phishing`.
- Upload real de ficheiros (até 12 MiB) sem execução: identificação de formato, SHA-256, entropia e indicadores estáticos.
- Upload de CSV/JSON **completo** com as features esperadas: classificação verdadeira com o respetivo modelo treinado (até 10 linhas).
- Entrada de URLs reais: triagem lexical local e indicadores de atenção (sem visitar o URL).
- As rotas antigas de amostras do dataset permanecem na API para regressão/testes, mas **os botões de benigno/ameaça foram retirados da interface**.
- Integração direta com Ollama para enviar perguntas e escolher um modelo instalado.
- Endpoint opcional para CrewAI.
- Histórico Web em `reports/web_history.json`, sem guardar as features submetidas.
- Download dos relatórios HTML já existentes.

**Muito importante:** os três classificadores IAAC foram treinados com **features estruturadas**, não com ficheiros arbitrários. O upload de EXE, DLL, PDF, EML etc. é uma **inspeção estática**, não uma classificação de malware/ransomware pelo XGBoost. Um URL real é submetido a **triagem lexical sem navegação na rede**, não ao classificador IAAC de Phishing. Para obter classificação automática desses inputs brutos com ML será necessário acrescentar (e validar contra os dados de treino) um pipeline de extração específico ou treinar modelos compatíveis com essas entradas. Nunca são inventadas features. Esta versão **não treina novamente** os modelos.

## Endpoints

| Método | Caminho | Descrição |
| --- | --- | --- |
| GET | `/api/health` | Estado do projeto, modelos, Ollama e CrewAI |
| GET | `/api/models` | Modelos detetados |
| POST | `/api/analyze/upload/{tipo}` | multipart/form-data campo `file`; CSV/JSON usa modelo, outros ficheiros inspecionados sem execução |
| POST | `/api/analyze/url` | JSON `{"url": "https://..."}`; triagem lexical sem navegação |
| GET | `/api/samples/{tipo}/{label}` | Exemplo `benign` ou `threat` do dataset |
| POST | `/api/analyze/{tipo}` | Análise com o classificador IAAC |
| POST | `/api/analyze/{tipo}/sample/{label}` | Classificação direta de um exemplo do dataset |
| POST | `/api/agents/{tipo}` | CrewAI opcional (dependências necessárias) |
| POST | `/api/assistant` | Pergunta ao Ollama |
| GET | `/api/history` | Histórico de análises Web |
| GET | `/api/reports/{ficheiro}` | Download de relatório HTML existente |

Tipos suportados: `malware`, `ransomware` e `phishing`.

## Acesso por outros dispositivos na LAN

Por omissão, `run-web.bat` usa `127.0.0.1`, e só o próprio PC pode aceder.

Para testes numa **rede privada de confiança**, abre o PowerShell na pasta do projeto:

```powershell
$env:CYBERGUARD_WEB_USER="utilizador"
$env:CYBERGUARD_WEB_PASSWORD="palavra-passe-longa-e-unica"
.\run-lan.bat
```

Descobre o IP local com `ipconfig` e, noutro dispositivo, abre `http://IP-DO-PC:8000`. Pode ser necessário autorizar a porta 8000 no perfil **Privado** da Firewall. **Não exponhas diretamente à Internet.** A autenticação HTTP Basic sobre HTTP não cifra as credenciais; para redes não confiáveis, usa TLS ou um túnel autenticado. Não disponibilizes este serviço em redes públicas ou académicas sem autorização.

## Observações técnicas

- Nesta versão a UI estática é entregue localmente, sem fontes nem bibliotecas por CDN.
- O módulo de CrewAI do projeto original pode manter estado global por amostra. A Web serializa as chamadas CrewAI dentro de um único processo Uvicorn para evitar misturas de resultados; não uses múltiplos workers sem refatorar as tools.
- O ficheiro `web_history.json` é gravado na pasta `reports/`, apenas após uma execução bem-sucedida.
- Os logs e modelos existentes continuam sob a gestão do projeto original.
- A Web não tem sistema de contas, RBAC, CSRF específico para autenticação com cookies, nem TLS. Utiliza-a localmente ou em laboratório fechado.

## Regras de segurança para inputs reais

- Os uploads não são guardados permanentemente nem executados; a aplicação aceita até 12 MiB por ficheiro e não extrai automaticamente arquivos ZIP. O parser multipart do servidor pode usar ficheiros temporários durante o pedido.
- Nunca abras ficheiros suspeitos numa aplicação do sistema. Uma inspeção estática **não garante segurança**.
- Os URLs introduzidos não são visitados, não são resolvidos por DNS e não são descarregados: isto evita SSRF na plataforma Web.
- O histórico guarda apenas tipo e resumo, sem guardar o conteúdo do ficheiro nem o endereço URL completo.
- Usa esta aplicação só em localhost ou LAN controlada com autenticação; para uma disponibilização pública serão precisos TLS, contas e permissões, CSRF e limites adicionais.
