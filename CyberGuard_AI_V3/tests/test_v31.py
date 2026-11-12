import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from starlette.datastructures import UploadFile
from starlette.requests import Request
from backend import app, service
from backend.ransomware_static import extract as extract_ransomware, FEATURES
from backend.phishing_url import extract as extract_url
from tests.test_v3 import fixture

def run(coro):
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value
    raise AssertionError('Unexpected I/O')

async def direct(fn,*args):
    return fn(*args)

class V31Tests(unittest.TestCase):
    def test_ransomware_extraction_and_prediction(self):
        for wide in (False,True):
            data=extract_ransomware(fixture(wide))
            self.assertEqual(list(data),FEATURES)
            result=service.predict('ransomware_static',data)
            self.assertIn(result['classificacao'],('Não ransomware','Ransomware'))

    def test_url_features_and_real_prediction(self):
        f=extract_url('http://192.0.2.1/login@verify')
        self.assertEqual(f['UsingIP'],-1)
        self.assertEqual(f['Symbol@'],-1)
        self.assertEqual(len(f),7)
        result=service.predict('phishing_url',f)
        self.assertTrue(result['modelo_treinado_utilizado'])

    def test_routes_and_reports(self):
        with tempfile.TemporaryDirectory(dir=service.ROOT) as tmp:
            def db():
                c=sqlite3.connect(Path(tmp)/'test.sqlite3')
                c.execute('CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, created_at TEXT, payload TEXT)')
                return c
            with patch.object(service,'database',db),patch.object(app,'run_in_threadpool',direct),patch('starlette.datastructures.run_in_threadpool',direct):
                result=run(app.upload('ransomware_static',UploadFile(io.BytesIO(fixture()),filename='test.exe')))
                self.assertTrue(result['modelo_treinado_utilizado'])
                async def receive():
                    return {'type':'http.request','body':json.dumps({'url':'https://example.com'}).encode(),'more_body':False}
                request=Request({'type':'http','method':'POST','path':'/api/analyze/url','headers':[]},receive)
                result=run(app.url(request))
                self.assertTrue(result['modelo_treinado_utilizado'])
                self.assertEqual(result['tipo'],'phishing_url')
                self.assertNotIn('example.com',json.dumps(service.report(result['id'])))
                result=run(app.upload('malware',UploadFile(io.BytesIO(b'%PDF-1.0 test'),filename='test.pdf')))
                self.assertFalse(result['modelo_treinado_utilizado'])

if __name__=='__main__':
    unittest.main()
