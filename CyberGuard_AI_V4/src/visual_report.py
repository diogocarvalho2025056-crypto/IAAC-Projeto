"""Relatorios HTML locais para IAAC-Projeto.

A fonte dos valores deve ser SEMPRE o dicionario devolvido pelo classificador
Python/XGBoost, nunca um texto gerado pelo LLM.
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
import math
import webbrowser


PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_RELATORIOS = PASTA_PROJETO / "reports"


def _probabilidade(resultado: dict, chave: str) -> float:
    if chave not in resultado:
        raise ValueError(f"Falta o campo obrigatorio '{chave}' no resultado do modelo.")
    valor = float(resultado[chave])
    if not math.isfinite(valor) or not 0 <= valor <= 1:
        raise ValueError(f"Probabilidade invalida para {chave}: {valor}")
    return valor


def _texto(valor: object) -> str:
    return escape(str(valor), quote=True)


def _numero(valor: object, casas: int = 4) -> str:
    try:
        numero = float(valor)
        if not math.isfinite(numero):
            return "—"
        return f"{numero:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    except (TypeError, ValueError):
        return _texto(valor)


def gerar_relatorio_visual(
    resultado: dict,
    tipo_analise: str,
    abrir_browser: bool = True,
) -> Path:
    """Guarda um dashboard HTML a partir dos dados tecnicos reais do classificador.

    Args:
        resultado: resultado de analisar_malware/analisar_ransomware/analisar_phishing.
        tipo_analise: 'Malware', 'Ransomware' ou 'Phishing'.
        abrir_browser: abre o ficheiro local no browser, se True.

    Returns:
        Caminho absoluto do ficheiro HTML criado.
    """
    if not isinstance(resultado, dict) or resultado.get("sucesso") is not True:
        raise ValueError("O modelo nao devolveu um resultado tecnico valido (sucesso=True).")

    tipo = str(tipo_analise).strip().lower()
    configuracao = {
        "malware": ("Malware", "Benigno", "Malware", "probabilidade_benigno", "probabilidade_malware"),
        "ransomware": ("Ransomware", "Benigno", "Ransomware/Malware", "probabilidade_benigno", "probabilidade_malware"),
        "phishing": ("Phishing", "Legítimo", "Phishing", "probabilidade_legitimo", "probabilidade_phishing"),
    }
    if tipo not in configuracao:
        raise ValueError("Tipo desconhecido. Usa Malware, Ransomware ou Phishing.")

    titulo, etiqueta_benigno, etiqueta_ameaca, chave_benigno, chave_ameaca = configuracao[tipo]
    prob_benigno = _probabilidade(resultado, chave_benigno)
    prob_ameaca = _probabilidade(resultado, chave_ameaca)
    confianca = _probabilidade(resultado, "confianca")

    classe = int(resultado.get("classe", -1))
    if classe not in (0, 1):
        raise ValueError(f"Classe inesperada: {classe}")
    ameaca = classe == 1
    cor = "#fb7185" if ameaca else "#22c55e"
    cor_fundo = "rgba(251, 113, 133, .12)" if ameaca else "rgba(34, 197, 94, .12)"
    estado = "Ameaça detetada" if ameaca else "Sem ameaça detetada"
    classificacao = _texto(resultado.get("classificacao", etiqueta_ameaca if ameaca else etiqueta_benigno))
    subtitulo = (
        "Website de phishing" if tipo == "phishing" and ameaca
        else "Website legítimo" if tipo == "phishing"
        else "Amostra suspeita" if ameaca
        else "Amostra benigna"
    )

    # As contribuicoes sao valores numericos da explicacao do modelo, NAO percentagens.
    top_features = resultado.get("top_features", [])
    features_html = ""
    if isinstance(top_features, list) and top_features:
        linhas = []
        for feature in top_features[:8]:
            if not isinstance(feature, dict):
                continue
            nome = _texto(feature.get("feature", "Desconhecida"))
            valor = _numero(feature.get("valor", "—"), 3)
            contrib = _numero(feature.get("contribuicao", "—"), 4)
            linhas.append(
                f'<tr><td class="feature">{nome}</td><td class="num">{valor}</td>'
                f'<td class="num">{contrib}</td></tr>'
            )
        if linhas:
            features_html = (
                '<section class="features"><h2>Principais características da análise</h2>'
                '<div class="table-wrap"><table><thead><tr><th>Feature</th>'
                '<th>Valor</th><th>Contribuição</th></tr></thead><tbody>'
                + "".join(linhas)
                + '</tbody></table></div><p class="note">As contribuições são valores numéricos '
                'da explicação local do modelo; não são percentagens.</p></section>'
            )

    data = datetime.now().astimezone()
    data_texto = _texto(data.strftime("%d/%m/%Y · %H:%M:%S %Z"))
    mensagem = resultado.get("mensagem", "")
    mensagem_html = (
        f'<p class="modelo-mensagem">{_texto(mensagem)}</p>' if mensagem else ""
    )
    p_b = prob_benigno * 100
    p_a = prob_ameaca * 100
    p_conf = confianca * 100

    pagina = f'''<!DOCTYPE html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>IAAC · {_texto(titulo)} · Resultado</title>
  <style>
    :root {{ color-scheme: dark; --fundo:#080b10; --painel:#10151e; --texto:#eef2f7;
      --muted:#a2adbd; --linha:#273142; --benigno:#22c55e; --ameaca:#fb7185; }}
    * {{box-sizing:border-box}}
    body {{background: radial-gradient(ellipse at 90% 0%,#152238 0%,var(--fundo) 48%);
      color:var(--texto);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;
      margin:0;min-height:100vh;padding:42px 20px}}
    main {{max-width:980px;margin:auto}}
    .brand {{letter-spacing:.17em;text-transform:uppercase;color:#9fb5d9;font-size:.76rem;
      font-weight:800;margin-bottom:16px}}
    .card {{background:linear-gradient(145deg,#121925,#0d1119);border:1px solid var(--linha);
      border-radius:21px;padding:30px 32px;box-shadow:0 18px 65px rgba(0,0,0,.28)}}
    .header {{display:flex;justify-content:space-between;align-items:flex-start;gap:15px;
      margin-bottom:28px}}
    h1 {{font-size:clamp(1.32rem,2.3vw,1.8rem);margin:0;font-weight:720;line-height:1.25}}
    h2 {{font-size:1.08rem;margin:0 0 15px}}
    .pill {{white-space:nowrap;color:{cor};background:{cor_fundo};border:1px solid {cor}66;
      border-radius:999px;font-size:.82rem;font-weight:700;padding:6px 13px}}
    .grid {{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin:8px 0 28px}}
    .label {{font-size:.91rem;color:var(--muted);margin-bottom:8px}}
    .big {{font-size:clamp(1.8rem,4vw,2.6rem);font-weight:760;line-height:1.25}}
    .classification {{color:{cor}}}
    .bar-row {{display:flex;justify-content:space-between;align-items:center;gap:10px;
      margin:17px 0 7px;font-size:.95rem}}
    .bar-row strong {{font-size:1.04rem;font-variant-numeric:tabular-nums}}
    .track {{height:14px;border-radius:99px;background:#2a303c;overflow:hidden}}
    .fill {{height:100%;border-radius:99px}}
    .safe {{background:var(--benigno)}} .danger {{background:var(--ameaca)}}
    .features {{margin-top:22px;padding-top:22px;border-top:1px solid var(--linha)}}
    .table-wrap {{overflow-x:auto}}
    table {{border-collapse:collapse;width:100%;font-size:.89rem}}
    th {{color:var(--muted);text-align:left;font-weight:600}}
    td,th {{border-bottom:1px solid #273142;padding:10px 8px}}
    .num {{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
    .feature {{overflow-wrap:anywhere}}
    .note, footer, .modelo-mensagem {{color:var(--muted);font-size:.83rem}}
    .modelo-mensagem {{margin:19px 0 0}}
    footer {{margin-top:20px;display:flex;gap:12px;justify-content:space-between;flex-wrap:wrap}}
    @media(max-width:650px) {{body {{padding:17px 12px}} .card {{padding:22px 17px}}
      .header {{display:block}} .pill {{display:inline-block;margin-top:14px}} .grid {{gap:12px}}}}
    @media print {{:root {{color-scheme:light}} body {{background:white;color:#141414;padding:0}}
      .card {{box-shadow:none;border-color:#ddd;background:white}} .label,.note,footer {{color:#555}}
      .track {{background:#eee}}}}
  </style>
</head>
<body>
  <main>
    <div class="brand">IAAC · Sistema Multiagente · Relatório técnico</div>
    <article class="card">
      <header class="header">
        <h1>{_texto(titulo)} — {_texto(subtitulo)}</h1>
        <span class="pill">{'⚠' if ameaca else '✓'} {_texto(estado)}</span>
      </header>
      <div class="grid">
        <div><div class="label">Classificação</div><div class="big classification">{classificacao}</div></div>
        <div><div class="label">Confiança do modelo</div><div class="big">{_numero(p_conf,2)}%</div></div>
      </div>
      <section aria-label="Probabilidades previstas pelo modelo">
        <div class="bar-row"><span>Probabilidade de {_texto(etiqueta_benigno.lower())}</span>
          <strong>{_numero(p_b,2)}%</strong></div>
        <div class="track"><div class="fill safe" style="width:{p_b:.6f}%"></div></div>
        <div class="bar-row"><span>Probabilidade de {_texto(etiqueta_ameaca.lower())}</span>
          <strong>{_numero(p_a,2)}%</strong></div>
        <div class="track"><div class="fill danger" style="width:{p_a:.6f}%"></div></div>
      </section>
      {features_html}
      {mensagem_html}
    </article>
    <footer><span>Fonte: classificação direta do modelo ML/XGBoost · não do texto do LLM</span>
      <span>{data_texto}</span></footer>
  </main>
</body>
</html>'''

    PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
    # O timestamp evita substituir relatorios anteriores.
    ficheiro = PASTA_RELATORIOS / f"analise_{tipo}_{data.strftime('%Y%m%d_%H%M%S_%f')}.html"
    ficheiro.write_text(pagina, encoding="utf-8")
    if abrir_browser:
        webbrowser.open(ficheiro.resolve().as_uri())
    return ficheiro
