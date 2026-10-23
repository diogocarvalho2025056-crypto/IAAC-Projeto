import pandas as pd
from features import _to_number, clean_and_transform_features, raw_sample_to_features


def test_hex_e_decimal_dao_o_mesmo_valor():
    assert _to_number("0x00008600") == _to_number("34304") == 34304.0


def test_valores_invalidos_viram_nan():
    assert pd.isna(_to_number("abc")) and pd.isna(_to_number(None))


def test_pipeline_devolve_so_numerico_e_sem_target_em_X():
    df = pd.DataFrame({
        "md5": ["a", "b", "c"], "sha1": ["x", "y", "z"], "file_extension": ["exe"] * 3,
        "SizeOfCode": ["0x00008600", "34304", "0x00000010"], "PEType": ["PE32", "PE32+", "PE32"],
        "DllCharacteristics": ["['A', 'B']", "['A']", "[]"], "Class": ["Benign", "Malware", "Malware"],
        "Category": ["Benign", "Trojan", "RAT"], "Family": ["Benign", "f1", "f2"],
    })
    out = clean_and_transform_features(df)
    feats = out.drop(columns=["md5", "Class", "Category", "Family"])
    assert all(pd.api.types.is_numeric_dtype(feats[c]) for c in feats.columns)
    assert "sha1" not in out.columns and "dll_A" in out.columns
    assert out.loc[0, "SizeOfCode"] == out.loc[1, "SizeOfCode"] == 34304


def test_amostra_bruta_alinha_com_lista_de_features():
    feats = ["SizeOfCode", "dll_A", "PEType_PE32", "inexistente"]
    r = raw_sample_to_features({"SizeOfCode": "0x10", "PEType": "PE32", "DllCharacteristics": "['A']"}, feats)
    assert list(r) == feats and r["SizeOfCode"] == 16 and r["dll_A"] == 1 and r["inexistente"] == 0
