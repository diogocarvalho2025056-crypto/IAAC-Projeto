from pathlib import Path
root = Path(__file__).resolve().parents[1]
p = root/'frontend/index.html'
s = p.read_text(encoding='utf-8')
s = s.replace('<option value="ransomware">Malware comportamental · 165 features</option>', '<option value="ransomware_static">Ransomware · Executáveis Windows</option><option value="ransomware">Avançado: malware comportamental · 165 features</option>')
s = s.replace('Triagem de URL','Phishing de URL')
s = s.replace('Triagem lexical local. Não visita a página e não utiliza o modelo treinado de phishing. O endereço completo não é guardado.', 'Classificação XGBoost com 7 features extraídas do URL. Sem visitar a página. Versão lexical do modelo, treinada com o dataset do projeto; não usa HTML ou reputação. O endereço completo não é guardado.')
s = s.replace('Inspecionar URL ↗','Analisar phishing ↗')
p.write_text(s,encoding='utf-8')
