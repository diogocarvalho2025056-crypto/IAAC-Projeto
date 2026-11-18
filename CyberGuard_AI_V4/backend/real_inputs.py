"""Real-input triage: safe, non-executing local file/URL inspections.

These functions DO NOT replace the IAAC classifiers, which expect trained,
structured feature vectors. No uploaded binaries are executed or persisted.
No URL requests, DNS resolutions or remote content downloads are performed.
"""
from __future__ import annotations

import csv
import hashlib
import io
import ipaddress
import json
import math
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

MAX_UPLOAD_BYTES = 12 * 1024 * 1024
MAX_STRUCTURED_ROWS = 10


def _format(data: bytes, filename: str) -> str:
    if data[:2] == b'MZ':
        return 'Executável PE/DOS (MZ)'
    if data[:4] == b'\x7fELF':
        return 'Executável ELF'
    if data.startswith(b'%PDF-'):
        return 'Documento PDF'
    if data.startswith(b'PK\x03\x04'):
        return 'ZIP / Office Open XML / ficheiro comprimido'
    if data.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
        return 'Documento Office binário/OLE'
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'Imagem PNG'
    if data.startswith(b'\xff\xd8\xff'):
        return 'Imagem JPEG'
    if data.startswith(b'#!'):
        return 'Script de texto'
    if filename.lower().endswith('.eml'):
        return 'Mensagem de correio EML'
    if b'\0' not in data[:4096]:
        try:
            data[:4096].decode('utf-8')
            return 'Ficheiro de texto / dados'
        except UnicodeDecodeError:
            pass
    return 'Formato não identificado'


def inspect_file(data: bytes, filename: str, kind: str) -> dict:
    if not data:
        raise ValueError('O ficheiro está vazio.')
    filename = Path(filename.replace('\\', '/')).name[:150] or 'ficheiro'
    total = len(data)
    frequencies = Counter(data)
    entropy = -sum((n / total) * math.log2(n / total) for n in frequencies.values())
    indicators = []
    lowered = data.lower()
    patterns = (
        (b'powershell -enc', 'Referência a PowerShell com argumento de codificação'),
        (b'vssadmin delete shadows', 'Referência a remoção de cópias de sombra'),
        (b'wbadmin delete catalog', 'Referência a remoção de catálogo de backups'),
        (b'createremotethread', 'Referência a uma API usada na criação de threads remotas'),
        (b'virtualallocex', 'Referência a uma API de alocação de memória noutro processo'),
        (b'vbaProject.bin'.lower(), 'Referência a projeto VBA/macros'),
        (b'/javascript', 'Referência a JavaScript em documento PDF'),
        (b'/openaction', 'Referência a ação automática em documento PDF'),
    )
    for needle, note in patterns:
        if needle in lowered:
            indicators.append(note)
    if entropy >= 7.6 and total >= 4096:
        indicators.append('Entropia elevada: pode resultar de compressão, encriptação ou dados normais')
    return {
        'sucesso': True,
        'modo': 'inspecao_estatica',
        'tipo': kind,
        'classificacao': 'Não determinada — inspeção estática',
        'modelo_treinado_utilizado': False,
        'ficheiro': filename,
        'extensao': Path(filename).suffix.lower(),
        'formato_identificado': _format(data, filename),
        'tamanho_bytes': total,
        'sha256': hashlib.sha256(data).hexdigest(),
        'entropia_bits_por_byte': round(entropy, 3),
        'indicadores_observados': indicators,
        'nota': ('O ficheiro foi inspecionado sem ser executado. Os classificadores IAAC '
                 'usam features do treino e não podem classificar automaticamente este '
                 'ficheiro bruto. Os indicadores não provam benignidade nem infeção.'),
    }


def inspect_url(value: str) -> dict:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise ValueError('Indica um URL com até 4096 caracteres.')
    value = value.strip()
    if any(ord(ch) < 32 or ch.isspace() for ch in value):
        raise ValueError('O URL contém espaços ou caracteres inválidos.')
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in ('http', 'https') or not parsed.hostname:
            raise ValueError('O URL tem de começar por http:// ou https:// e incluir um domínio.')
        host = parsed.hostname.lower().rstrip('.')
        port = parsed.port  # May raise ValueError for malformed port.
        if len(host) > 253 or not host:
            raise ValueError('Domínio inválido.')
    except (ValueError, UnicodeError) as exc:
        raise ValueError(f'URL inválido: {exc}') from exc

    flags = []
    if parsed.scheme.lower() != 'https':
        flags.append('Ligação HTTP, sem HTTPS no URL')
    try:
        ipaddress.ip_address(host.strip('[]'))
        flags.append('O URL usa um endereço IP em vez de um domínio')
    except ValueError:
        pass
    if parsed.username is not None or parsed.password is not None:
        flags.append('Contém credenciais ou símbolo @ antes do domínio')
    if 'xn--' in host:
        flags.append('O domínio usa Punycode (verificar possível imitação visual)')
    if len(value) > 120:
        flags.append('URL muito longo')
    if host.count('.') >= 4:
        flags.append('Domínio com vários subdomínios')
    if host.count('-') >= 3:
        flags.append('Domínio com muitos hífenes')
    if '%' in parsed.path or '%' in parsed.query:
        flags.append('O URL contém caracteres codificados em percentagem')
    shorteners = {'bit.ly', 'tinyurl.com', 't.co', 'is.gd', 'cutt.ly', 'ow.ly', 'rb.gy'}
    if host in shorteners:
        flags.append('Domínio habitual de encurtamento de links')
    if port is not None and port not in (80, 443):
        flags.append('Porta não habitual no URL')
    terms = ('login', 'verify', 'verification', 'password', 'reset', 'signin', 'wallet', 'account-update')
    if any(term in (parsed.path + '?' + parsed.query + ' ' + host).lower() for term in terms):
        flags.append('Contém termos associados a páginas de autenticação/contas')
    return {
        'sucesso': True,
        'modo': 'triagem_url_local',
        'tipo': 'phishing',
        'classificacao': 'Sinais para revisão' if flags else 'Sem sinais lexicais evidentes',
        'modelo_treinado_utilizado': False,
        'dominio': host,
        'esquema': parsed.scheme.lower(),
        'comprimento_url': len(value),
        'indicadores_observados': flags,
        'total_indicadores': len(flags),
        'nota': ('Análise lexical local do URL. O servidor não visita o endereço, não faz DNS '
                 'e não introduz as 30 features exigidas pelo modelo IAAC de Phishing. '
                 'Sem sinais não significa que o site seja seguro.'),
    }


def parse_feature_file(data: bytes, extension: str, required_features: list[str] | None) -> list[dict]:
    if not required_features:
        raise ValueError('Lista de features do modelo não disponível. Confirma models/*_features.json.')
    if extension == '.json':
        try:
            raw = json.loads(data.decode('utf-8-sig'))
        except (UnicodeError, ValueError) as exc:
            raise ValueError('O ficheiro JSON não é válido em UTF-8.') from exc
        samples = raw if isinstance(raw, list) else [raw]
    elif extension == '.csv':
        try:
            decoded = data.decode('utf-8-sig')
        except UnicodeError as exc:
            raise ValueError('O ficheiro CSV deve estar codificado em UTF-8.') from exc
        reader = csv.DictReader(io.StringIO(decoded))
        if not reader.fieldnames:
            raise ValueError('O CSV não tem cabeçalho.')
        samples = []
        for row in reader:
            samples.append(row)
            if len(samples) > MAX_STRUCTURED_ROWS:
                break
    else:
        raise ValueError('Usa CSV ou JSON para amostras com features.')
    if not samples or len(samples) > MAX_STRUCTURED_ROWS:
        raise ValueError(f'O ficheiro deve conter entre 1 e {MAX_STRUCTURED_ROWS} amostras.')
    output = []
    for i, raw in enumerate(samples, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f'A amostra {i} deve ser um objeto JSON ou linha CSV.')
        missing = [name for name in required_features if name not in raw or raw[name] in ('', None)]
        if missing:
            raise ValueError(f'Amostra {i}: faltam {len(missing)} features. Exemplos: {", ".join(missing[:6])}.')
        sample = {}
        for name in required_features:
            original = raw[name]
            if isinstance(original, bool):
                raise ValueError(f'Amostra {i}: a feature {name} deve ser numérica.')
            try:
                number = float(original)
            except (ValueError, TypeError, OverflowError) as exc:
                raise ValueError(f'Amostra {i}: a feature {name} não é numérica.') from exc
            if not math.isfinite(number):
                raise ValueError(f'Amostra {i}: a feature {name} não é finita.')
            sample[name] = number
        output.append(sample)
    return output
