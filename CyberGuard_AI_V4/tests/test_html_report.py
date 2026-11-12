import unittest
from unittest.mock import patch
from backend.html_report import render_report
from backend.app import app
from fastapi.testclient import TestClient

class ReportTests(unittest.TestCase):
    def sample(self,kind='phishing_url',label=1):
        return {'id':'abc123','tipo':kind,'classe':label,'classificacao':'Phishing' if label else 'Legítimo',
                'confianca':.8,'probabilidade_ameaca':.8 if label else .2,'modelo_treinado_utilizado':True,
                'top_features':[{'feature':'UsingIP','valor':-1,'contribuicao':1.42}],
                'features':{'UsingIP':-1},'created_at':'2026-11-10T20:00:00+00:00',
                'modelo':{'artefacto':'phishing_url_xgboost.json','sha256':'a'*64},'versao':'3.1.0'}

    def test_reference_sections_scores_and_print(self):
        html=render_report(self.sample())
        for value in ['Classificação','80,00%','20,00%','Contribuição SHAP','UsingIP','1,4200','Rastreabilidade técnica','Ctrl+P','phishing_url_xgboost.json','@media print']:
            self.assertIn(value,html)

    def test_escapes_untrusted_content(self):
        item=self.sample(); item['classificacao']='<script>alert(1)</script>'
        item['top_features'][0]['feature']='<img src=x onerror=alert(1)>'
        html=render_report(item)
        self.assertNotIn('<script>',html); self.assertNotIn('<img',html)
        self.assertIn('&lt;script&gt;',html)

    def test_inspection_never_invents_scores(self):
        html=render_report({'tipo':'malware','classificacao':'Inspeção estática','modelo_treinado_utilizado':False,'indicadores_observados':['Entropia elevada']})
        self.assertIn('Não aplicável',html)
        self.assertNotIn('Score de benigno',html)
        self.assertIn('Entropia elevada',html)

    def test_ransomware_negative_is_not_benign(self):
        item=self.sample('ransomware_static',0); item['classificacao']='Não ransomware'
        html=render_report(item)
        self.assertIn('Score de não ransomware',html)
        self.assertNotIn('Score de benigno',html)
        self.assertIn('outros tipos de malware',html)

    def test_batch(self):
        item=self.sample(); item['resultados']=[self.sample(),self.sample(label=0)]
        html=render_report(item)
        self.assertIn('Amostra 1',html); self.assertIn('Amostra 2',html)

    def test_http_download_preview_json_and_missing(self):
        with TestClient(app) as client,patch('backend.app.service.report',return_value=self.sample()):
            response=client.get('/api/reports/abc123/html')
            self.assertEqual(response.status_code,200)
            self.assertIn('attachment',response.headers['content-disposition'])
            self.assertIn('text/html',response.headers['content-type'])
            self.assertIn("script-src 'none'",response.headers['content-security-policy'])
            self.assertIn("style-src 'unsafe-inline'",response.headers['content-security-policy'])
            self.assertNotIn('content-disposition',client.get('/api/reports/abc123/html?download=false').headers)
            self.assertEqual(client.get('/api/reports/abc123').json()['id'],'abc123')
        with TestClient(app) as client,patch('backend.app.service.report',return_value=None):
            self.assertEqual(client.get('/api/reports/missing/html').status_code,404)

if __name__=='__main__': unittest.main()
