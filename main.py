"""Sistema multiagente de cibersegurança — módulo de Ransomware (Tomás Matos).

    python main.py
"""
import sys
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA / "src"))

from orchestrator import processar_pedido  # noqa: E402

AMOSTRAS = pd.read_csv(PASTA / "data" / "processed" / "ransom_demo_samples.csv")  # 10 benignas + 10 malware do Test Set


def obter_amostra(classe: int, indice: int = 0) -> dict:
    linhas = AMOSTRAS[AMOSTRAS["Class"] == classe].drop(columns="Class")
    return linhas.iloc[indice].to_dict()


def menu_ransomware():
    print("\n======================================\nANÁLISE DE RANSOMWARE/MALWARE\n======================================")
    print("1 - Amostra benigna (do Test Set)\n2 - Amostra de malware (do Test Set)")
    opcao = input("\nOpção: ").strip()
    if opcao not in ("1", "2"):
        print("\nOpção inválida.")
        return

    print("\nA processar análise...")
    resposta = processar_pedido("ransomware", obter_amostra(0 if opcao == "1" else 1))
    if not resposta["sucesso"]:
        print("\nErro:\n" + resposta["erro"])
        return

    r = resposta["resultado"]
    print("\n======================================\nRESULTADO TÉCNICO\n======================================")
    print("Classificação:", r["classificacao"])
    print(f"Confiança: {r['confianca'] * 100:.2f}%")
    print(f"Probabilidade Benigno: {r['probabilidade_benigno'] * 100:.2f}%")
    print(f"Probabilidade Malware: {r['probabilidade_malware'] * 100:.2f}%")
    for t in r["top_features"]:
        print(f"  - {t['feature']} = {t['valor']:g} (contribuição {t['contribuicao']:+.2f})")
    print("\n======================================\nRELATÓRIO GERADO\n======================================")
    print(resposta["relatorio"])


def main():
    while True:
        print("\n======================================\nSISTEMA MULTIAGENTE DE CIBERSEGURANÇA\n======================================")
        print("1 - Malware\n2 - Ransomware\n3 - Phishing\n0 - Sair")
        opcao = input("\nOpção: ").strip()
        if opcao == "2":
            menu_ransomware()
        elif opcao in ("1", "3"):
            print("\nEste agente ainda não está integrado neste repositório.")
        elif opcao == "0":
            print("\nA terminar o sistema.")
            break
        else:
            print("\nOpção inválida.")


if __name__ == "__main__":
    main()
