import hashlib
import logging
import json
import time
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from backend.html_report import render_report
from fastapi.staticfiles import StaticFiles

from backend import crew_analysis, evidence, service
from src.virustotal_client import consultar_ficheiro, consultar_url
from backend.pe_features import extract_pe
from backend.real_inputs import MAX_UPLOAD_BYTES, inspect_file, parse_feature_file
from backend.ransomware_static import extract as extract_ransomware
from backend.phishing_url import extract as extract_phishing_url

app = FastAPI(title='CyberGuard AI V5', version='5.0.0')
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
    return {'models': service.model_status(), 'versao': '5.0.0'}


@app.get('/api/crew/status')
def crew_status():
    return crew_analysis.status()


def finish_analysis(result):
    try:
        result['crewai'] = crew_analysis.interpret(result)
    except crew_analysis.CrewUnavailable as exc:
        result["crewai"] = {"estado": "indisponivel", "summary": str(exc)}
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


def unavailable(detail):
    return {'classificacao': 'Não determinada', 'modelo_treinado_utilizado': False,
            'limitacao': detail}


def infer(kind, features):
    try:
        return service.predict(kind, features)
    except ValueError as exc:
        return unavailable(str(exc))
    except Exception:
        logging.getLogger(__name__).exception('Falha na inferência de %s', kind)
        return unavailable('O modelo treinado está indisponível. Consulta o estado dos modelos.')


@app.post('/api/analyze/upload/{kind}')
async def upload(kind: str, file: UploadFile = File(...), features_file: Annotated[bool | None, Form()] = None):
    if kind not in service.ARTIFACTS:
        raise ValueError('Tipo de análise desconhecido.')
    try:
        data = await file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        await file.close()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, 'O limite é 12 MiB por ficheiro.')
    if not data:
        raise ValueError('O ficheiro está vazio.')
    filename = file.filename or 'ficheiro'
    suffix = Path(filename).suffix.lower()
    structured = features_file if features_file is not None else suffix in ('.csv', '.json')
    started = time.perf_counter()
    sha256 = hashlib.sha256(data).hexdigest()

    def local():
        if structured:
            try:
                rows = parse_feature_file(data, suffix, service.feature_names(kind))
            except (ValueError, OSError) as exc:
                result = unavailable(str(exc) if isinstance(exc, ValueError) else 'Esquema de features indisponível.')
                return dict(result, modo='features_estruturadas')
            results = [infer(kind, row) for row in rows]
            result = dict(results[0]) if len(results) == 1 else {
                'classificacao': f'{len(results)} amostras analisadas', 'resultados': results,
                'modelo_treinado_utilizado': all(item['modelo_treinado_utilizado'] for item in results),
            }
            if kind == 'ransomware':
                result['comportamento'] = {'estado': 'fornecido', 'origem': 'Features fornecidas pelo utilizador',
                                           'detalhe': 'A proveniência da telemetria não foi verificada.'}
            return dict(result, modo='features_estruturadas', numero_amostras=len(results))

        inspection = inspect_file(data, filename, kind)
        if kind == 'ransomware':
            features, behavior = evidence.behavioral(sha256)
            if features is None:
                result = unavailable(behavior['detalhe'])
                return dict(inspection, **result, comportamento=behavior)
            result = infer(kind, features)
            if result['modelo_treinado_utilizado']:
                result['limitacao'] = 'O modelo distingue benigno de malware em geral.'
            elif result['limitacao'].endswith('requer um valor inteiro.'):
                behavior.update(estado='incompativel', detalhe=result['limitacao'])
            return dict(result, modo='sandbox_export', comportamento=behavior,
                        indicadores_observados=inspection['indicadores_observados'])
        if kind in ('malware', 'ransomware_static') and data.startswith(b'MZ'):
            try:
                extractor = extract_pe if kind == 'malware' else extract_ransomware
                features = extractor(data)
            except ValueError as exc:
                return dict(inspection, limitacao=str(exc))
            result = infer(kind, features)
            if result['modelo_treinado_utilizado']:
                result['limitacao'] = 'Análise estática. A equivalência com a extração do dataset original ainda requer validação pareada.'
            return dict(result, modo='pe_estatico', extrator='pe-v1', validacao_externa=False,
                        indicadores_observados=inspection['indicadores_observados'])
        return dict(inspection, limitacao='Formato sem classificador compatível para esta opção.')

    def reputation():
        return {'estado': 'nao_aplicavel'} if structured else consultar_ficheiro(sha256)

    def analyze():
        result = evidence.collect(local, reputation)
        result.update(tipo=kind, sha256=sha256, tamanho_bytes=len(data),
                      tempo_ms=round((time.perf_counter() - started) * 1000, 2))
        return finish_analysis(result)

    return await run_in_threadpool(analyze)


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
    features = extract_phishing_url(payload.get('url'))

    def local():
        result = infer('phishing_url', features)
        if result['modelo_treinado_utilizado']:
            result['limitacao'] = 'Modelo lexical de 7 features. A equivalência do extrator com os dados de treino ainda não tem validação pareada.'
        return result

    def reputation():
        if payload.get('consultar_virustotal') is False:
            return {'estado': 'desativado'}
        return consultar_url(payload['url'], payload.get('autorizar_consulta_privada') is True)

    def analyze():
        result = evidence.collect(local, reputation)
        result.update(tipo='phishing_url', modo='modelo_phishing_url')
        return finish_analysis(result)
    return await run_in_threadpool(analyze)
