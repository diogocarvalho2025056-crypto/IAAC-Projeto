"""Standalone reports styled after the user's original IAAC HTML reports."""
import math
from html import escape
from datetime import datetime

CSS = '''
:root{color-scheme:dark;--bg:#080b10;--text:#eef2f7;--muted:#a2adbd;--line:#273142;--safe:#22c55e;--danger:#fb7185}*{box-sizing:border-box}body{background:radial-gradient(ellipse at 90% 0%,#152238 0%,var(--bg) 48%);color:var(--text);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;min-height:100vh;padding:42px 20px}main{max-width:980px;margin:auto}.brand{letter-spacing:.17em;text-transform:uppercase;color:#9fb5d9;font-size:.76rem;font-weight:800;margin-bottom:16px}.card{background:linear-gradient(145deg,#121925,#0d1119);border:1px solid var(--line);border-radius:21px;padding:30px 32px;margin-bottom:22px;box-shadow:0 18px 65px #0004}.header{display:flex;justify-content:space-between;align-items:flex-start;gap:15px;margin-bottom:28px}h1{font-size:clamp(1.32rem,2.3vw,1.8rem);margin:0;line-height:1.25}h2{font-size:1.08rem;margin:0 0 15px}.pill{border:1px solid currentColor;border-radius:999px;font-size:.82rem;font-weight:700;padding:6px 13px;white-space:nowrap}.grid{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin:8px 0 28px}.label{font-size:.91rem;color:var(--muted);margin-bottom:8px}.big{font-size:clamp(1.8rem,4vw,2.6rem);font-weight:760;line-height:1.25}.threat{color:var(--danger)}.negative{color:var(--safe)}.neutral{color:#f4c56d}.bar-row{display:flex;justify-content:space-between;gap:10px;margin:17px 0 7px}.track{height:14px;border-radius:99px;background:#2a303c;overflow:hidden}.fill{height:100%;border-radius:99px}.safe{background:var(--safe)}.danger{background:var(--danger)}section{margin-top:22px;padding-top:22px;border-top:1px solid var(--line)}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.89rem}th{color:var(--muted);text-align:left;font-weight:600}td,th{border-bottom:1px solid var(--line);padding:10px 8px}.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}td,dd{overflow-wrap:anywhere}.note,footer{color:var(--muted);font-size:.83rem}dl{display:grid;grid-template-columns:150px 1fr;gap:8px;font-size:.83rem}dt{color:var(--muted)}dd{margin:0}footer{margin-top:20px;display:flex;gap:12px;justify-content:space-between;flex-wrap:wrap}li{margin:8px 0}@media(max-width:650px){body{padding:17px 12px}.card{padding:22px 17px}.header{display:block}.pill{display:inline-block;margin-top:14px}.grid{grid-template-columns:1fr;gap:14px}dl{grid-template-columns:1fr}}@media print{:root{color-scheme:light;--text:#141414;--muted:#555;--line:#ddd;--safe:#16803e;--danger:#ad213a}body{background:white;color:#141414;padding:0}.card{box-shadow:none;background:white;border-color:#ddd}.track{background:#eee}section,tr{break-inside:avoid}.brand{color:#334155}}
'''
LABELS = {'malware':'Malware','phishing':'Phishing','phishing_url':'Phishing de URL',
          'ransomware':'Malware comportamental','ransomware_static':'Ransomware estático'}

def text(value):
    return escape(str(value if value is not None else 'Não disponível'),quote=True)

def numeric(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def number(value,digits=3):
    return f'{value:.{digits}f}'.replace('.',',') if numeric(value) else text(value)

def details(fields):
    return '<dl>'+''.join(f'<dt>{text(k)}</dt><dd>{text(v)}</dd>' for k,v in fields if v is not None)+'</dl>'

def card(item,kind,index=None):
    ml=item.get('modelo_treinado_utilizado') is True
    label=item.get('classe')
    css='threat' if ml and label==1 else ('negative' if ml and label==0 else 'neutral')
    badge='Classe ameaça prevista' if ml and label==1 else ('Classe negativa prevista' if ml and label==0 else 'Resultado inconclusivo')
    title=LABELS.get(kind,kind)+(f' · Amostra {index}' if index else '')
    confidence=item.get('confianca')
    score=number(confidence*100,2)+'%' if ml and numeric(confidence) else 'Não aplicável'
    out=f'<article class="card"><header class="header"><h1>{text(title)}</h1><span class="pill {css}">{badge}</span></header><div class="grid"><div><div class="label">Classificação</div><div class="big {css}">{text(item.get("classificacao"))}</div></div><div><div class="label">Confiança do modelo nesta previsão</div><div class="big">{score}</div></div></div>'
    p=item.get('probabilidade_ameaca')
    if ml and numeric(p) and 0<=p<=1:
        negative='Legítimo' if kind.startswith('phishing') else ('Não ransomware' if kind=='ransomware_static' else 'Benigno')
        positive='Phishing' if kind.startswith('phishing') else ('Ransomware' if kind=='ransomware_static' else 'Malware')
        out+='<section aria-label="Scores previstos pelo modelo">'
        for name,value,color in [(negative,1-p,'safe'),(positive,p,'danger')]:
            out+=f'<div class="bar-row"><span>Score de {name.lower()}</span><strong>{number(value*100,2)}%</strong></div><div class="track"><div class="fill {color}" style="width:{value*100:.6f}%"></div></div>'
        out+='<p class="note">Scores do classificador, sem calibração demonstrada. Não representam a precisão global do sistema.</p></section>'
    out+='<section><h2>Principais características da análise</h2>'
    features=item.get('top_features') or []
    if features:
        out+='<div class="table-wrap"><table><thead><tr><th>Feature</th><th class="num">Valor</th><th class="num">Contribuição SHAP</th></tr></thead><tbody>'
        for f in features:
            out+=f'<tr><td>{text(f.get("feature"))}</td><td class="num">{number(f.get("valor"))}</td><td class="num">{number(f.get("contribuicao"),4)}</td></tr>'
        out+='</tbody></table></div><p class="note">Contribuições locais: valores positivos favorecem a classe ameaça; negativos favorecem a classe negativa. Não são percentagens nem provas isoladas de infeção.</p>'
    else:
        out+='<p class="note">Contribuições locais não disponíveis nesta análise. Não são inventadas explicações.</p>'
    out+='</section>'
    if item.get('indicadores_observados'):
        out+='<section><h2>Indicadores observados</h2><ul>'+''.join(f'<li>{text(i)}</li>' for i in item['indicadores_observados'])+'</ul></section>'
    if not ml:
        recommendation='A inspeção não produziu uma classificação de malware. Encaminhar para uma análise compatível com o formato antes de tomar uma decisão.'
    elif label==1 and kind.startswith('phishing'):
        recommendation='O modelo prevê phishing. Evitar introduzir credenciais ou descarregar conteúdo; confirmar o endereço através de um canal oficial independente.'
    elif label==1:
        recommendation='O modelo prevê uma ameaça. Não executar o ficheiro e encaminhar para análise num ambiente isolado. O resultado não prova que o computador esteja infetado.'
    elif kind=='ransomware_static':
        recommendation='A classe não ransomware também inclui outros tipos de malware. Complementar com a análise de malware; este resultado não garante segurança.'
    else:
        recommendation='O modelo prevê a classe negativa. A ausência de deteção não garante segurança; manter a verificação de origem e análise complementar quando necessário.'
    out+='<section><h2>Interpretação e recomendações</h2><p>'+recommendation+'</p>'
    if item.get('nota'):
        out+=f'<p class="note">{text(item["nota"])}</p>'
    if item.get('limitacao'):
        out+=f'<p class="note"><strong>Limitações:</strong> {text(item["limitacao"])}</p>'
    out+='</section>'
    if item.get('features'):
        out+='<section><h2>Features utilizadas</h2><div class="table-wrap"><table><thead><tr><th>Feature</th><th class="num">Valor</th></tr></thead><tbody>'+''.join(f'<tr><td>{text(k)}</td><td class="num">{number(v)}</td></tr>' for k,v in item['features'].items())+'</tbody></table></div></section>'
    model=item.get('modelo') or {}
    out+='<section><h2>Rastreabilidade técnica</h2>'+details([('Método',item.get('modo')),('Modelo',model.get('artefacto')),('SHA-256 do modelo',model.get('sha256')),('SHA-256 do esquema',model.get('schema_sha256'))])+'</section></article>'
    return out

def render_report(item):
    kind=str(item.get('tipo','Análise'))
    created=item.get('created_at','Não disponível')
    try:
        created=datetime.fromisoformat(created).strftime('%d/%m/%Y · %H:%M:%S %z')
    except (ValueError,TypeError):
        pass
    samples=item.get('resultados')
    cards=''.join(card(dict(s,modo=item.get('modo'),limitacao=s.get('limitacao',item.get('limitacao'))),kind,i+1) for i,s in enumerate(samples)) if samples else card(item,kind)
    crew=item.get('crewai')
    if crew:
        cards += ('<article class="card"><h2>Síntese CrewAI</h2>'
                  '<p style="white-space:pre-wrap">'+text(crew['summary'])+'</p>'
                  +details([('Modelo local',crew['model']),('Agentes',', '.join(crew['agents']))])
                  +'</article>')
    meta=[('Identificador',item.get('id')),('Data',created),('Versão',item.get('versao')),('SHA-256 do upload',item.get('sha256')),('Tamanho (bytes)',item.get('tamanho_bytes'))]
    return '<!doctype html><html lang="pt-PT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CyberGuard AI · Relatório técnico</title><style>'+CSS+'</style></head><body><main><div class="brand">IAAC · CyberGuard AI · Relatório técnico</div>'+cards+'<article class="card"><h2>Identificação da análise</h2>'+details(meta)+'</article><footer><span>Fonte da classificação: resultados técnicos registados.</span><span>Imprimir ou guardar como PDF: Ctrl+P no browser.</span></footer></main></body></html>'
