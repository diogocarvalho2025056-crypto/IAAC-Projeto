"""CyberGuard AI — dashboard e API para os modelos originais do IAAC.

Os módulos src/ e crewai_version/ mantêm-se intactos. As funcionalidades
ML pressupõem o projeto IAAC presente na raiz (ou CYBERGUARD_CORE_PATH).
"""
from __future__ import annotations

import importlib
import json
import os
import re
import secrets
import sys
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.real_inputs import MAX_UPLOAD_BYTES, inspect_file, inspect_url, parse_feature_file

WEB_ROOT = Path(__file__).resolve().parents[1]
ROOT_CANDIDATES = [
    Path(os.environ.get("CYBERGUARD_CORE_PATH", WEB_ROOT)),
    WEB_ROOT,
    WEB_ROOT.parent / "ProjetoIAAC-main",
    WEB_ROOT.parent / "IAAC-Projeto",
]
CORE = next((p.resolve() for p in ROOT_CANDIDATES if (p / "src").is_dir()),
            ROOT_CANDIDATES[0].resolve())
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

REPORTS = CORE / "reports"
HISTORY = REPORTS / "web_history.json"
OLLAMA_URL = os.environ.get("CYBERGUARD_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("CYBERGUARD_OLLAMA_MODEL", "qwen3.5:9b")
HISTORY_LOCK = threading.Lock()
CREW_LOCK = threading.Lock()

MODEL_CONFIG = {
    "malware": {
        "label": "Malware", "module": "src.malware_inference", "predictor": "prever_malware",
        "artifacts": ["models/malware_xgboost.json", "models/malware_features.json"],
        "dataset": "dataset/Malware_prepared.csv", "target": "Malicious",
        "benign_labels": {"0"}, "threat_labels": {"1"},
    },
    "ransomware": {
        "label": "Ransomware", "module": "src.ransomware_inference", "predictor": "prever_ransomware",
        "artifacts": ["models/ransomware_model.pkl", "models/ransomware_features.json"],
        "dataset": "data/processed/ransom_cleaned.csv", "target": "Class",
        "benign_labels": {"benign", "normal", "0", "non-ransomware"},
        "threat_labels": {"malware", "ransomware", "1"},
    },
    "phishing": {
        "label": "Phishing", "module": "src.phishing_inference", "predictor": "prever_phishing",
        "artifacts": ["models/phishing_xgboost.json", "models/phishing_features.json"],
        "dataset": "dataset/phishing_prepared.csv", "target": "class",
        "benign_labels": {"1"}, "threat_labels": {"-1"},
    },
}

app = FastAPI(title="CyberGuard AI", description="Dashboard integrado IAAC", version="1.0.0")
app.mount("/static", StaticFiles(directory=WEB_ROOT / "frontend" / "static"), name="static")
templates = Jinja2Templates(directory=WEB_ROOT / "frontend" / "templates")


@app.middleware("http")
async def basic_auth_if_enabled(request: Request, call_next):
    """HTTP Basic opcional para acesso em LAN; configurar ambas as variáveis.

    O utilizador local (127.0.0.1) pode operar sem Basic Auth, mas o script
    run-lan.bat impede acesso externo sem credenciais configuradas.
    """
    expected_user = os.environ.get("CYBERGUARD_WEB_USER", "")
    expected_password = os.environ.get("CYBERGUARD_WEB_PASSWORD", "")
    if not expected_user or not expected_password:
        return await call_next(request)

    import base64
    credentials = request.headers.get("authorization", "")
    authorized = False
    if credentials.lower().startswith("basic "):
        try:
            raw = base64.b64decode(credentials[6:], validate=True).decode("utf-8")
            supplied_user, supplied_password = raw.split(":", 1)
            authorized = (secrets.compare_digest(supplied_user, expected_user)
                          and secrets.compare_digest(supplied_password, expected_password))
        except Exception:
            authorized = False
    if not authorized:
        return JSONResponse({"detail": "Autenticação necessária"}, status_code=401,
                            headers={"WWW-Authenticate": 'Basic realm="CyberGuard AI"'})
    return await call_next(request)


def _require_kind(kind: str) -> dict:
    if kind not in MODEL_CONFIG:
        raise HTTPException(404, "Módulo não encontrado. Escolhe malware, ransomware ou phishing.")
    return MODEL_CONFIG[kind]


def model_status() -> dict:
    statuses = {}
    for kind, spec in MODEL_CONFIG.items():
        missing = [name for name in spec["artifacts"] if not (CORE / name).is_file()]
        statuses[kind] = {
            "label": spec["label"], "files_available": not missing,
            "missing": missing, "source_present": (CORE / "src" / f"{kind}_inference.py").is_file(),
            "dataset_available": (CORE / spec["dataset"]).is_file(),
        }
    return statuses


def crew_status() -> dict:
    # Presence check only: a working CrewAI execution also needs installed dependencies and Ollama.
    import importlib.util
    return {
        "files_present": (CORE / "crewai_version" / "crew.py").is_file(),
        "package_installed": importlib.util.find_spec("crewai") is not None,
    }


def ollama_status() -> dict:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as response:
            data = json.load(response)
        models = [model.get("name", "") for model in data.get("models", [])]
        return {"online": True, "models": models, "default_model": OLLAMA_MODEL}
    except (OSError, ValueError, urllib.error.URLError):
        return {"online": False, "models": [], "default_model": OLLAMA_MODEL}


def reports_summary() -> dict:
    REPORTS.mkdir(exist_ok=True, parents=True)
    counts = {k: 0 for k in MODEL_CONFIG}
    files = []
    for path in REPORTS.glob("analise_*.html"):
        match = re.fullmatch(r"analise_(malware|ransomware|phishing)_[\w-]+\.html", path.name)
        if not match or not path.is_file():
            continue
        counts[match[1]] += 1
        files.append(path)
    recent = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:8]
    return {"total": len(files), "by_type": counts,
            "recent": [{"filename": p.name,
                        "type": p.name.split("_")[1],
                        "modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%d/%m/%Y %H:%M")}
                       for p in recent]}


def read_history(limit: int = 50) -> list[dict]:
    try:
        data = json.loads(HISTORY.read_text(encoding="utf-8"))
        return data[:limit] if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def record_history(item: dict) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    with HISTORY_LOCK:
        items = read_history(500)
        items.insert(0, item)
        temporary = HISTORY.with_suffix(".tmp")
        temporary.write_text(json.dumps(items[:500], ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(HISTORY)


def make_json_safe(value):
    """Converte scalars e vetores NumPy usados pelos modelos para JSON normal."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if -float("inf") < value < float("inf") else None
    if isinstance(value, dict):
        return {str(k): make_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [make_json_safe(v) for v in value]
    if hasattr(value, "item"):
        try:
            return make_json_safe(value.item())
        except (ValueError, TypeError):
            pass
    if hasattr(value, "tolist"):
        return make_json_safe(value.tolist())
    return str(value)


def predictor_for(kind: str):
    spec = _require_kind(kind)
    try:
        module = importlib.import_module(spec["module"])
        return getattr(module, spec["predictor"])
    except Exception as error:
        raise HTTPException(
            503, f"Não foi possível importar {spec['module']}.{spec['predictor']}: "
                 f"{type(error).__name__}: {error}") from error


def predict(kind: str, sample: dict, origin: str = "json") -> dict:
    spec = _require_kind(kind)
    if not isinstance(sample, dict) or not sample:
        raise HTTPException(422, "Envia um objeto JSON com as features do modelo.")
    missing = [name for name in spec["artifacts"] if not (CORE / name).is_file()]
    if missing:
        raise HTTPException(503, f"Modelo {kind} incompleto. Em falta: {', '.join(missing)}")
    predictor = predictor_for(kind)
    started = perf_counter()
    try:
        result = predictor(sample)
    except Exception as error:
        raise HTTPException(500, f"Falha na inferência {kind}: {type(error).__name__}: {error}") from error
    duration_ms = round((perf_counter() - started) * 1000, 2)
    if not isinstance(result, dict):
        raise HTTPException(502, "O classificador devolveu um resultado inesperado.")
    result = make_json_safe(result)
    if result.get("sucesso") is False:
        raise HTTPException(422, str(result.get("erro", "A amostra foi rejeitada pelo modelo.")))
    result.update({"tipo": kind, "tempo_ms": duration_ms})
    analysis_id = uuid4().hex[:12]
    record_history({
        "id": analysis_id, "created_at": datetime.now(timezone.utc).isoformat(),
        "tipo": kind, "origem": origin,
        "classificacao": result.get("classificacao", result.get("predicao", "Concluída")),
        "confianca": result.get("confianca"), "tempo_ms": duration_ms,
    })
    result["analysis_id"] = analysis_id
    return result


def _feature_names(kind: str) -> list[str] | None:
    path = CORE / "models" / f"{kind}_features.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if isinstance(value, dict):
        for candidate in ("features", "feature_names", "columns", "colunas", "selected_features"):
            if candidate in value:
                value = value[candidate]
                break
    return value if isinstance(value, list) and all(isinstance(x, str) for x in value) else None


def example_from_dataset(kind: str, label: str) -> dict:
    spec = _require_kind(kind)
    if label not in {"benign", "threat"}:
        raise HTTPException(400, "Exemplo inválido. Escolhe benign ou threat.")
    path = CORE / spec["dataset"]
    if not path.is_file():
        raise HTTPException(404, f"Dataset não encontrado: {spec['dataset']}")
    try:
        import pandas as pd
        frame = pd.read_csv(path)
        target = spec["target"]
        if target not in frame.columns:
            raise HTTPException(422, f"Dataset sem coluna '{target}'.")
        normalized = frame[target].astype(str).str.strip().str.lower()
        valid = spec["benign_labels"] if label == "benign" else spec["threat_labels"]
        rows = frame[normalized.isin(valid)]
        if rows.empty:
            raise HTTPException(404, f"Sem amostras '{label}' no dataset (classes: {normalized.unique()[:8].tolist()}).")
        row = rows.iloc[0]
        original_class = make_json_safe(row[target])
        features = _feature_names(kind)
        if features:
            missing = [name for name in features if name not in frame.columns]
            if missing:
                raise HTTPException(422, f"Features em falta no dataset: {missing[:8]}")
            sample = {name: make_json_safe(row[name]) for name in features}
        else:
            excluded = {"class", "malicious", "category", "family", "md5", "sha256", "filename", "file_name"}
            sample = {name: make_json_safe(row[name]) for name in frame.columns if name.lower() not in excluded}
        return {"tipo": kind, "label": label, "classe_dataset": original_class, "amostra": sample}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(500, f"Erro a carregar exemplo: {type(error).__name__}: {error}") from error


def _read_json_request_sync(data: bytes) -> dict:
    if len(data) > 128 * 1024:
        raise HTTPException(413, "Pedido demasiado grande (limite 128 KiB).")
    try:
        value = json.loads(data)
    except (ValueError, UnicodeDecodeError) as error:
        raise HTTPException(400, "O corpo do pedido deve ser JSON válido.") from error
    if not isinstance(value, dict):
        raise HTTPException(422, "O JSON deve ser um objeto.")
    return value


@app.post('/api/analyze/upload/{kind}')
async def analyze_upload(kind: str, file: UploadFile = File(...)):
    """Accept a REAL file. CSV/JSON feature matrices use the trained IAAC
    classifiers; raw binaries are inspected offline, NEVER executed or
    inaccurately passed to classifiers expecting unrelated training features.
    """
    _require_kind(kind)
    filename = Path((file.filename or 'ficheiro').replace('\\', '/')).name[:150]
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    await file.close()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f'O tamanho máximo por ficheiro é {MAX_UPLOAD_BYTES // (1024 * 1024)} MiB.')
    if not data:
        raise HTTPException(422, 'O ficheiro está vazio.')
    extension = Path(filename).suffix.lower()
    if extension in ('.json', '.csv'):
        try:
            rows = await run_in_threadpool(parse_feature_file, data, extension, _feature_names(kind))
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        results = []
        for row in rows:
            results.append(await run_in_threadpool(predict, kind, row, 'ficheiro_csv_json'))
        return {
            'sucesso': True, 'tipo': kind, 'modo': 'modelo_treinado',
            'modelo_treinado_utilizado': True, 'numero_amostras': len(results),
            'classificacao': results[0].get('classificacao', 'Classificação concluída')
                if len(results) == 1 else f'{len(results)} amostras analisadas',
            'resultados': results,
            'nota': 'Classificação real com features do mesmo esquema usado no treino do modelo IAAC.',
        }
    result = await run_in_threadpool(inspect_file, data, filename, kind)
    record_history({
        'id': uuid4().hex[:12], 'created_at': datetime.now(timezone.utc).isoformat(),
        'tipo': kind, 'origem': 'ficheiro_real', 'classificacao': result['classificacao'],
        'confianca': None, 'tempo_ms': None,
    })
    return result


@app.post('/api/analyze/url')
async def analyze_real_url(request: Request):
    payload = _read_json_request_sync(await request.body())
    try:
        result = await run_in_threadpool(inspect_url, payload.get('url'))
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    record_history({
        'id': uuid4().hex[:12], 'created_at': datetime.now(timezone.utc).isoformat(),
        'tipo': 'phishing', 'origem': 'url_real', 'classificacao': result['classificacao'],
        'confianca': None, 'tempo_ms': None,
    })
    return result


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "models": model_status(), "reports": reports_summary(),
        "ollama": await run_in_threadpool(ollama_status), "crew": crew_status(),
    })


@app.get("/api/health")
async def health():
    return {"application": "online", "core_present": (CORE / "src").is_dir(),
            "models": model_status(), "ollama": await run_in_threadpool(ollama_status),
            "crewai": crew_status()}


@app.get("/api/dashboard")
async def dashboard_data():
    return {"reports": reports_summary(), "models": model_status(), "recent_web_analyses": read_history(10)}


@app.get("/api/models")
async def models():
    return {"models": model_status(), "ollama": await run_in_threadpool(ollama_status), "crewai": crew_status()}


@app.get("/api/samples/{kind}/{label}")
async def sample(kind: str, label: str):
    return await run_in_threadpool(example_from_dataset, kind, label)


@app.post("/api/analyze/{kind}")
async def analyze(kind: str, request: Request):
    _require_kind(kind)
    sample_data = _read_json_request_sync(await request.body())
    return await run_in_threadpool(predict, kind, sample_data)


@app.post("/api/analyze/{kind}/sample/{label}")
async def analyze_example(kind: str, label: str):
    example = await run_in_threadpool(example_from_dataset, kind, label)
    return await run_in_threadpool(predict, kind, example["amostra"], "dataset")


@app.get("/api/history")
async def history(limit: int = 50):
    return {"items": read_history(min(500, max(1, limit)))}


@app.get("/api/reports/{filename}")
async def report_file(filename: str):
    if not re.fullmatch(r"analise_(malware|ransomware|phishing)_[\w-]+\.html", filename):
        raise HTTPException(400, "Nome de relatório inválido.")
    path = REPORTS / filename
    if not path.is_file():
        raise HTTPException(404, "Relatório não encontrado.")
    # Entregar como anexo em vez de interpretar HTML não confiável no domínio da API.
    return FileResponse(path, media_type="text/html", filename=filename,
                        content_disposition_type="attachment")


@app.post("/api/assistant")
async def assistant(request: Request):
    payload = _read_json_request_sync(await request.body())
    prompt = payload.get("prompt")
    model = payload.get("model", OLLAMA_MODEL)
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 4000:
        raise HTTPException(422, "O prompt deve ter entre 1 e 4000 caracteres.")
    if not isinstance(model, str) or not model or len(model) > 120:
        raise HTTPException(422, "Modelo Ollama inválido.")

    def query_ollama():
        status = ollama_status()
        if not status["online"]:
            raise HTTPException(503, "Ollama não está acessível no PC servidor.")
        if model not in status["models"]:
            raise HTTPException(422, "O modelo não está instalado no Ollama.")
        body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
        req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=body,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                result = json.load(response)
            return {"sucesso": True, "modelo": model, "resposta": result.get("response", "")}
        except (OSError, ValueError, urllib.error.URLError) as error:
            raise HTTPException(502, f"Erro de comunicação com Ollama: {type(error).__name__}: {error}") from error
    return await run_in_threadpool(query_ollama)


@app.post("/api/agents/{kind}")
async def agent_analysis(kind: str, request: Request):
    """Ponte opcional para o CrewAI presente no projeto IAAC.

    As tools atuais usam estado global para passar amostras; serializar os pedidos
    evita sobreposição acidental de execuções simultâneas dentro deste processo.
    """
    _require_kind(kind)
    sample_data = _read_json_request_sync(await request.body())
    status = crew_status()
    if not status["files_present"] or not status["package_installed"]:
        raise HTTPException(503, "CrewAI ainda não está instalado/configurado neste ambiente.")

    def run_crew():
        with CREW_LOCK:
            try:
                from crewai_version.crew import criar_crew
                from crewai_version import crew as crew_module
                tools_module = importlib.import_module(f"crewai_version.tools.{kind}_tool")
                define = getattr(tools_module, f"definir_amostra_{kind}")
                read = getattr(tools_module, f"obter_ultimo_resultado_{kind}")
                task = getattr(crew_module, f"criar_task_{kind}")
                define(sample_data)
                text = str(criar_crew(task()).kickoff())
                technical = read()
                if not technical:
                    raise RuntimeError("O agente não produziu um resultado técnico validado.")
                return {"sucesso": True, "tipo": kind,
                        "resultado_tecnico": make_json_safe(technical), "explicacao": text}
            except Exception as error:
                raise HTTPException(502, f"Falha ao executar CrewAI: {type(error).__name__}: {error}") from error
    return await run_in_threadpool(run_crew)
