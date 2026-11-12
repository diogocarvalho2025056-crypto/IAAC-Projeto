"""Tests for the Web API using stub inference modules (no model artifacts redistributed)."""
import importlib
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def setup_core(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "models").mkdir()
    (tmp_path / "dataset").mkdir()
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "reports").mkdir()
    configs = {
        "malware": ("models/malware_xgboost.json", "dataset/Malware_prepared.csv", "Malicious", "0", "1"),
        "phishing": ("models/phishing_xgboost.json", "dataset/phishing_prepared.csv", "class", "1", "-1"),
        "ransomware": ("models/ransomware_model.pkl", "data/processed/ransom_cleaned.csv", "Class", "Benign", "Malware"),
    }
    for kind, (artifact, csv, target, benign, threat) in configs.items():
        (tmp_path / artifact).write_text("stub")
        (tmp_path / "models" / f"{kind}_features.json").write_text(json.dumps(["f1", "f2"]))
        (tmp_path / csv).write_text(f"f1,f2,{target}\n1,2,{benign}\n7,8,{threat}\n")
        (tmp_path / "src" / f"{kind}_inference.py").write_text(
            f"def prever_{kind}(sample):\n"
            "    assert set(sample)=={'f1','f2'}\n"
            "    return {'sucesso': True, 'classificacao': 'AMOSTRA TESTE', 'confianca': 0.95}\n")


@pytest.fixture
def api(tmp_path, monkeypatch):
    setup_core(tmp_path)
    overlay_path = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.syspath_prepend(str(overlay_path))
    monkeypatch.setenv("CYBERGUARD_CORE_PATH", str(tmp_path))
    monkeypatch.delenv("CYBERGUARD_WEB_USER", raising=False)
    monkeypatch.delenv("CYBERGUARD_WEB_PASSWORD", raising=False)
    for name in list(sys.modules):
        if name == "src" or name.startswith("src.") or name.startswith("backend"):
            del sys.modules[name]
    mod = importlib.import_module("backend.app")
    mod.ollama_status = lambda: {"online": False, "models": [], "default_model": "qwen3.5:9b"}
    with TestClient(mod.app) as client:
        yield client, tmp_path


def test_dashboard_and_health(api):
    client, _ = api
    assert client.get("/").status_code == 200
    health = client.get("/api/health").json()
    assert all(value["files_available"] for value in health["models"].values())
    assert health["ollama"]["online"] is False


@pytest.mark.parametrize("kind", ["malware", "phishing", "ransomware"])
@pytest.mark.parametrize("label", ["benign", "threat"])
def test_samples_and_inference(api, kind, label):
    client, core = api
    example = client.get(f"/api/samples/{kind}/{label}")
    assert example.status_code == 200, example.text
    assert set(example.json()["amostra"]) == {"f1", "f2"}
    response = client.post(f"/api/analyze/{kind}", json=example.json()["amostra"])
    assert response.status_code == 200, response.text
    assert response.json()["classificacao"] == "AMOSTRA TESTE"
    assert response.json()["analysis_id"]
    assert (core / "reports" / "web_history.json").is_file()


def test_direct_sample_api(api):
    client, _ = api
    response = client.post("/api/analyze/phishing/sample/threat")
    assert response.status_code == 200
    assert response.json()["tipo"] == "phishing"


def test_validation_and_report_path_traversal(api):
    client, _ = api
    assert client.post("/api/analyze/malware", json=[1, 2]).status_code == 422
    assert client.post("/api/analyze/unknown", json={"f1": 1}).status_code == 404
    assert client.post("/api/analyze/malware", content=b'not-json').status_code == 400
    assert client.get("/api/reports/not-a-report.html").status_code == 400
    assert client.post("/api/assistant", json={"prompt": "test"}).status_code == 503


def test_basic_auth_enabled(api, monkeypatch):
    client, _ = api
    monkeypatch.setenv("CYBERGUARD_WEB_USER", "investigador")
    monkeypatch.setenv("CYBERGUARD_WEB_PASSWORD", "secret-long-password")
    assert client.get("/api/health").status_code == 401
    assert client.get("/api/health", auth=("investigador", "secret-long-password")).status_code == 200


def test_dashboard_has_real_file_and_url_controls(api):
    client, _ = api
    page = client.get('/').text
    assert 'Arrasta o ficheiro para aqui' in page
    assert 'id="target-url"' in page
    assert 'id="load-benign"' not in page
    assert 'id="load-threat"' not in page


def test_real_binary_upload_inspects_without_ml(api):
    client, core = api
    payload = b'MZ' + b'\x00' * 40 + b'vssadmin delete shadows' + b'\x00' * 300
    response = client.post('/api/analyze/upload/malware', files={
        'file': ('ficheiro.exe', payload, 'application/octet-stream'),
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['modelo_treinado_utilizado'] is False
    assert data['modo'] == 'inspecao_estatica'
    assert data['formato_identificado'].startswith('Executável')
    assert len(data['sha256']) == 64
    assert data['indicadores_observados']
    assert b'vssadmin' not in (core/'reports'/'web_history.json').read_bytes()


@pytest.mark.parametrize('kind', ['malware','ransomware','phishing'])
def test_real_csv_features_use_model(api, kind):
    client, core = api
    response = client.post(f'/api/analyze/upload/{kind}', files={
        'file': ('medidas.csv', b'f1,f2\n7,8\n', 'text/csv'),
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['modo'] == 'modelo_treinado'
    assert data['modelo_treinado_utilizado'] is True
    assert data['numero_amostras'] == 1
    assert data['resultados'][0]['classificacao'] == 'AMOSTRA TESTE'


def test_json_features_uploaded(api):
    client, _ = api
    r = client.post('/api/analyze/upload/phishing', files={
        'file': ('amostra.json', b'{"f1":1,"f2":2}', 'application/json'),
    })
    assert r.status_code == 200, r.text
    assert r.json()['modelo_treinado_utilizado'] is True


def test_uploaded_csv_missing_feature_rejected(api):
    client, _ = api
    response = client.post('/api/analyze/upload/malware', files={
        'file': ('bad.csv', b'f1\n1\n', 'text/csv'),
    })
    assert response.status_code == 422
    assert 'f2' in response.json()['detail']


def test_raw_url_triage_without_model(api):
    client, core = api
    r = client.post('/api/analyze/url', json={'url':'http://127.0.0.1/verify/account'})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data['modo'] == 'triagem_url_local'
    assert data['tipo'] == 'phishing'
    assert not data['modelo_treinado_utilizado']
    assert data['total_indicadores'] >= 2
    assert '127.0.0.1' not in (core/'reports'/'web_history.json').read_text()


def test_url_unsupported_protocol_rejected(api):
    client, _ = api
    for url in ('file:///etc/passwd', 'javascript:alert(1)', 'http://:80/', 'https://test.com:invalid'):
        r = client.post('/api/analyze/url', json={'url': url})
        assert r.status_code == 422, (url, r.text)


def test_file_limit(api):
    client, _ = api
    r = client.post('/api/analyze/upload/ransomware', files={
        'file': ('large.pdf', b'X' * (12 * 1024 * 1024 + 1), 'application/pdf'),
    })
    assert r.status_code == 413
