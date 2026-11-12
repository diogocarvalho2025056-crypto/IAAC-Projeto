import unittest
from unittest.mock import patch

from fastapi import HTTPException
from backend import app, crew_analysis
from backend.html_report import render_report


class CrewAnalysisTests(unittest.TestCase):
    def test_cannot_save_without_crew(self):
        with patch.object(crew_analysis, 'interpret', side_effect=crew_analysis.CrewUnavailable('Inicia o Ollama.')), patch.object(app.service, 'save') as save:
            with self.assertRaises(HTTPException) as error:
                app.finish_analysis({'classificacao': 'Phishing'})
            self.assertEqual(error.exception.status_code, 503)
            save.assert_not_called()

    def test_preserves_classification_and_includes_escaped_synthesis(self):
        synthesis = {'engine': 'CrewAI', 'model': 'local', 'agents': ['Analista', 'Revisor'],
                     'summary': '<script>texto do modelo</script>'}
        with patch.object(crew_analysis, 'interpret', return_value=synthesis) as interpret, patch.object(app.service, 'save', side_effect=lambda item: item):
            result = app.finish_analysis({'classificacao': 'Phishing', 'tipo': 'phishing_url'})
        interpret.assert_called_once()
        self.assertEqual(result['classificacao'], 'Phishing')
        self.assertEqual(result['crewai'], synthesis)
        html = render_report(result)
        self.assertIn('Síntese CrewAI', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>', html)

    def test_evidence_excludes_original_input_and_handles_batches(self):
        result = {'url': 'https://example.com/private', 'nome': 'private.exe', 'tipo': 'malware',
                  'resultados': [{'classificacao': 'Malware', 'modelo_treinado_utilizado': True},
                                 {'classificacao': 'Inconclusivo', 'modelo_treinado_utilizado': False}]}
        context = crew_analysis.evidence(result)
        self.assertEqual(len(context['amostras']), 2)
        self.assertEqual(context['amostras'][0]['classificacao'], 'Malware')
        self.assertIsNone(context['amostras'][1]['classificacao'])
        self.assertNotIn('private', str(context))
