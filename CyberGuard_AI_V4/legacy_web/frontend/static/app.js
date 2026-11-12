'use strict';
const $ = (id) => document.getElementById(id);
const formatTime = (s) => { try { return new Date(s).toLocaleString('pt-PT'); } catch { return s; } };
const safe = (s) => String(s ?? '—');
let busy = false;

async function fetchJson(url, options = {}) {
  const response = await fetch(url, { credentials: 'same-origin', ...options });
  let data;
  try { data = await response.json(); }
  catch { throw new Error(`Resposta inválida do servidor (HTTP ${response.status}).`); }
  if (!response.ok) {
    const detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || data);
    throw new Error(`HTTP ${response.status}: ${detail}`);
  }
  return data;
}
function setNotice(id, message, error = false) {
  const node = $(id);
  node.textContent = message;
  node.className = `notice ${error ? 'error' : 'success'}`;
}
function sampleJson() {
  try {
    const value = JSON.parse($('sample-json').value);
    if (!value || Array.isArray(value) || typeof value !== 'object') throw new Error();
    return value;
  } catch {
    setNotice('analysis-message', 'Introduz uma amostra em JSON válido, com as features e respetivos valores.', true);
    return null;
  }
}
async function loadSample(label) {
  const kind = $('model-select').value;
  setNotice('analysis-message', `A carregar exemplo de ${kind}...`);
  try {
    const data = await fetchJson(`/api/samples/${encodeURIComponent(kind)}/${label}`);
    $('sample-json').value = JSON.stringify(data.amostra, null, 2);
    setNotice('analysis-message', `Exemplo carregado (${data.classe_dataset}). Pronto a executar.`);
  } catch (error) { setNotice('analysis-message', error.message, true); }
}
function showResult(data) {
  $('result-placeholder').hidden = true;
  $('result-content').hidden = false;
  const title = data.classificacao ?? data.predicao ?? data.resultado ?? 'Classificação concluída';
  $('result-classification').textContent = typeof title === 'object' ? 'Análise concluída' : safe(title);
  const conf = Number(data.confianca);
  const confidence = data.confianca !== undefined && Number.isFinite(conf)
    ? ` · Confiança: ${(conf <= 1 ? conf * 100 : conf).toFixed(2)}%` : '';
  const modeText = data.modelo_treinado_utilizado === true || data.modo === 'modelo_treinado'
    ? 'CLASSIFICADOR TREINADO' : data.modo === 'triagem_url_local'
      ? 'TRIAGEM LEXICAL · SEM ML' : data.modo === 'inspecao_estatica'
        ? 'INSPEÇÃO ESTÁTICA · SEM ML' : 'INFERÊNCIA DE FEATURES';
  const parts = [safe(data.tipo).toUpperCase(), modeText];
  if (confidence) parts.push(confidence.trim().replace(/^· /, ''));
  if (data.tempo_ms !== null && data.tempo_ms !== undefined) parts.push(`${data.tempo_ms} ms`);
  if (data.analysis_id) parts.push(`ID ${data.analysis_id}`);
  $('result-meta').textContent = parts.join(' · ');
  $('result-json').textContent = JSON.stringify(data, null, 2);
  $('result-note').textContent = typeof data.nota === 'string' ? data.nota : '';
  const container = $('result-highlights');
  container.replaceChildren();
  const facts = [];
  if (data.ficheiro) facts.push(['Ficheiro', data.ficheiro]);
  if (data.formato_identificado) facts.push(['Formato', data.formato_identificado]);
  if (data.sha256) facts.push(['SHA-256', data.sha256]);
  if (data.dominio) facts.push(['Domínio', data.dominio]);
  if (data.numero_amostras) facts.push(['Amostras classificadas', data.numero_amostras]);
  if (Array.isArray(data.indicadores_observados)) {
    facts.push(['Indicadores identificados', data.indicadores_observados.length]);
  }
  for (const [name, value] of facts) {
    const card = document.createElement('div'); card.className = 'result-fact';
    const label = document.createElement('span'); label.textContent = name;
    const strong = document.createElement('strong'); strong.textContent = String(value);
    card.append(label, strong); container.append(card);
  }
  if (Array.isArray(data.indicadores_observados) && data.indicadores_observados.length) {
    const heading = document.createElement('h4'); heading.textContent = 'Sinais que merecem atenção';
    const list = document.createElement('ul'); list.className = 'signal-list';
    for (const message of data.indicadores_observados) {
      const item = document.createElement('li'); item.textContent = message; list.append(item);
    }
    container.append(heading, list);
  }
}
async function analyzeModel(useAgent = false) {
  if (busy) return;
  const sample = sampleJson();
  if (!sample) return;
  busy = true;
  $('analyze-button').disabled = true;
  $('crew-button').disabled = true;
  const kind = $('model-select').value;
  setNotice('analysis-message', useAgent ? 'A executar os agentes CrewAI...' : 'A executar inferência do classificador...');
  try {
    const data = await fetchJson(useAgent ? `/api/agents/${kind}` : `/api/analyze/${kind}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sample),
    });
    if (useAgent) {
      const technical = data.resultado_tecnico && typeof data.resultado_tecnico === 'object'
        ? data.resultado_tecnico : { resultado: data.resultado_tecnico };
      showResult({ ...technical, tipo: kind, explicacao_agente: data.explicacao });
    } else showResult(data);
    setNotice('analysis-message', 'Análise executada com sucesso.');
    await loadHistory();
  } catch (error) { setNotice('analysis-message', error.message, true); }
  finally { busy = false; $('analyze-button').disabled = false; $('crew-button').disabled = false; }
}
let chosenFile = null;
let currentMode = 'file';

function switchMode(mode) {
  if (mode === 'url' && $('model-select').value !== 'phishing') mode = 'file';
  currentMode = mode;
  for (const value of ['file', 'url', 'features']) {
    $(`${value}-pane`).hidden = value !== mode;
    $(`mode-${value}`).classList.toggle('active', value === mode);
    $(`mode-${value}`).setAttribute('aria-pressed', String(value === mode));
  }
  setNotice('analysis-message', mode === 'file' ? 'Seleciona ou arrasta um ficheiro real.'
    : mode === 'url' ? 'Introduz um URL real para triagem lexical.'
    : 'Introduz features com os nomes exatos usados no treino do modelo.');
}
function changeKind() {
  const phishing = $('model-select').value === 'phishing';
  $('mode-url').hidden = !phishing;
  chosenFile = null;
  $('real-file').value = '';
  $('file-selected').textContent = 'Nenhum ficheiro selecionado.';
  $('sample-json').value = '';
  $('result-content').hidden = true;
  $('result-placeholder').hidden = false;
  switchMode(phishing ? 'url' : 'file');
}
function chooseFile(file) {
  if (!file) return;
  if (file.size > 12 * 1024 * 1024) {
    chosenFile = null;
    $('file-selected').textContent = 'Nenhum ficheiro selecionado.';
    setNotice('analysis-message', 'O ficheiro excede o limite de 12 MiB.', true);
    return;
  }
  chosenFile = file;
  $('file-selected').textContent = `${file.name} · ${(file.size / 1024).toFixed(1)} KiB`;
  setNotice('analysis-message', 'Ficheiro carregado no navegador. Clica em Analisar ficheiro.');
}
async function analyzeFile() {
  if (busy) return;
  if (!chosenFile) { setNotice('analysis-message', 'Escolhe ou arrasta um ficheiro primeiro.', true); return; }
  const kind = $('model-select').value;
  const form = new FormData();
  form.append('file', chosenFile, chosenFile.name);
  busy = true;
  $('analyze-file').disabled = true;
  setNotice('analysis-message', 'A processar o ficheiro localmente...');
  try {
    const data = await fetchJson(`/api/analyze/upload/${encodeURIComponent(kind)}`, {
      method: 'POST', body: form,
    });
    showResult(data);
    setNotice('analysis-message', data.modo === 'modelo_treinado'
      ? 'Inferência real concluída utilizando as features do modelo.'
      : 'Inspeção estática concluída. O resultado não é uma classificação de malware.');
    await loadHistory();
  } catch (error) { setNotice('analysis-message', error.message, true); }
  finally { busy = false; $('analyze-file').disabled = false; }
}
async function analyzeUrl() {
  if (busy) return;
  const url = $('target-url').value.trim();
  if (!url) { setNotice('analysis-message', 'Introduz o URL a analisar.', true); return; }
  busy = true;
  $('analyze-url').disabled = true;
  setNotice('analysis-message', 'A analisar o endereço sem visitar o site...');
  try {
    const data = await fetchJson('/api/analyze/url', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({url}),
    });
    showResult(data);
    setNotice('analysis-message', 'Triagem do URL concluída. Isto não é uma previsão do modelo Phishing.');
    await loadHistory();
  } catch (error) { setNotice('analysis-message', error.message, true); }
  finally { busy = false; $('analyze-url').disabled = false; }
}

async function refreshStatus() {
  try {
    const data = await fetchJson('/api/models');
    $('ollama-status').textContent = data.ollama.online ? 'Online' : 'Offline';
    $('ollama-status').className = `state ${data.ollama.online ? 'ready' : 'missing'}`;
    const crewReady = data.crewai.files_present && data.crewai.package_installed;
    $('crew-status').textContent = crewReady ? 'Instalado' : 'Não configurado';
    $('crew-status').className = `state ${crewReady ? 'ready' : 'missing'}`;
    const select = $('ollama-model');
    const previous = select.value;
    select.replaceChildren();
    const models = data.ollama.models || [];
    if (!models.length) {
      select.add(new Option(data.ollama.online ? 'Sem modelos instalados' : 'Ollama offline', ''));
      $('ask-button').disabled = true;
    } else {
      models.forEach((m) => select.add(new Option(m, m)));
      select.value = models.includes(previous) ? previous : models.includes(data.ollama.default_model) ? data.ollama.default_model : models[0];
      $('ask-button').disabled = false;
    }
    return data;
  } catch (error) { setNotice('assistant-message', error.message, true); }
}
async function askAssistant() {
  const prompt = $('ollama-prompt').value.trim();
  const model = $('ollama-model').value;
  if (!prompt || !model) { setNotice('assistant-message', 'Escolhe um modelo e introduz uma pergunta.', true); return; }
  $('ask-button').disabled = true;
  setNotice('assistant-message', 'O Ollama está a gerar a resposta...');
  $('assistant-response').hidden = true;
  try {
    const data = await fetchJson('/api/assistant', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, model }),
    });
    $('assistant-response').textContent = data.resposta || '(resposta vazia)';
    $('assistant-response').hidden = false;
    setNotice('assistant-message', `Resposta recebida de ${data.modelo}.`);
  } catch (error) { setNotice('assistant-message', error.message, true); }
  finally { $('ask-button').disabled = false; }
}
async function loadHistory() {
  const node = $('web-history');
  try {
    const data = await fetchJson('/api/history?limit=15');
    node.replaceChildren();
    if (!data.items.length) { node.textContent = 'Ainda não foram feitas análises nesta interface.'; return; }
    data.items.forEach((item) => {
      const row = document.createElement('div'); row.className = 'history-row';
      const left = document.createElement('div');
      const title = document.createElement('strong'); title.textContent = `${safe(item.tipo)} · ${safe(item.classificacao)}`;
      const time = document.createElement('small'); time.textContent = formatTime(item.created_at);
      left.append(title, time);
      const duration = document.createElement('small'); duration.textContent = `${safe(item.tempo_ms)} ms`;
      row.append(left, duration); node.append(row);
    });
  } catch (error) { node.textContent = `Erro a carregar histórico: ${error.message}`; }
}

document.addEventListener('DOMContentLoaded', () => {
  $('mode-file').addEventListener('click', () => switchMode('file'));
  $('mode-url').addEventListener('click', () => switchMode('url'));
  $('mode-features').addEventListener('click', () => switchMode('features'));
  const zone = $('drop-zone');
  const input = $('real-file');
  zone.addEventListener('click', (event) => { if (event.target !== input) input.click(); });
  zone.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); input.click(); }
  });
  input.addEventListener('change', () => chooseFile(input.files?.[0]));
  zone.addEventListener('dragover', (event) => { event.preventDefault(); zone.classList.add('dragging'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragging'));
  zone.addEventListener('drop', (event) => {
    event.preventDefault(); zone.classList.remove('dragging');
    chooseFile(event.dataTransfer.files?.[0]);
  });
  $('analyze-file').addEventListener('click', analyzeFile);
  $('analyze-url').addEventListener('click', analyzeUrl);
  $('target-url').addEventListener('keydown', (event) => {
    if (event.key === 'Enter') { event.preventDefault(); analyzeUrl(); }
  });
  $('analyze-button').addEventListener('click', () => analyzeModel(false));
  $('crew-button').addEventListener('click', () => analyzeModel(true));
  $('model-select').addEventListener('change', changeKind);
  $('ask-button').addEventListener('click', askAssistant);
  $('refresh-status').addEventListener('click', refreshStatus);
  $('refresh-history').addEventListener('click', loadHistory);
  changeKind();
  refreshStatus(); loadHistory();
});
