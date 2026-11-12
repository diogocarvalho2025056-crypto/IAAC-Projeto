import hashlib
import json
import time
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from backend.html_report import render_report
from fastapi.staticfiles import StaticFiles

from backend import crew_analysis, service
from backend.pe_features import extract_pe
from backend.real_inputs import MAX_UPLOAD_BYTES, inspect_url, inspect_file, parse_feature_file
from backend.ransomware_static import extract as extract_ransomware
from backend.phishing_url import extract as extract_phishing_url

app = FastAPI(title='CyberGuard AI V4', version='4.0.0')
app.mount('/static', StaticFiles(directory=service.ROOT / 'frontend'), name='static')


@app.middleware('http')
async def local_boundary(request: Request, call_next):
    host = request.headers.get('host', '').split(':')[0].lower()
    if host not in ('localhost', '127.0.0.1', 'testserver'):
        return JSONResponse({'detail': 'Esta versão está limitada ao computador local.'}, status_code=403)
    if request.method == 'POST':
        origin = request.headers.get('origin')
        if origin and origin not in ('http://localhost:8000', 'http://127.0.0.1:8000'):
            return JSONResponse({'detail': 'Origem do pedido não autorizada.'}, status_code=403)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    if 'Content-Security-Policy' not in response.headers:
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    return response


@app.exception_handler(ValueError)
async def invalid_input(request, exc):
    return JSONResponse({'detail': str(exc)}, status_code=422)


@app.get('/')
def home():
    return FileResponse(service.ROOT / 'frontend' / 'index.html')


@app.get('/api/models')
def models():
    return {'models': service.model_status(), 'versao': '4.0.0'}


@app.get('/api/crew/status')
def crew_status():
    return crew_analysis.status()


def finish_analysis(result):
    try:
        result['crewai'] = crew_analysis.interpret(result)
    except crew_analysis.CrewUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    return service.save(result)


@app.get('/api/schema/{kind}')
def schema(kind: str):
    return {'tipo': kind, 'features': service.feature_names(kind), 'dominio': [-1, 0, 1] if kind in ('phishing','phishing_url') else 'números finitos'}


@app.get('/api/history')
def history():
    return {'items': service.history()}


@app.get('/api/reports/{identifier}')
def download(identifier: str):
    item = service.report(identifier)
    if item is None:
        raise HTTPException(404, 'Análise não encontrada.')
    return JSONResponse(item, headers={'Content-Disposition': f'attachment; filename="analise-{item["id"]}.json"'})


@app.get('/api/reports/{identifier}/html')
def html_report(identifier: str, download: bool = True):
    item = service.report(identifier)
    if item is None:
        raise HTTPException(404, 'Análise não encontrada.')
    headers = {'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; script-src 'none'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'"}
    if download:
        headers['Content-Disposition'] = f'attachment; filename="analise-{item["id"]}.html"'
    return HTMLResponse(render_report(item),headers=headers)


@app.post('/api/analyze/upload/{kind}')
async def upload(kind: str, file: UploadFile = File(...)):
    names = service.feature_names(kind)
    try:
        data = await file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        await file.close()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, 'O limite é 12 MiB por ficheiro.')
    if not data:
        raise ValueError('O ficheiro está vazio.')
    suffix = Path(file.filename or '').suffix.lower()
    started = time.perf_counter()
    def analyze():
        if suffix in ('.csv', '.json'):
            rows = parse_feature_file(data, suffix, names)
            results = [service.predict(kind, row) for row in rows]
            result = dict(results[0]) if len(results) == 1 else {
                'classificacao': f'{len(results)} amostras analisadas', 'resultados': results,
                'modelo_treinado_utilizado': True,
            }
            result.update(modo='features_estruturadas', numero_amostras=len(results))
        elif kind in ('malware', 'ransomware_static') and not data.startswith(b'MZ'):
            result = inspect_file(data, file.filename or 'ficheiro', kind)
            result['limitacao'] = 'Formato sem classificador treinado nesta versão. Inspeção estática sem diagnóstico de infeção.'
        elif kind in ('malware', 'ransomware_static'):
            features = extract_pe(data) if kind == 'malware' else extract_ransomware(data)
            result = service.predict(kind, features)
            result.update(modo='pe_estatico', extrator='pe-v1',
                          validacao_externa=False,
                          limitacao='Inferência real. A equivalência do extrator com o extrator original do dataset ainda exige validação pareada.')
        elif kind == 'ransomware':
            raise ValueError('O modelo atual requer 165 features, incluindo comportamento de sandbox. Envia CSV/JSON completo. Não identifica a família ransomware.')
        else:
            raise ValueError('Para este modelo de phishing, envia CSV/JSON com as 30 features. Para um URL, usa Triagem de URL.')
        result.update(tipo=kind, sha256=hashlib.sha256(data).hexdigest(), tamanho_bytes=len(data),
                      tempo_ms=round((time.perf_counter() - started) * 1000, 2))
        if kind == 'ransomware':
            result['limitacao'] = 'Este classificador distingue benigno de malware em geral; não identifica ransomware especificamente.'
        if kind == 'ransomware_static' and result.get('modelo_treinado_utilizado'):
            result['limitacao'] = 'Não ransomware pode incluir outros malwares. Modelo estático de demonstração: recall interno de teste 63,96%; sem validação externa pareada do extrator.'
        return finish_analysis(result)
    try:
        return await run_in_threadpool(analyze)
    except (ValueError, HTTPException):
        raise
    except Exception as exc:
        raise HTTPException(503, 'Não foi possível executar o modelo. Consulta o estado dos modelos e as dependências.') from exc


@app.post('/api/analyze/url')
async def url(request: Request):
    body = await request.body()
    if len(body) > 8192:
        raise HTTPException(413, 'Pedido demasiado grande.')
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeError):
        raise ValueError('JSON inválido.')
    if not isinstance(payload, dict):
        raise ValueError('É necessário um objeto JSON com o URL.')
    def analyze():
        features = extract_phishing_url(payload.get('url'))
        result = service.predict('phishing_url', features)
        result.update(tipo='phishing_url', modo='modelo_phishing_url',
                      limitacao='Modelo lexical com 7 features. Sem HTML, reputação ou validação externa pareada. Legítimo não garante segurança.')
        return finish_analysis(result)
    return await run_in_threadpool(analyze)
