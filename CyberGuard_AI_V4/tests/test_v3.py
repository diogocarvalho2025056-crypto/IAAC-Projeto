import importlib.util
import json
import struct
import tempfile
import unittest
import io
from unittest.mock import patch
from pathlib import Path

from backend.pe_features import UnsupportedPE, extract_pe


def fixture(wide=False, overlay=b''):
    data = bytearray(1024)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 60, 128)
    data[128:132] = b'PE\0\0'
    struct.pack_into('<H', data, 134, 1)
    size = 240 if wide else 224
    struct.pack_into('<H', data, 148, size)
    opt = 152
    struct.pack_into('<H', data, opt, 0x20b if wide else 0x10b)
    struct.pack_into('<I', data, opt + 4, 512)
    struct.pack_into('<I', data, opt + 20, 4096)
    struct.pack_into('<I', data, opt + 60, 512)
    struct.pack_into('<I', data, opt + (108 if wide else 92), 16)
    if wide:
        struct.pack_into('<Q', data, opt + 24, 0x140000000)
    else:
        struct.pack_into('<I', data, opt + 24, 8192)
        struct.pack_into('<I', data, opt + 28, 0x400000)
    section = opt + size
    data[section:section + 8] = b'.text\0\0\0'
    struct.pack_into('<IIII', data, section + 8, 512, 4096, 512, 512)
    return bytes(data) + overlay


class PEFeaturesTests(unittest.TestCase):
    def test_both_pe_formats_and_overlay(self):
        for wide in (False, True):
            result = extract_pe(fixture(wide, b'OVERLAY'))
            self.assertEqual(len(result), 23)
            self.assertEqual(result['BaseOfData'], 0 if wide else 8192)
            self.assertEqual(result['ImageBase'], 0x140000000 if wide else 0x400000)
            self.assertEqual(result['TextSectionSize'], 512)
            self.assertEqual(result['OverlaySize'], 7)
            self.assertEqual(result['AvgSectionEntropy'], 0)

    def test_rejects_invalid_and_truncated_files(self):
        for data in (b'', b'MZ', b'%PDF-1.0', fixture()[:700]):
            with self.assertRaises(UnsupportedPE):
                extract_pe(data)

    def test_import_export_directories(self):
        for wide in (False, True):
            data = bytearray(fixture(wide))
            directories = 152 + (112 if wide else 96)
            struct.pack_into('<II', data, directories, 4200, 40)
            struct.pack_into('<II', data, directories + 8, 4096, 40)
            struct.pack_into('<IIIII', data, 512, 4144, 0, 0, 4164, 4144)
            struct.pack_into('<Q' if wide else '<I', data, 560, 1 << (63 if wide else 31) | 1)
            data[580:593] = b'KERNEL32.dll\0'
            struct.pack_into('<I', data, 636, 3)
            result = extract_pe(bytes(data))
            self.assertEqual(result['ImportedDLLs'], 1)
            self.assertEqual(result['ImportedFunctions'], 1)
            self.assertEqual(result['HasExportTable'], 1)
            self.assertEqual(result['ExportedFunctions'], 3)

    def test_out_of_bounds_import_is_rejected(self):
        data = bytearray(fixture())
        struct.pack_into('<II', data, 152 + 96 + 8, 0x7fffffff, 40)
        with self.assertRaises(UnsupportedPE):
            extract_pe(bytes(data))


@unittest.skipUnless(importlib.util.find_spec('xgboost'), 'Model dependencies required')
@patch('backend.crew_analysis.interpret', new=lambda _: {'engine':'CrewAI','model':'test','agents':[],'summary':'Síntese de teste'})
class DirectPipelineTests(unittest.TestCase):
    """Exercise real route handlers and models without opening any sockets."""
    def test_real_models_and_validation(self):
        from backend import service
        self.assertTrue(all(m['carregado'] for m in service.model_status()))
        for kind in ('malware', 'phishing', 'ransomware'):
            sample = {n: 0 for n in service.feature_names(kind)}
            result = service.predict(kind, sample)
            self.assertIn(result['classe'], (0, 1))
            self.assertTrue(0 <= result['probabilidade_ameaca'] <= 1)
            self.assertEqual(len(result['modelo']['sha256']), 64)
            sample[next(iter(sample))] = float('inf')
            with self.assertRaises(ValueError):
                service.validate(kind, sample)
        with self.assertRaises(ValueError):
            service.validate('malware', {})

    def test_upload_route_and_persistence(self):
        from backend import app as module, service
        from starlette.datastructures import UploadFile
        import sqlite3
        def run(coroutine):
            try:
                coroutine.send(None)
            except StopIteration as done:
                return done.value
            raise AssertionError('Unexpected asynchronous I/O')
        async def direct(function, *args):
            return function(*args)
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as tmp:
            def database():
                db = sqlite3.connect(Path(tmp) / 'history.sqlite3')
                db.execute('CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, created_at TEXT, payload TEXT)')
                return db
            with patch.object(service, 'database', database), patch.object(module, 'run_in_threadpool', direct), patch('starlette.datastructures.run_in_threadpool', direct):
                result = run(module.upload('malware', UploadFile(io.BytesIO(fixture()), filename='test.exe')))
                self.assertTrue(result['modelo_treinado_utilizado'])
                self.assertEqual(result['modo'], 'pe_estatico')
                self.assertEqual(len(result['features']), 23)
                self.assertEqual(service.report(result['id'])['sha256'], result['sha256'])
                self.assertEqual(len(service.history()), 1)
                with self.assertRaises(ValueError):
                    run(module.upload('ransomware', UploadFile(io.BytesIO(fixture()), filename='test.exe')))
                with self.assertRaises(ValueError):
                    run(module.upload('malware', UploadFile(io.BytesIO(b'MZ'), filename='bad.exe')))
                sample = {n: 1 for n in service.feature_names('phishing')}
                result = run(module.upload('phishing', UploadFile(io.BytesIO(json.dumps(sample).encode()), filename='features.json')))
                self.assertTrue(result['modelo_treinado_utilizado'])
                self.assertEqual(len(service.history()), 2)

    def test_url_and_structured_input_rules(self):
        from backend.real_inputs import inspect_url, parse_feature_file
        self.assertFalse(inspect_url('https://example.com')['modelo_treinado_utilizado'])
        with self.assertRaises(ValueError):
            inspect_url('file:///secret')
        with self.assertRaises(ValueError):
            parse_feature_file(b'a\nNaN\n', '.csv', ['a'])
        with self.assertRaises(ValueError):
            parse_feature_file(b'a\n1\n', '.csv', ['a', 'b'])


@unittest.skipUnless(importlib.util.find_spec('fastapi') and importlib.util.find_spec('httpx'), 'API dependencies required')
@patch('backend.crew_analysis.interpret', new=lambda _: {'engine':'CrewAI','model':'test','agents':[],'summary':'Síntese de teste'})
class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient
        from backend import service
        from backend.app import app
        cls.service = service
        cls.original_database = service.database
        cls.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        import sqlite3
        def database():
            db = sqlite3.connect(Path(cls.temp.name) / 'test.sqlite3')
            db.execute('CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, created_at TEXT, payload TEXT)')
            return db
        service.database = database
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.service.database = cls.original_database
        cls.temp.cleanup()

    def test_real_models_load_and_predict(self):
        states = self.client.get('/api/models').json()['models']
        self.assertTrue(all(s['carregado'] for s in states), states)
        for kind in ('malware', 'ransomware', 'phishing'):
            sample = {name: 0 for name in self.service.feature_names(kind)}
            result = self.service.predict(kind, sample)
            self.assertIn(result['classe'], (0, 1))
            self.assertTrue(0 <= result['probabilidade_ameaca'] <= 1)

    def test_exe_inference_history_and_report(self):
        r = self.client.post('/api/analyze/upload/malware', files={'file': ('test.exe', fixture())})
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertTrue(data['modelo_treinado_utilizado'])
        self.assertEqual(data['modo'], 'pe_estatico')
        self.assertFalse(data['validacao_externa'])
        self.assertEqual(len(data['features']), 23)
        report = self.client.get('/api/reports/' + data['id'])
        self.assertEqual(report.status_code, 200)
        self.assertIn('attachment', report.headers['content-disposition'])
        self.assertTrue(self.client.get('/api/history').json()['items'])

    def test_ransomware_cannot_use_raw_executable(self):
        r = self.client.post('/api/analyze/upload/ransomware', files={'file': ('test.exe', fixture())})
        self.assertEqual(r.status_code, 422)

    def test_phishing_features_use_real_model(self):
        sample = {name: 1 for name in self.service.feature_names('phishing')}
        r = self.client.post('/api/analyze/upload/phishing', files={'file': ('test.json', json.dumps(sample).encode())})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertTrue(r.json()['modelo_treinado_utilizado'])

    def test_invalid_inputs(self):
        for name, data in [('bad.exe', b'MZ'), ('empty.exe', b''), ('missing.csv', b'wrong\n1\n')]:
            r = self.client.post('/api/analyze/upload/malware', files={'file': (name, data)})
            self.assertEqual(r.status_code, 422, r.text)
        sample = {n: 0 for n in self.service.feature_names('malware')}
        sample['SizeOfCode'] = float('inf')
        with self.assertRaises(ValueError):
            self.service.validate('malware', sample)
        r = self.client.post('/api/analyze/upload/malware', files={'file': ('big.exe', b'x' * (12 * 1024 * 1024 + 1))})
        self.assertEqual(r.status_code, 413)

    def test_url_uses_model_and_is_not_persisted(self):
        url = 'http://127.0.0.1/private?secret=never-store-this'
        r = self.client.post('/api/analyze/url', json={'url': url})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertTrue(r.json()['modelo_treinado_utilizado'])
        self.assertNotIn('dominio', r.json())
        self.assertNotIn('never-store-this', self.client.get('/api/reports/' + r.json()['id']).text)
        self.assertEqual(self.client.post('/api/analyze/url', json={'url': 'file:///a'}).status_code, 422)

    def test_local_boundary(self):
        self.assertEqual(self.client.get('/', headers={'host': 'attacker.example'}).status_code, 403)
        self.assertEqual(self.client.post('/api/analyze/url', headers={'origin':'https://attacker.example'}, json={'url':'https://example.com'}).status_code, 403)
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('Content-Security-Policy', r.headers)


if __name__ == '__main__':
    unittest.main()
