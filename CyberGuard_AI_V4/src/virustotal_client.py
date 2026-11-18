import ipaddress
import os
import re
from base64 import urlsafe_b64encode
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests


def _api_key():
    key = os.getenv("VIRUSTOTAL_API_KEY", "").strip() or os.getenv("VT_API_KEY", "").strip()
    if key:
        return key
    path = Path(__file__).resolve().parents[1] / ".env"
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            name, separator, value = line.partition("=")
            if separator and name.strip() == "VIRUSTOTAL_API_KEY":
                return value.strip().strip('"').strip("'")
    return ""


def _evidencia_ficheiro(atributos):
    evidencia = {}
    classificacao = atributos.get("popular_threat_classification")
    if isinstance(classificacao, dict):
        rotulo = classificacao.get("suggested_threat_label")
        if isinstance(rotulo, str) and re.fullmatch(r"ransomware\.[a-z0-9_./-]{1,120}", rotulo, re.IGNORECASE):
            evidencia["familia_sugerida"] = rotulo.split(".", 1)[1]

    sandboxes = atributos.get("sandbox_verdicts")
    if isinstance(sandboxes, dict):
        vereditos = [
            {"sandbox": nome[:100], "categoria": item["category"]}
            for nome, item in sandboxes.items()
            if isinstance(item, dict) and item.get("category") in
            ("malicious", "suspicious", "harmless", "undetected")
        ]
        if vereditos:
            evidencia["vereditos_sandbox"] = vereditos[:12]
    return evidencia


def _consultar_relatorio(tipo: str, identificador: str) -> dict:
    try:
        api_key = _api_key()
    except (OSError, UnicodeError):
        return {"estado": "configuracao_invalida"}
    if not api_key:
        return {"estado": "sem_configuracao"}

    try:
        resposta = requests.get(
            f"https://www.virustotal.com/api/v3/{tipo}/{identificador}",
            headers={"x-apikey": api_key},
            timeout=5,
            allow_redirects=False,
        )
        if resposta.status_code == 404:
            return {"estado": "sem_registo"}
        if resposta.status_code == 429:
            return {"estado": "limite_api"}

        if resposta.status_code in (401, 403):
            return {"estado": "acesso_negado"}
        if resposta.status_code == 202:
            return {"estado": "pendente"}
        if resposta.status_code != 200:
            return {"estado": "indisponivel"}
        atributos = resposta.json()["data"]["attributes"]
        extras = _evidencia_ficheiro(atributos) if tipo == "files" else {}
        estatisticas = atributos.get("last_analysis_stats")
        if not estatisticas:
            return {"estado": "pendente" if atributos.get("status") in ("queued", "in-progress") else "sem_resultados", **extras}
        counts = {name: estatisticas[name] for name in ("malicious", "suspicious")}
        if any(type(count) is not int or count < 0 for count in counts.values()):
            return {"estado": "indisponivel"}
        data_analise = atributos.get("last_analysis_date")

        return {
            "estado": "encontrado",
            **counts,
            **extras,
            "ultima_analise": (
                datetime.fromtimestamp(data_analise, tz=timezone.utc).date().isoformat()
                if data_analise is not None
                else None
            ),
        }
    except requests.Timeout:
        return {"estado": "timeout"}
    except (requests.RequestException, KeyError, AttributeError, TypeError, ValueError, OverflowError, OSError):
        return {"estado": "indisponivel"}


def consultar_ficheiro(sha256: str | None) -> dict:
    if not sha256:
        return {"estado": "sem_hash"}

    sha256 = sha256.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        return {"estado": "hash_invalido"}

    return _consultar_relatorio("files", sha256)


def consultar_url(url: str | None, autorizar_envio: bool = False) -> dict:
    if not url:
        return {"estado": "sem_url"}

    url = url.strip()
    try:
        partes = urlsplit(url)
        if partes.scheme not in {"http", "https"} or not partes.hostname:
            return {"estado": "url_invalido"}
        if partes.username is not None or partes.password is not None:
            return {"estado": "url_invalido"}
    except ValueError:
        return {"estado": "url_invalido"}

    host = partes.hostname.lower().rstrip(".")
    try:
        public = ipaddress.ip_address(host).is_global
    except ValueError:
        public = bool(re.fullmatch(r"[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,63}", host))
        public = public and host.split(".")[-1] not in {"local", "localhost", "internal", "test", "invalid", "example", "onion", "lan", "corp", "home"}
        public = public and not host.endswith((".home.arpa", ".in-addr.arpa"))
    if not autorizar_envio and (not public or partes.query or partes.fragment):
        return {"estado": "privado"}
    identificador = urlsafe_b64encode(url.encode("utf-8")).decode("ascii").rstrip("=")
    return _consultar_relatorio("urls", identificador)


# Mantém a compatibilidade com chamadas existentes de consulta por SHA-256.
consultar_virustotal = consultar_ficheiro
