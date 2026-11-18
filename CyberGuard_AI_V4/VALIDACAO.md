# Validação da V5 Web

Validação de 18 de novembro de 2026 em Windows, com Python 3.13 e Edge.
A aplicação foi iniciada com `cmd /c run.bat`, em
<http://127.0.0.1:8000>. A síntese foi validada com CrewAI e Ollama
(`qwen2.5:0.5b`).

## Interface e serviços reais

| Entrada | Artefacto e resultado real | VirusTotal real | Relatório |
| --- | --- | --- | --- |
| Bloco de Notas do Windows (`notepad.exe`) | XGBoost PE de 23 features. Benigno, score 0,29% | Consulta por SHA-256. 0 deteções maliciosas, 0 suspeitas. Veredito de sandbox Zenbox `harmless` | Completo, fontes concordantes |
| `https://example.com/` | XGBoost lexical de 7 features. Legítimo, score 0,15% | Consulta de reputação. 0 deteções maliciosas, 0 suspeitas | Completo, fontes concordantes |

Em ambas as análises, foram confirmados o resultado no formulário, a
síntese CrewAI e o acesso ao JSON gravado. Foi também aberta a exportação
HTML. Uma execução anterior sem chave mostrou a análise parcial no Edge
para ambas as entradas. A seleção comportamental sem export mostrou as
features em falta e deixou a classificação indeterminada. Um ficheiro de
texto benigno criado para o teste devolveu um hash desconhecido na API
real. Na análise comportamental desse ficheiro, a API Web confirmou o
estado parcial e a ausência de telemetria.

## Testes automatizados

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

34 testes passaram. Os testes carregam artefactos treinados e exercitam
extração PE, inferência, HTTP, histórico e relatórios. Os casos de
divergência, hash desconhecido, quota, timeout, resposta pendente e
classificação de família usam respostas VirusTotal controladas. Um vetor
controlado de 165 features percorre o classificador comportamental real.
Os casos comportamentais incluem telemetria em falta, export incompatível
e rejeição de um valor fracionário numa coluna inteira.

## Validação pendente

Falta configurar uma sandbox isolada e validar o mapeamento da telemetria
para as 165 features. A consulta real devolveu um veredito resumido de
sandbox. O veredito não contém as medições necessárias ao modelo
comportamental. A equivalência dos extratores Web PE e lexical com o
pré-processamento dos datasets originais continua sem validação pareada.
