"""Reúne os resultados técnicos e descreve a cobertura da análise."""
import json
from concurrent.futures import ThreadPoolExecutor

from backend import service
from backend.real_inputs import MAX_UPLOAD_BYTES

VT_DETAILS = {
    'sem_configuracao': 'Configura VIRUSTOTAL_API_KEY no backend.',
    'configuracao_invalida': 'Não foi possível ler a configuração VirusTotal.',
    'sem_registo': 'O indicador é desconhecido no VirusTotal.',
    'limite_api': 'Quota de consultas VirusTotal atingida.',
    'acesso_negado': 'A API VirusTotal recusou a chave ou o acesso.',
    'pendente': 'O VirusTotal ainda está a processar a análise.',
    'sem_resultados': 'O VirusTotal ainda não apresenta resultados dos motores.',
    'timeout': 'A consulta VirusTotal excedeu o tempo limite.',
    'desativado': 'A consulta de reputação foi desativada para este URL.',
    'privado': 'A consulta de um URL potencialmente privado requer autorização.',
    'url_invalido': 'O URL não está disponível para consulta de reputação.',
    'indisponivel': 'A consulta VirusTotal falhou.',
    'nao_aplicavel': 'O upload contém features. O hash do ficheiro de dados não representa as amostras.',
}


def collect(local, reputation):
    with ThreadPoolExecutor(max_workers=1) as workers:
        remote = workers.submit(reputation)
        result = local()
        vt = remote.result()

    state = vt['estado']
    vt['detalhe'] = VT_DETAILS.get(state)
    result['virustotal'] = vt
    model_ready = bool(result.get('modelo_treinado_utilizado'))
    found = state == 'encontrado'
    verdict = 'Inconclusivo'
    relation = None
    if found and model_ready and result.get('classe') in (0, 1):
        engines_flagged = (vt['malicious'] + vt['suspicious']) > 0
        model_flagged = result['classe'] == 1
        if engines_flagged != model_flagged:
            relation = 'divergencia'
            verdict = 'Fontes divergentes'
        else:
            relation = 'concordancia'
            verdict = 'Indícios de ameaça em ambas as fontes' if model_flagged else 'Sem indícios nas fontes consultadas'
    elif found and (vt['malicious'] or vt['suspicious']):
        verdict = 'Deteções reportadas pelo VirusTotal'
    elif result.get('classe') == 1:
        verdict = 'Indício de ameaça no modelo'

    reasons = []
    if not model_ready and result.get('limitacao'):
        reasons.append(result['limitacao'])
    for index, sample in enumerate(result.get('resultados', []), 1):
        if not sample.get('modelo_treinado_utilizado'):
            reasons.append(f"Amostra {index}: {sample['limitacao']}")
    if vt['detalhe']:
        reasons.append(vt['detalhe'])
    result.update(estado_analise='completa' if model_ready and found else 'parcial',
                  veredito=verdict, relacao_fontes=relation, motivos=reasons,
                  confianca_veredito='Evidência concordante' if relation == 'concordancia' else 'Evidência limitada')
    return result


def behavioral(sha256):
    """Lê um export normalizado da sandbox existente, ligado ao hash do upload."""
    path = service.ROOT / 'runtime' / 'behavior' / f'{sha256}.json'
    evidence = {'estado': 'em_falta', 'origem': 'Export local de sandbox'}
    try:
        with path.open('rb') as stream:
            data = stream.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            raise ValueError('O relatório comportamental excede 12 MiB.')
        report = json.loads(data)
        if not isinstance(report, dict) or report.get('sha256') != sha256:
            raise ValueError('O SHA-256 do relatório não corresponde ao ficheiro.')
        features = service.validate('ransomware', report.get('features'))
    except FileNotFoundError:
        detail = 'Falta um relatório de sandbox com as 165 features do treino para este SHA-256.'
    except (OSError, ValueError, OverflowError) as exc:
        evidence['estado'] = 'incompativel'
        detail = str(exc) if isinstance(exc, ValueError) else 'Não foi possível ler os valores do relatório.'
    else:
        evidence.update(estado='disponivel', numero_features=len(features),
                        observacoes={name: value for name, value in features.items()
                                     if name.startswith(('registry_', 'network_', 'processes_', 'files_'))
                                     or name in {'total_procsses', 'dlls_calls', 'apis'}})
        return features, evidence
    evidence['detalhe'] = detail
    return None, evidence
