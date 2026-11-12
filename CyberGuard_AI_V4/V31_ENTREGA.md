# Atualização para entrega: V3.1

Esta atualização substitui as limitações de entrada descritas na documentação inicial da V3.

## Fluxos disponíveis

- Malware: EXE/DLL com o modelo original de 23 features.
- Ransomware estático: EXE/DLL com novo XGBoost de 16 features de cabeçalhos, sem sandbox. Target: Category == Ransomware; a classe negativa inclui benigno e outros malwares. Não ransomware não significa benigno.
- Phishing de URL: novo XGBoost lexical com 7 features extraíveis do URL, treinado com o dataset de phishing do projeto. Não é o modelo completo de 30 features. O URL não é visitado nem guardado.
- Modelos originais de phishing (30 features) e comportamento (165 features): mantidos para CSV/JSON completo.
- Outros formatos: inspeção estática com identificação, hash, entropia e indicadores, sem afirmar uma classificação ML.

## Treino e avaliação

Os scripts de treino estão em `tools/train_ransomware_static.py` e `tools/train_phishing_url.py`. As métricas, esquema, target e hash dos datasets estão em `models/*_metrics.json`.

Ransomware: uma amostra por md5; oito grupos com rótulos contraditórios foram excluídos; divisão estratificada 70/15/15 sem md5 partilhados. O teste interno teve recall 63,96%, precision 94,04% e F1 76,14%. Esta versão falha uma parte relevante das amostras e exige melhoria futura. Não deve ser apresentada como proteção de produção.

Phishing lexical: divisão agrupada por registo original completo, sem afinação no conjunto final. O dataset não contém os URLs originais; não é possível verificar isolamento por domínio ou tempo. Websites diferentes podem partilhar o mesmo perfil lexical e receber o mesmo score.

No teste interno de 573 amostras, o modelo lexical teve accuracy 67,54%, precision 63,10%, recall 89,53%, F1 74,02% e ROC-AUC 0,7021. É uma versão limitada: os sete indicadores geram falsos positivos relevantes. O modelo completo de 30 features é preservado; as métricas desse modelo não são atribuídas à versão lexical.

As regras do extrator lexical estão documentadas no código. Não foram validadas contra pares URL/features do dataset original. A extração PE também exige validação externa pareada. Estas limitações aplicam-se às previsões apesar de a inferência com os modelos ser real.

## Demonstração

1. Executar `run.bat` e abrir http://127.0.0.1:8000.
2. Selecionar Malware ou Ransomware e submeter um EXE/DLL de teste autorizado.
3. Abrir Phishing de URL e introduzir um URL. O resultado identifica a inferência treinada e disponibiliza as features no relatório.
4. Mostrar histórico, identificação SHA-256 do modelo e relatório JSON.

Não executar ficheiros suspeitos no Windows. O upload realiza apenas análise estática.
