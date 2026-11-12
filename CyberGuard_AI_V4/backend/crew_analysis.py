"""Local CrewAI interpretation of completed defensive analysis results."""
import json
import os
from importlib.util import find_spec
from threading import Lock
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

OLLAMA_URL = 'http://127.0.0.1:11434'
CREW_LOCK = Lock()
DEFAULT_MODEL = 'qwen2.5:3b'


class CrewUnavailable(RuntimeError):
    pass


def model_name():
    return os.environ.get('CYBERGUARD_OLLAMA_MODEL', DEFAULT_MODEL).strip() or DEFAULT_MODEL


def status():
    model = model_name()
    installed = find_spec('crewai') is not None
    try:
        with build_opener(ProxyHandler({})).open(f'{OLLAMA_URL}/api/tags', timeout=2) as response:
            installed_models = json.load(response).get('models', [])
        ready = any(item.get('name') == model for item in installed_models)
    except (OSError, URLError, ValueError):
        return {'ready': False, 'model': model, 'detail': 'Inicia o Ollama em 127.0.0.1:11434.'}
    if not installed:
        return {'ready': False, 'model': model, 'detail': 'Instala as dependências com install.bat.'}
    if not ready:
        return {'ready': False, 'model': model, 'detail': f'Executa ollama pull {model}.'}
    return {'ready': True, 'model': model, 'detail': 'CrewAI e modelo local disponíveis.'}


def evidence(result):
    samples = result.get('resultados') or [result]
    return {
        'tipo': result.get('tipo'),
        'metodo': result.get('modo'),
        'limitacao': result.get('limitacao'),
        'amostras': [
            {
                'amostra': index,
                'classificacao': sample.get('classificacao') if sample.get('modelo_treinado_utilizado') else None,
                'modelo_utilizado': bool(sample.get('modelo_treinado_utilizado')),
                'score_ameaca': sample.get('probabilidade_ameaca'),
                'features_relevantes': sample.get('top_features', []),
            }
            for index, sample in enumerate(samples, 1)
        ],
    }


def interpret(result):
    setup = status()
    if not setup['ready']:
        raise CrewUnavailable(setup['detail'])

    # Set before importing CrewAI so its telemetry sees these defaults.
    os.environ['OTEL_SDK_DISABLED'] = 'true'
    os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'
    os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'true'
    bypass = os.environ.get('no_proxy', os.environ.get('NO_PROXY', '')).split(',')
    bypass = ','.join(dict.fromkeys(host for host in [*bypass, '127.0.0.1', 'localhost'] if host))
    os.environ['NO_PROXY'] = os.environ['no_proxy'] = bypass
    try:
        from crewai import Agent, Crew, LLM, Process, Task

        with CREW_LOCK:
            llm = LLM(model=setup['model'], custom_openai=True,
                      base_url=f'{OLLAMA_URL}/v1', api_key='ollama-local',
                      temperature=0.1, timeout=120, max_tokens=650)
            options = dict(llm=llm, allow_delegation=False, allow_code_execution=False,
                           tools=[], max_iter=2, verbose=False)
            analyst = Agent(role='Analista de evidências', goal='Interpretar resultados de análise defensiva',
                            backstory='Especialista em classificação e limitações de modelos.', **options)
            reviewer = Agent(role='Revisor do relatório', goal='Produzir uma síntese fiel em português de Portugal',
                             backstory='Revisor de relatórios técnicos de segurança defensiva.', **options)
            analysis = Task(
                description='Interpreta os seguintes dados técnicos: {evidencias}. '
                            'Identifica os resultados por amostra, a evidência disponível e as limitações. '
                            'Usa apenas os dados fornecidos e preserva as classificações.',
                expected_output='Notas concisas sobre as evidências e as limitações.',
                agent=analyst,
            )
            review = Task(
                description='Revê as notas do analista à luz dos dados originais: {evidencias}. '
                            'Escreve até 180 palavras em português de Portugal em texto simples. '
                            'Preserva classificações e números. Distingue scores de certezas. '
                            'Se houve apenas inspeção, indica que falta um diagnóstico. '
                            'Inclui recomendações defensivas proporcionais e evita inventar evidências.',
                expected_output='Síntese técnica revista, com limitações e recomendações defensivas.',
                agent=reviewer,
                context=[analysis],
            )
            crew = Crew(agents=[analyst, reviewer], tasks=[analysis, review],
                        process=Process.sequential, memory=False, cache=False,
                        verbose=False, tracing=False)
            output = crew.kickoff(inputs={'evidencias': json.dumps(evidence(result), ensure_ascii=False)})
    except Exception as exc:
        raise CrewUnavailable('A execução CrewAI falhou. Verifica o Ollama e o modelo instalado.') from exc

    summary = output.raw.strip()
    if not summary or len(summary) > 6000:
        raise CrewUnavailable('O CrewAI devolveu uma síntese inválida. Repete a análise.')
    return {'engine': 'CrewAI', 'model': setup['model'],
            'agents': ['Analista de evidências', 'Revisor do relatório'], 'summary': summary}
