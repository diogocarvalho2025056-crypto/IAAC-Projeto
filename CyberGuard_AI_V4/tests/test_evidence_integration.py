import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from fastapi.testclient import TestClient

from backend import service
from backend.app import app
from src import virustotal_client as vt


class EvidenceIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = self.enterContext(tempfile.TemporaryDirectory())
        self.temp = Path(temp)

        def database():
            db = sqlite3.connect(self.temp / 'history.sqlite')
            db.execute('CREATE TABLE IF NOT EXISTS analyses (id, created_at, payload)')
            return db

        self.enterContext(patch.object(service, 'database', database))
        self.enterContext(patch('backend.crew_analysis.interpret', return_value=None))
        self.key = self.enterContext(patch.object(vt, '_api_key', return_value='test-key'))
        self.get = self.enterContext(patch.object(vt.requests, 'get'))
        self.client = self.enterContext(TestClient(app))

    def upload(self):
        response = self.client.post('/api/analyze/upload/ransomware', files={'file': ('benign.txt', b'Test document')})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_missing_key(self):
        self.key.return_value = ''
        result = self.upload()
        self.assertEqual(result['virustotal']['estado'], 'sem_configuracao')
        self.assertEqual(result['estado_analise'], 'parcial')
        self.get.assert_not_called()

    def test_unknown_hash_and_missing_features(self):
        self.get.return_value = Mock(status_code=404)
        result = self.upload()
        self.assertEqual(result['virustotal']['estado'], 'sem_registo')
        self.assertEqual(result['comportamento']['estado'], 'em_falta')
        self.assertFalse(result['modelo_treinado_utilizado'])
        self.assertTrue(self.get.call_args.args[0].endswith('/files/' + hashlib.sha256(b'Test document').hexdigest()))

    def test_incompatible_behavior_report_does_not_predict(self):
        digest = hashlib.sha256(b'Test document').hexdigest()
        behavior = self.temp / 'runtime' / 'behavior'
        behavior.mkdir(parents=True)
        (behavior / (digest + '.json')).write_text(json.dumps({'sha256': digest, 'features': {}}))
        self.key.return_value = ''
        with patch.object(service, 'ROOT', self.temp), patch.object(service, 'feature_names', return_value=['processes_malicious']):
            result = self.upload()
        self.assertEqual(result['comportamento']['estado'], 'incompativel')
        self.assertFalse(result['modelo_treinado_utilizado'])

    def test_complete_behavior_export_runs_real_model(self):
        digest = hashlib.sha256(b'Test document').hexdigest()
        names = service.feature_names('ransomware')
        self.assertEqual(len(names), 165)
        root = self.temp
        export = root / 'runtime' / 'behavior'
        export.mkdir(parents=True)
        (root / 'models').mkdir()
        for artifact in ('ransomware_features.json', 'ransomware_model.pkl'):
            (root / 'models' / artifact).write_bytes((service.ROOT / 'models' / artifact).read_bytes())
        # Controlled vector to exercise the inference path; no sandbox observation is claimed.
        sample = {name: 1 for name in reversed(names)}
        (export / (digest + '.json')).write_text(json.dumps({'sha256': digest, 'features': sample}))
        self.key.return_value = ''
        with patch.object(service, 'ROOT', root):
            result = self.upload()
        self.assertEqual(result['comportamento']['estado'], 'disponivel')
        self.assertEqual(len(result['comportamento']['observacoes']), 16)
        self.assertEqual(list(result['features']), names)
        self.assertTrue(result['modelo_treinado_utilizado'])
        self.assertEqual(result['estado_analise'], 'parcial')
        model = service.load_model('ransomware')
        integer_feature = next(name for name, dtype in zip(names, model.get_booster().feature_types)
                               if dtype == 'int')
        sample[integer_feature] = 1.5
        with self.assertRaisesRegex(ValueError, integer_feature):
            service.predict('ransomware', sample)

    def test_real_url_model_and_controlled_divergence(self):
        url = 'https://example.com/'
        from backend.phishing_url import extract
        label = service.predict('phishing_url', extract(url))['classe']
        self.get.return_value = Mock(status_code=200, **{'json.return_value': {
            'data': {'attributes': {'last_analysis_stats': {'malicious': 1 - label, 'suspicious': 0}}}
        }})
        response = self.client.post('/api/analyze/url', json={'url': url})
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertTrue(result['modelo_treinado_utilizado'])
        self.assertEqual(result['estado_analise'], 'completa')
        self.assertEqual(result['relacao_fontes'], 'divergencia')
        html = self.client.get(f"/api/reports/{result['id']}/html").text
        self.assertIn('Fontes divergentes', html)
        self.assertIn('Motores maliciosos', html)

    def test_private_url_requires_consent(self):
        private = 'http://127.0.0.1/?token=private'
        result = self.client.post('/api/analyze/url', json={'url': private}).json()
        self.assertEqual(result['virustotal']['estado'], 'privado')
        self.get.assert_not_called()
        self.get.return_value = Mock(status_code=404)
        self.client.post('/api/analyze/url', json={'url': private, 'autorizar_consulta_privada': True})
        self.get.assert_called_once()

    def test_existing_virus_total_sandbox_and_family_remain_attributed(self):
        attributes = {
            'last_analysis_stats': {'malicious': 2, 'suspicious': 1},
            'sandbox_verdicts': {'Test sandbox': {'category': 'malicious'}},
            'popular_threat_classification': {'suggested_threat_label': 'ransomware.testfamily'},
        }
        self.get.return_value = Mock(status_code=200, **{'json.return_value': {'data': {'attributes': attributes}}})
        result = self.upload()
        self.assertFalse(result['modelo_treinado_utilizado'])
        self.assertEqual(result['estado_analise'], 'parcial')
        self.assertEqual(result['virustotal']['familia_sugerida'], 'testfamily')
        self.assertEqual(result['virustotal']['vereditos_sandbox'][0]['sandbox'], 'Test sandbox')
        html = self.client.get(f"/api/reports/{result['id']}/html").text
        self.assertIn('Família sugerida pelo VirusTotal', html)
        self.assertIn('Sandbox via VirusTotal', html)
        attributes['popular_threat_classification']['suggested_threat_label'] = 'trojan.testfamily'
        self.assertNotIn('familia_sugerida', self.upload()['virustotal'])

    def test_pending_quota_and_timeout(self):
        for status, expected in [(202, 'pendente'), (403, 'acesso_negado'), (429, 'limite_api')]:
            self.get.return_value = Mock(status_code=status)
            self.assertEqual(vt.consultar_url('https://example.com/')['estado'], expected)
        self.get.side_effect = requests.Timeout()
        self.assertEqual(vt.consultar_url('https://example.com/')['estado'], 'timeout')
