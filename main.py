"""Demonstração do agente de Phishing (menu interativo).

Execução a partir da raiz do projeto:   python main.py
Para correr sem LLM (relatório determinístico):   IAAC_SEM_LLM=1 python main.py
"""
import sys
from pathlib import Path

import pandas as pd

pasta_projeto = Path(__file__).resolve().parent
if str(pasta_projeto) not in sys.path:
    sys.path.insert(0, str(pasta_projeto))

from src.orchestrator import processar_pedido

df = pd.read_csv(pasta_projeto / "dataset" / "phishing_prepared.csv")


def obter_amostra(classe):
    # No dataset: class = -1 -> Phishing | class = 1 -> Legítimo
    return df[df["class"] == classe].iloc[0].drop("class").to_dict()


def menu_phishing():
    print("\n======================================")
    print("ANÁLISE DE PHISHING")
    print("======================================")
    print("1 - Website legítimo\n2 - Website de phishing")
    opcao = input("\nOpção: ").strip()
    if opcao not in ("1", "2"):
        print("\nOpção inválida.")
        return

    resultado = processar_pedido("phishing", obter_amostra(1 if opcao == "1" else -1))
    if resultado["sucesso"] is False:
        print("\nErro:", resultado["erro"])
        return

    r = resultado["resultado"]
    print("\nClassificação:", r["classificacao"])
    print(f"Confiança: {r['confianca'] * 100:.2f}%")
    print(f"Probabilidade Legítimo: {r['probabilidade_legitimo'] * 100:.2f}%")
    print(f"Probabilidade Phishing: {r['probabilidade_phishing'] * 100:.2f}%")
    print("\nFeatures com maior contribuição:")
    for f in r["top_features"]:
        print(f"- {f['feature']} = {f['valor']:g} (contribuição {f['contribuicao']:+.2f})")
    print("\n======================================\nRELATÓRIO GERADO\n======================================")
    print(resultado["relatorio"])


def main():
    while True:
        print("\n======================================")
        print("PHISHING WEBSITE DETECTOR")
        print("======================================")
        print("1 - Analisar website\n0 - Sair")
        opcao = input("\nOpção: ").strip()
        if opcao == "1":
            menu_phishing()
        elif opcao == "0":
            break
        else:
            print("\nOpção inválida.")


if __name__ == "__main__":
    main()
