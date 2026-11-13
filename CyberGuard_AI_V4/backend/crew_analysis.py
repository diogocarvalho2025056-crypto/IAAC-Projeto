"""Local CrewAI interpretation of completed defensive analysis results."""
import json
import logging
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
    try:
        import httpx
        from crewai import Agent, Crew, Process, Task
        from crewai.llms.base_llm import BaseLLM

        with CREW_LOCK, httpx.Client(trust_env=False, timeout=120) as client:
            class LocalOllama(BaseLLM):
                def call(self, messages, **kwargs):
                    if isinstance(messages, str):
                        messages = [{'role': 'user', 'content': messages}]
                    response = client.post(f'{OLLAMA_URL}/api/chat', json={
                        'model': self.model, 'messages': messages, 'stream': False,
                        'options': {'temperature': 0.1, 'num_ctx': 2048, 'num_predict': 250},
                    })
                    response.raise_for_status()
                    return response.json()['message']['content']

            llm = LocalOllama(model=setup['model'])
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
                            'Avalia se os indicadores justificam revisão manual adicional. '
                            'Responde apenas com REVER ou SEM_REVISAO.',
                expected_output='Uma única opção: REVER ou SEM_REVISAO.',
                agent=reviewer,
                context=[analysis],
            )
            crew = Crew(agents=[analyst, reviewer], tasks=[analysis, review],
                        process=Process.sequential, memory=False, cache=False,
                        verbose=False, tracing=False)
            output = crew.kickoff(inputs={'evidencias': json.dumps(evidence(result), ensure_ascii=False)})
    except Exception as exc:
        logging.getLogger(__name__).exception('Falha na execução local do CrewAI')
        raise CrewUnavailable('A execução CrewAI falhou. Verifica o Ollama e o modelo instalado.') from exc

    summary = report_summary(result, output.raw)
    return {'engine': 'CrewAI', 'model': setup['model'],
            'agents': ['Analista de evidências', 'Revisor do relatório'], 'summary': summary}


def report_summary(result, review_output):
    lines = []
    samples = evidence(result)['amostras']
    for sample in samples:
        prefix = f"Amostra {sample['amostra']}. " if len(samples) > 1 else ''
        if not sample['modelo_utilizado']:
            lines.append(prefix + 'A inspeção não produziu uma classificação por modelo.')
            continue
        line = prefix + f"Classificação do modelo: {sample['classificacao']}."
        score = sample['score_ameaca']
        if isinstance(score, (int, float)) and 0 <= score <= 1:
            percentage = f'{score:.2%}'.replace('.', ',')
            line += f' Pontuação atribuída à classe de ameaça: {percentage}.'
        lines.append(line)
    if any(sample['modelo_utilizado'] for sample in samples):
        lines.append('A pontuação refere-se à entrada analisada e não é uma probabilidade calibrada.')
    if result.get('limitacao'):
        lines.append(result['limitacao'])
    if review_output.strip().upper() == 'REVER':
        lines.append('Recomenda-se revisão manual dos indicadores antes de tomar uma decisão.')
    return '\n'.join(lines)
