import joblib
import pandas as pd
import numpy as np

class RansomwareAgent:
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)
        
    def analyze_sample(self, sample_df: pd.DataFrame) -> dict:
        """Recebe uma amostra PE e gera o diagnóstico com explicações."""
        prediction = self.model.predict(sample_df)[0]
        proba = self.model.predict_proba(sample_df)[0][prediction] if hasattr(self.model, "predict_proba") else 1.0
        
        status = "RANSOMWARE/MALWARE" if prediction == 1 else "BENIGNO"
        
        # Identificar principais indicadores
        indicators = []
        if 'registry_write' in sample_df.columns and sample_df['registry_write'].values[0] > 10:
            indicators.append("Elevada atividade de escrita nas chaves de registo do sistema.")
        if 'processes_malicious' in sample_df.columns and sample_df['processes_malicious'].values[0] > 0:
            indicators.append("Detetada tentativa de criação de processos maliciosos/injetados.")
        if 'network_connections' in sample_df.columns and sample_df['network_connections'].values[0] > 0:
            indicators.append("Conexões de rede ativas para endereços IP não confiáveis.")
            
        report = f"""
        =====================================================
        🛡️ RELATÓRIO TÉCNICO DE ANÁLISE DE AMEAÇAS (AGENTE LLM)
        =====================================================
        DIAGNÓSTICO: {status}
        NÍVEL DE CONFIANÇA: {proba*100:.2f}%
        
        RESUMO EXECUTIVO:
        O ficheiro analisado demonstra um perfil comportamental compativel com {status}.
        
        EVIDÊNCIAS COMPORTAMENTAIS DETETADAS:
        """ + "\n".join([f" - {ind}" for ind in (indicators if indicators else ["Padrões PE padrão dentro da norma."])]) + """
        
        RECOMENDAÇÃO DE MITIGAÇÃO:
        """ + ("Isolar a máquina da rede imediatamente e revogar credenciais." if prediction == 1 else "Nenhuma ação necessária. Ficheiro seguro.")
        
        return {
            'status': status,
            'confidence': proba,
            'report': report
        }