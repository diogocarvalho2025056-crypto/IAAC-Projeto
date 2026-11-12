"""Train a URL-only phishing model from the existing encoded dataset."""
import sys
import json
import hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier
from backend.phishing_url import FEATURES

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1])
df = pd.read_csv(source)
X = df[FEATURES]
y = df['class'].eq(-1).astype(int)
if not set(df['class'].unique()) <= {-1,1} or y.nunique() != 2:
    raise ValueError('Rótulos de phishing inesperados.')
# Group exact original records (all 30 features), not the reduced lexical
# vectors: different websites can legitimately share the same lexical profile.
# Domain/time isolation cannot be verified because original URLs are absent.
groups = pd.util.hash_pandas_object(df.drop(columns=['class']),index=False).values
from sklearn.model_selection import StratifiedGroupKFold
folds = list(StratifiedGroupKFold(10,shuffle=True,random_state=42).split(X,y,groups))
test = folds[0][1]
train = folds[0][0]
model = XGBClassifier(n_estimators=150,max_depth=3,learning_rate=.08,n_jobs=1,random_state=42,eval_metric='logloss')
model.fit(X.iloc[train],y.iloc[train])
p = model.predict_proba(X.iloc[test])[:,1]; pred=model.predict(X.iloc[test]); actual=y.iloc[test]
metrics={'target':'class == -1', 'features':FEATURES, 'treino':len(train),'numero_amostras_teste':len(test),
         'dataset_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'divisao':'StratifiedGroupKFold, 1 de 10 folds para teste, agrupado pelo registo original completo (30 features); sem tuning no teste.',
         'teste':{'accuracy':accuracy_score(actual,pred),'precision':precision_score(actual,pred,zero_division=0),
                  'recall':recall_score(actual,pred,zero_division=0),'f1':f1_score(actual,pred,zero_division=0),
                  'roc_auc':roc_auc_score(actual,p),'matriz_confusao':confusion_matrix(actual,pred).tolist()},
         'limitacao':'Modelo lexical reduzido; sem HTML ou reputação. Dataset sem URLs originais: equivalência dos extratores não validada em pares, nem generalização por domínio/tempo.'}
model.save_model(root/'models/phishing_url_xgboost.json')
(root/'models/phishing_url_features.json').write_text(json.dumps(FEATURES,indent=2),encoding='utf-8')
(root/'models/phishing_url_metrics.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(metrics,indent=2,ensure_ascii=False),flush=True)
