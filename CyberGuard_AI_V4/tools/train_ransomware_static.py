"""Train ransomware vs all other classes, using static headers only.
Run with the local ransom_cleaned.csv path as the sole positional argument.
"""
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier
from backend.ransomware_static import FEATURES

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1])
df = pd.read_csv(source)
print('Categories:', df['Category'].value_counts().to_dict(), flush=True)
df['target'] = df['Category'].astype(str).str.strip().str.casefold().eq('ransomware').astype(int)
if df['target'].nunique() != 2:
    raise ValueError('O dataset não contém as duas classes necessárias.')
conflicting = df.groupby('md5')['target'].nunique()
conflicting = set(conflicting[conflicting > 1].index)
df = df[~df['md5'].isin(conflicting)].drop_duplicates('md5').copy()
X = df[FEATURES].apply(pd.to_numeric, errors='raise')
if X.isna().any().any():
    raise ValueError('Há features estáticas em falta; não são substituídas por zeros.')
train, rest = train_test_split(df.index, test_size=.30, stratify=df.target, random_state=42)
val, test = train_test_split(rest, test_size=.5, stratify=df.loc[rest, 'target'], random_state=42)
model = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=.08,
                      subsample=.9, colsample_bytree=.9, n_jobs=1,
                      random_state=42, eval_metric='logloss')
model.fit(X.loc[train], df.loc[train, 'target'])
def metrics(indices):
    y = df.loc[indices, 'target']
    pred = model.predict(X.loc[indices]); p = model.predict_proba(X.loc[indices])[:, 1]
    return {'accuracy': accuracy_score(y, pred), 'precision': precision_score(y,pred,zero_division=0),
            'recall': recall_score(y,pred,zero_division=0), 'f1': f1_score(y,pred,zero_division=0),
            'roc_auc': roc_auc_score(y,p), 'matriz_confusao': confusion_matrix(y,pred).tolist()}
meta = {'data': datetime.now(timezone.utc).isoformat(), 'target': 'Category == Ransomware',
        'classes': {'0':'Não ransomware (inclui benigno e outros malwares)', '1':'Ransomware'},
        'features': FEATURES, 'dataset_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'deduplicacao': 'Uma amostra por md5 antes da divisão; grupos contraditórios excluídos.',
        'grupos_contraditorios_excluidos': len(conflicting),
        'tamanhos': {'treino':len(train),'validacao':len(val),'teste':len(test)},
        'sobreposicao_md5': 0,
        'validacao': metrics(val), 'teste': metrics(test),
        'limitacao': 'Avaliação interna do dataset. Sem validação externa pareada com binários; não garante deteção de variantes novas.'}
model.save_model(root / 'models/ransomware_static_xgboost.json')
(root / 'models/ransomware_static_features.json').write_text(json.dumps(FEATURES,indent=2),encoding='utf-8')
(root / 'models/ransomware_static_metrics.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False,indent=2),flush=True)
