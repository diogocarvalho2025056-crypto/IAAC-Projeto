# Entrega ao professor · CyberGuard AI V5 Web

A aplicação local combina inferência dos classificadores do projeto IAAC com
reputação do VirusTotal. Apresenta as duas fontes, o estado e o veredito no
relatório Web, HTML e JSON. O CrewAI usa Ollama para organizar a síntese a
partir dos resultados registados pelo backend.

## Demonstração no Windows

1. A partir da pasta com `run.bat`, usa `install.bat` se as dependências ainda
   não estiverem instaladas. Inicia o Ollama para a síntese.
2. Configura `VIRUSTOTAL_API_KEY` no ambiente do backend ou copia
   `.env.example` para `.env` e preenche a chave localmente.
3. Executa `cmd /c run.bat` e abre <http://127.0.0.1:8000>.
4. Em Malware, analisa um executável Windows benigno, como `notepad.exe`.
   Em Phishing de URL, usa `https://example.com/`. Abre o relatório técnico
   e compara a classificação do modelo com o resultado VirusTotal.
5. Em Malware comportamental, usa um ficheiro com um export compatível ou
   observa o estado parcial quando o export associado ao SHA-256 estiver
   em falta.

## Âmbito e limites

- O modelo PE de malware usa 23 features estáticas. O modelo estático de
  ransomware usa 16 features e tem métricas de teste interno próprias.
- O classificador comportamental usa 165 features. Um export de sandbox
  existente tem de fornecer as medições no esquema original. A recolha
  automática de telemetria ainda depende de uma sandbox isolada configurada
  e de um mapeamento validado.
- A classificação lexical de URLs tem sete entradas. Os testes da aplicação
  verificam o percurso técnico. Os extratores Web de PE e URL continuam sem
  validação pareada com os datasets originais.
- O estado completo indica cobertura pelas duas fontes. As pontuações do
  modelo e as contagens do VirusTotal mantêm as respetivas escalas.

## Documentos de avaliação

- [Resultados reais, controlados e pendentes](VALIDACAO.md)
- [Configuração, esquema comportamental e arranque](README.md)
- [Estrutura e exportação do relatório HTML](RELATORIOS_HTML.md)
- [Treino e métricas dos classificadores estático e lexical](V31_ENTREGA.md)
- Fichas dos modelos de [malware](models/malware_model.md),
  [malware comportamental](models/ransomware_model.md) e
  [phishing de 30 features](models/phishing_model.md).
