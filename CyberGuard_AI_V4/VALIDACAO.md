# Validação da V3

Data: 10 de novembro de 2026.

## Verificações concluídas

Sete testes passaram com Python 3.13.5 e as dependências fixadas em `requirements.txt`:

- Extração PE32 e PE32+, incluindo BaseOfData, ImageBase, tamanhos, entropia e overlay.
- Contagem de imports e exports em ambos os formatos.
- Rejeição de diretórios fora dos limites do ficheiro.
- Rejeição de ficheiros inválidos ou truncados.
- Carregamento e previsão com os três artefactos reais; validação de esquema e números finitos.
- Fluxo direto de upload PE para inferência, armazenamento SQLite e leitura do relatório; classificação de features de phishing e rejeição de EXE na análise comportamental.
- Triagem de URL sem ML e rejeição de features ausentes/NaN.

O fluxo direto utiliza os handlers reais e os modelos reais. Apenas a execução em thread auxiliar é substituída por uma chamada síncrona nos testes sem sockets. Estes testes não substituem testes HTTP.

Também foram verificadas a sintaxe JavaScript com `node --check` e a compilação dos módulos Python.

## Verificações pendentes

Os testes com cliente HTTP ficaram bloqueados na criação de socketpair pelo event loop Windows, antes da execução dos handlers. Não foi concluída uma sessão de navegação nem uma revisão visual no browser. Os testes HTTP estão disponíveis para execução fora desta restrição.

Não foram executadas amostras de malware nem recolhidos comportamentos em sandbox. Não foi treinado um novo modelo. A validação estatística com ficheiros externos e a equivalência das features extraídas com o extrator original continuam pendentes. Os ficheiros PE dos testes são sintéticos e verificam a estrutura do pipeline, não a capacidade de deteção em ambiente real.
