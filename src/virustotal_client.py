import os
import re
from base64 import urlsafe_b64encode
from datetime import datetime, timezone
from urllib.parse import urlsplit

import requests


def _consultar_relatorio(tipo: str, identificador: str) -> dict:
    api_key = os.getenv("VT_API_KEY")
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

        resposta.raise_for_status()
        atributos = resposta.json()["data"]["attributes"]
        estatisticas = atributos["last_analysis_stats"]
        data_analise = atributos.get("last_analysis_date")

        return {
            "estado": "encontrado",
            "malicious": estatisticas["malicious"],
            "suspicious": estatisticas["suspicious"],
            "ultima_analise": (
                datetime.fromtimestamp(data_analise, tz=timezone.utc).date().isoformat()
                if data_analise is not None
                else None
            ),
        }
    except (requests.RequestException, KeyError, TypeError, ValueError, OverflowError, OSError):
        return {"estado": "indisponivel"}


def consultar_ficheiro(sha256: str | None) -> dict:
    if not sha256:
        return {"estado": "sem_hash"}

    sha256 = sha256.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        return {"estado": "hash_invalido"}

    return _consultar_relatorio("files", sha256)


def consultar_url(url: str | None) -> dict:
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

    identificador = urlsafe_b64encode(url.encode("utf-8")).decode("ascii").rstrip("=")
    return _consultar_relatorio("urls", identificador)


# Mantém a compatibilidade com chamadas existentes de consulta por SHA-256.
consultar_virustotal = consultar_ficheiro
