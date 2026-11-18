import hashlib
import json
import math
import sqlite3
import threading
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from uuid import uuid4
from contextlib import closing

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = {'malware': 'malware_xgboost.json', 'phishing': 'phishing_xgboost.json', 'ransomware': 'ransomware_model.pkl', 'ransomware_static':'ransomware_static_xgboost.json', 'phishing_url':'phishing_url_xgboost.json'}
LOCK = threading.Lock()


def feature_names(kind):
    if kind not in ARTIFACTS:
        raise ValueError('Tipo de análise desconhecido.')
    return json.loads((ROOT / 'models' / f'{kind}_features.json').read_text(encoding='utf-8'))


@lru_cache(maxsize=5)
def model_identity(kind):
    path = ROOT / 'models' / ARTIFACTS[kind]
    return {'artefacto': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'schema_sha256': hashlib.sha256((ROOT / 'models' / f'{kind}_features.json').read_bytes()).hexdigest()}


@lru_cache(maxsize=5)
def load_model(kind):
    path = ROOT / 'models' / ARTIFACTS[kind]
    if kind == 'ransomware':
        import joblib
        model = joblib.load(path)
    else:
        from xgboost import XGBClassifier
        model = XGBClassifier(n_jobs=1)
        model.load_model(path)
    model.set_params(n_jobs=1)
    expected = feature_names(kind)
    if (kind == 'ransomware' and len(expected) != 165) or model.n_features_in_ != len(expected):
        raise RuntimeError('O modelo e o esquema de features não correspondem.')
    names = getattr(model, 'feature_names_in_', None)
    if names is not None and list(names) != expected:
        raise RuntimeError('A ordem das features do modelo não corresponde ao esquema.')
    if list(model.classes_) != [0, 1]:
        raise RuntimeError('Classes inesperadas no modelo.')
    if kind == 'ransomware' and (names is None or
                                 set(model.get_booster().feature_types or []) != {'int', 'float'}):
        raise RuntimeError('O artefacto comportamental não fornece o esquema de tipos esperado.')
    return model


def validate(kind, sample):
    names = feature_names(kind)
    if not isinstance(sample, dict) or set(sample) != set(names):
        missing = [n for n in names if not isinstance(sample, dict) or n not in sample]
        extra = [n for n in sample if n not in names] if isinstance(sample, dict) else []
        raise ValueError(f'Esquema inválido. Em falta: {missing[:8]}; extra: {extra[:8]}.')
    output = {}
    for n in names:
        value = sample[n]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f'{n}: é necessário um número finito.')
        if kind in ('phishing','phishing_url') and value not in (-1, 0, 1):
            raise ValueError(f'{n}: os valores permitidos são -1, 0 e 1.')
        output[n] = value if kind == "ransomware" else float(value)
    return output


def predict(kind, sample):
    import pandas as pd
    values = validate(kind, sample)
    model = load_model(kind)
    names = feature_names(kind)
    if kind == 'ransomware':
        for name, dtype in zip(names, model.get_booster().feature_types, strict=True):
            value = values[name]
            if dtype == 'int' and value % 1:
                raise ValueError(f'{name}: o modelo comportamental requer um valor inteiro.')
            values[name] = int(value) if dtype == 'int' else float(value)
    frame = pd.DataFrame([values], columns=names)
    p = model.predict_proba(frame)[0]
    label = int(model.predict(frame)[0])
    names = ('Legítimo', 'Phishing') if kind in ('phishing','phishing_url') else (('Não ransomware', 'Ransomware') if kind == 'ransomware_static' else ('Benigno', 'Malware'))
    top = []
    try:
        from xgboost import DMatrix
        contrib = model.get_booster().predict(DMatrix(frame), pred_contribs=True)[0][:-1]
        for i in sorted(range(len(contrib)), key=lambda i: abs(contrib[i]), reverse=True)[:5]:
            name = frame.columns[i]
            top.append({'feature': name, 'valor': values[name], 'contribuicao': float(contrib[i])})
    except Exception:
        pass
    return {'classificacao': names[label], 'classe': label, 'confianca': float(p[label]),
            'probabilidade_ameaca': float(p[1]), 'modelo_treinado_utilizado': True,
            'top_features': top, 'features': values, 'modelo': model_identity(kind),
            'nota': 'A probabilidade do modelo não é uma garantia de segurança nem uma probabilidade calibrada.'}


def database():
    folder = ROOT / 'runtime'
    folder.mkdir(exist_ok=True)
    db = sqlite3.connect(folder / 'history.sqlite3', timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, payload TEXT NOT NULL)')
    return db


def save(result):
    result = dict(result, versao='5.0.0', id=uuid4().hex, created_at=datetime.now(timezone.utc).isoformat())
    with LOCK, closing(database()) as db, db:
        db.execute('INSERT INTO analyses VALUES (?, ?, ?)', (result['id'], result['created_at'], json.dumps(result, ensure_ascii=False, allow_nan=False)))
    return result


def history():
    with closing(database()) as db:
        rows = db.execute('SELECT payload FROM analyses ORDER BY created_at DESC LIMIT 50').fetchall()
    return [{k: v for k, v in json.loads(row[0]).items() if k not in ('features', 'top_features', 'resultados')} for row in rows]


def report(identifier):
    with closing(database()) as db:
        row = db.execute('SELECT payload FROM analyses WHERE id = ?', (identifier,)).fetchone()
    return json.loads(row[0]) if row else None


def model_status():
    results = []
    for kind, filename in ARTIFACTS.items():
        path = ROOT / 'models' / filename
        item = {'tipo': kind, 'features': None, 'disponivel': path.is_file(), 'carregado': False}
        try:
            item['features'] = len(feature_names(kind))
            load_model(kind)
            item['carregado'] = True
        except Exception as exc:
            item['erro'] = f'{type(exc).__name__}: {exc}'
        if path.is_file():
            item['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        results.append(item)
    return results
