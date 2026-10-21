"""Sistema multiagente de cibersegurança — módulo de Ransomware (Tomás Matos).

    python main.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA / "src"))

from orchestrator import processar_pedido  # noqa: E402

DEMO = PASTA / "data" / "processed" / "ransom_demo_samples.csv"   # gerado por models/modeling.py
LIMPO = PASTA / "data" / "processed" / "ransom_cleaned.csv"       # gerado pelo notebook 02
CAMINHO_FEATURES = PASTA / "models" / "ransomware_features.json"
FEATURES = json.loads(CAMINHO_FEATURES.read_text(encoding="utf-8"))
_ROTULOS = {"benign": 0, "benigno": 0, "malware": 1, "0": 0, "1": 1}


def carregar_amostras() -> pd.DataFrame:
    """Amostras do Test Set com as features do modelo + coluna 'Class' (0 = Benigno, 1 = Malware)."""
    if DEMO.exists():
        df = pd.read_csv(DEMO)
    elif LIMPO.exists():
        # Reconstrói o Test Set a partir do dataset limpo (demora alguns segundos)
        from features import prepare_datasets
        from models import split_dataset

        print("A preparar amostras de teste a partir de ransom_cleaned.csv...")
        X, y, _, grupos = prepare_datasets(pd.read_csv(LIMPO), return_groups=True)
        _, _, X_test, _, _, y_test, _ = split_dataset(X, y, grupos, verbose=False)
        df = X_test.copy()
        df["Class"] = y_test
    else:
        sys.exit("Não encontrei ransom_demo_samples.csv nem ransom_cleaned.csv em data/processed/.\n"
                 "Corre primeiro: python models/modeling.py")

    # Class pode vir como 0/1 ou como Benign/Malware
    df["Class"] = df["Class"].astype(str).str.strip().str.lower().map(_ROTULOS)
    if df["Class"].isna().any() or set(df["Class"]) != {0, 1}:
        sys.exit("A coluna 'Class' tem de ter amostras benignas e de malware (0/1 ou Benign/Malware).")
    return df


AMOSTRAS = carregar_amostras()


def obter_amostra(classe: int, indice: int = 0) -> dict:
    """Devolve só as features do modelo (ignora md5, Category, Family, etc., se existirem)."""
    linhas = AMOSTRAS[AMOSTRAS["Class"] == classe]
    em_falta = [f for f in FEATURES if f not in linhas.columns]
    if em_falta:
        sys.exit(f"Faltam {len(em_falta)} features do modelo nas amostras (ex.: {em_falta[:3]}). "
                 "Volta a correr: python models/modeling.py")
    return linhas.iloc[indice % len(linhas)][FEATURES].to_dict()


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