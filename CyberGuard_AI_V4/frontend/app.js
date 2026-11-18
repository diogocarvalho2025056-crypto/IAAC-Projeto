const $ = id => document.getElementById(id);
const notes = {
  ransomware_static: 'EXE/DLL: extração de 16 features estáticas e modelo específico de ransomware. Não executa o ficheiro. Não ransomware pode incluir outros malwares.',
  malware: 'EXE/DLL: extração de 23 features e inferência XGBoost. Extrator experimental, ainda sem validação pareada contra o dataset original. Também aceita CSV/JSON.',
  ransomware: 'Para um ficheiro, procura um relatório de sandbox associado ao SHA-256. Também aceita CSV/JSON com as 165 features. O modelo distingue benigno de malware em geral.',
  phishing: 'Apenas CSV/JSON com as 30 features codificadas em −1, 0 e 1. Para endereços reais, usa Triagem de URL.',
};
let busy = false;
async function api(path, options) {
  const response = await fetch(path, options);
  const value = await response.json();
  if (!response.ok) throw new Error(value.detail || 'Não foi possível concluir o pedido.');
  return value;
}
function node(tag, text, cls) {
  const el = document.createElement(tag); el.textContent = text; if (cls) el.className = cls; return el;
}
function message(text, error = false) { $('message').textContent = text; $('message').className = error ? 'error' : ''; }
function kindChanged() { $('kind-note').textContent = notes[$('kind').value]; $('schema-link').href = `/api/schema/${$('kind').value}`; }
function showResult(data) {
  $('result').hidden = false;
  $('verdict').textContent = data.veredito || data.classificacao;
  $('result-mode').textContent = data.estado_analise ? 'Análise ' + data.estado_analise : 'Resultado';
  $('probability').replaceChildren();
  if (typeof data.probabilidade_ameaca === 'number') {
    $('probability').append(node('span', `${(data.probabilidade_ameaca * 100).toFixed(1)}%`), node('small', 'SCORE DA CLASSE AMEAÇA'));
  }
  $('result-note').textContent = data.nota || '';
  $('limitation').textContent = data.limitacao || '';
  $('evidence').replaceChildren();
  if (data.confianca_veredito) {
    $('evidence').append(node('p', 'Confiança no veredito · ' + data.confianca_veredito));
  }
  $('evidence').append(node('h3', 'Modelo treinado'), node('p', data.classificacao));
  for (const reason of data.motivos || []) {
    if (reason !== data.limitacao && reason !== data.virustotal?.detalhe) $('evidence').append(node('p', reason));
  }
  if (data.comportamento) {
    const behavior = data.comportamento;
    $('evidence').append(node('h3', 'Evidência comportamental'), node('p', behavior.origem + ' · ' + (behavior.detalhe || (behavior.numero_features + ' features validadas'))));
    for (const [name, value] of Object.entries(behavior.observacoes || {})) {
      $('evidence').append(node('div', name + ' = ' + value, 'evidence-row'));
    }
  }
  for (const item of data.top_features || []) {
    const row = node('div', '', 'evidence-row');
    row.append(node('span', `${item.feature} = ${item.valor}`), node('span', `SHAP ${item.contribuicao > 0 ? '+' : ''}${item.contribuicao.toFixed(3)}`));
    $('evidence').append(row);
  }
  for (const item of data.indicadores_observados || []) $('evidence').append(node('div', item, 'evidence-row'));
  for (const [i, item] of (data.resultados || []).entries()) $('evidence').append(node('div', `Amostra ${i + 1}: ${item.classificacao}${typeof item.probabilidade_ameaca === 'number' ? ' · score ameaça ' + (item.probabilidade_ameaca * 100).toFixed(1) + '%' : ''}`, 'evidence-row'));
  $('result-meta').textContent = data.sha256 ? `SHA-256 ${data.sha256}` : 'Sem acesso ao endereço remoto';
  if (data.virustotal) {
    const vt = data.virustotal;
    const status = {
      sem_configuracao: 'Consulta por configurar.',
      sem_registo: 'Sem relatório para este indicador.',
      limite_api: 'Limite de consultas atingido.',
    };
    const detail = vt.estado === 'encontrado'
      ? `${vt.malicious} deteções maliciosas, ${vt.suspicious} suspeitas.`
      : vt.detalhe || status[vt.estado] || 'Consulta indisponível.';
    $('evidence').append(node('h3', 'VirusTotal'), node('p', detail));
    if (vt.familia_sugerida) $('evidence').append(node('p', 'Família sugerida pelo VirusTotal · ' + vt.familia_sugerida));
    for (const verdict of vt.vereditos_sandbox || []) {
      $('evidence').append(node('p', 'Sandbox via VirusTotal · ' + verdict.sandbox + ' · ' + verdict.categoria));
    }
  }
  if (data.crewai) {
    $('evidence').append(node('h3', 'Síntese CrewAI'), node('p', data.crewai.summary));
  }
  $('download').href = `/api/reports/${data.id}/html`;
  $('download').textContent = 'Descarregar relatório HTML';
  let links = $('report-links');
  if (!links) { links=node('span',''); links.id='report-links'; $('download').parentElement.append(links); }
  links.replaceChildren();
  const preview=node('a','Abrir relatório'); preview.href=`/api/reports/${data.id}/html?download=false`; preview.target='_blank'; preview.rel='noopener';
  const raw=node('a','JSON'); raw.href=`/api/reports/${data.id}`;
  links.append(preview,document.createTextNode(' · '),raw);
}
async function run(work) {
  if (busy) return; busy = true; message('A analisar e a preparar a síntese com CrewAI…'); $('result').hidden = true;
  document.querySelectorAll('button[type=submit]').forEach(b => b.disabled = true);
  try { showResult(await work()); message('Análise concluída e registada.'); await loadHistory(); }
  catch (error) { message(error.message, true); }
  finally { busy = false; document.querySelectorAll('button[type=submit]').forEach(b => b.disabled = false); }
}
async function loadModels() {
  try {
    const data = await api('/api/models'); $('modelos').replaceChildren();
    for (const m of data.models) {
      const card = node('article', '', 'model');
      const label = {malware:'Malware PE',ransomware:'Malware comportamental',phishing:'Phishing completo',ransomware_static:'Ransomware estático',phishing_url:'Phishing de URL'}[m.tipo];
      card.append(node('span', m.carregado ? '● Modelo carregado' : '○ Indisponível', `state ${m.carregado ? '' : 'error'}`), node('h3', label), node('small', `${m.features} features · XGBoost`), node('p', m.erro || 'Artefacto carregado e esquema confirmado.'));
      $('modelos').append(card);
    }
  } catch (e) { $('modelos').replaceChildren(node('p', `Não foi possível verificar os modelos: ${e.message}`)); }
}
async function loadHistory() {
  try {
    const data = await api('/api/history'); $('history').replaceChildren();
    if (!data.items.length) { const tr = node('tr', ''); const td = node('td', 'Ainda não há análises. Começa por um executável ou um ficheiro de features.'); td.colSpan = 5; tr.append(td); $('history').append(tr); }
    for (const item of data.items) {
      const tr = node('tr', '');
      tr.append(node('td', new Date(item.created_at).toLocaleString('pt-PT')), node('td', item.tipo), node('td', item.veredito || item.classificacao), node('td', item.estado_analise || (item.modelo_treinado_utilizado ? 'Modelo' : 'Triagem')));
      const td=node('td',''); const a=node('a','HTML'); a.href=`/api/reports/${item.id}/html`; const raw=node('a','JSON'); raw.href=`/api/reports/${item.id}`; td.append(a,document.createTextNode(' · '),raw); tr.append(td); $('history').append(tr);
    }
  } catch(e) { message(e.message, true); }
}
$('kind').addEventListener('change', kindChanged);
for (const mode of ['file', 'url']) $( `tab-${mode}`).addEventListener('click', () => {
  for (const m of ['file','url']) { $(`tab-${m}`).setAttribute('aria-selected', String(m === mode)); $(`${m}-form`).hidden = m !== mode; }
  $('result').hidden = true; message('');
});
$('file-form').addEventListener('submit', event => {
  event.preventDefault(); const file = $('file').files[0];
  if (!file) return;
  if (file.size > 12 * 1024 * 1024) { message('O limite é 12 MiB por ficheiro.', true); return; }
  const form = new FormData(); form.append('file', file); form.append('features_file', $('features-file').checked);
  run(() => api(`/api/analyze/upload/${$('kind').value}`, {method:'POST',body:form}));
});
$('url-form').addEventListener('submit', event => { event.preventDefault();
  const consent = $('allow-private').checked;
  $('allow-private').checked = false;
  run(() => api('/api/analyze/url', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({url:$('url').value, autorizar_consulta_privada:consent, consultar_virustotal:$('consult-vt').checked}),
  })); });
$('file').addEventListener('change', () => { $('file-label').textContent = $('file').files[0]?.name || 'Escolhe ou arrasta um ficheiro'; });
$('drop-zone').addEventListener('dragover', e => { e.preventDefault(); $('drop-zone').classList.add('dragging'); });
$('drop-zone').addEventListener('dragleave', () => $('drop-zone').classList.remove('dragging'));
$('drop-zone').addEventListener('drop', e => { e.preventDefault(); $('drop-zone').classList.remove('dragging'); if(e.dataTransfer.files.length) { $('file').files = e.dataTransfer.files; $('file').dispatchEvent(new Event('change')); } });
$('refresh').addEventListener('click', loadHistory);
kindChanged(); loadModels(); loadHistory();

async function loadCrewStatus() {
  try {
    const result = await api('/api/crew/status');
    $('crew-status').textContent = result.ready ? `CrewAI disponível · ${result.model}` : result.detail;
  } catch (error) {
    $('crew-status').textContent = error.message;
  }
}
loadCrewStatus();
