import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# --------------------------------------------------
# 1. CARREGAR DATASET
# --------------------------------------------------

pasta_projeto = Path(__file__).parent.parent

ficheiro_csv = (
    pasta_projeto
    / "dataset"
    / "Malware_and_benign_recognition.csv"
)

df = pd.read_csv(ficheiro_csv)

print("--- DATASET ORIGINAL ---")
print(df.shape)


# --------------------------------------------------
# 2. CRIAR CÓPIA PARA PREPARAÇÃO
# --------------------------------------------------

df_prep = df.copy()


# --------------------------------------------------
# 3. REMOVER COLUNAS DESNECESSÁRIAS
# --------------------------------------------------

# Identificador do ficheiro
df_prep = df_prep.drop(columns=["File"])

# Variável constante
df_prep = df_prep.drop(columns=["SuspiciousSectionNames"])

# Variável redundante com NumberOfSections
df_prep = df_prep.drop(columns=["SectionCount"])


print("\n--- DATASET APÓS PREPARAÇÃO INICIAL ---")
print(df_prep.shape)

print("\n--- COLUNAS RESTANTES ---")
print(df_prep.columns)


# --------------------------------------------------
# 4. VERIFICAR VALORES EM FALTA
# --------------------------------------------------

print("\n--- VALORES EM FALTA ---")
print(df_prep.isnull().sum().sum())


# --------------------------------------------------
# 5. VERIFICAR DUPLICADOS COMPLETOS
# --------------------------------------------------

print("\n--- DUPLICADOS COMPLETOS ---")
print(df_prep.duplicated().sum())


# --------------------------------------------------
# 6. VERIFICAR PERFIS DE FEATURES REPETIDOS
# --------------------------------------------------

features_sem_target = df_prep.drop(columns=["Malicious"])

duplicados_features = features_sem_target.duplicated(
    keep=False
)

dados_repetidos = df_prep[duplicados_features]

print("\n--- PERFIS DE FEATURES REPETIDOS ---")
print(dados_repetidos)

print("\nNúmero de registos com features repetidas:")
print(len(dados_repetidos))


# --------------------------------------------------
# 7. VERIFICAR RÓTULOS CONTRADITÓRIOS
# --------------------------------------------------

print("\n--- VERIFICAÇÃO DE RÓTULOS CONTRADITÓRIOS ---")

grupos = df_prep.groupby(
    list(features_sem_target.columns)
)["Malicious"].nunique()

conflitos = grupos[grupos > 1]

print(conflitos)

print(
    "\nNúmero de perfis com conflito:",
    len(conflitos)
)


# --------------------------------------------------
# 8. REMOVER DUPLICADOS COMPLETOS
# --------------------------------------------------

df_prep = df_prep.drop_duplicates()

print("\n--- DATASET APÓS REMOVER DUPLICADOS ---")
print(df_prep.shape)

print("\nDuplicados restantes:")
print(df_prep.duplicated().sum())


# --------------------------------------------------
# 9. GUARDAR DATASET PREPARADO
# --------------------------------------------------

ficheiro_preparado = (
    pasta_projeto
    / "dataset"
    / "Malware_prepared.csv"
)

df_prep.to_csv(
    ficheiro_preparado,
    index=False
)

print("\n--- DATASET PREPARADO GUARDADO ---")
print(ficheiro_preparado)
print("Dimensão:", df_prep.shape)


# --------------------------------------------------
# 10. SEPARAR FEATURES E TARGET
# --------------------------------------------------

X = df_prep.drop(columns=["Malicious"])
y = df_prep["Malicious"]

print("\n--- FEATURES ---")
print(X.shape)

print("\n--- TARGET ---")
print(y.shape)


# --------------------------------------------------
# 11. DIVIDIR TREINO E TESTE
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n--- DIMENSÕES DOS CONJUNTOS ---")
print("X_train:", X_train.shape)
print("X_test:", X_test.shape)
print("y_train:", y_train.shape)
print("y_test:", y_test.shape)


# --------------------------------------------------
# 12. CONFIRMAR DISTRIBUIÇÃO DAS CLASSES
# --------------------------------------------------

print("\n--- DISTRIBUIÇÃO NO TREINO ---")
print(y_train.value_counts(normalize=True) * 100)

print("\n--- DISTRIBUIÇÃO NO TESTE ---")
print(y_test.value_counts(normalize=True) * 100)


# --------------------------------------------------
# 13. FEATURE SCALING - STANDARDIZAÇÃO
# --------------------------------------------------

scaler = StandardScaler()

# Aprende média e desvio-padrão apenas com o treino
X_train_scaled = scaler.fit_transform(X_train)

# Aplica exatamente a mesma transformação ao teste
X_test_scaled = scaler.transform(X_test)

# Converter novamente para DataFrame para manter nomes das colunas
X_train_scaled = pd.DataFrame(
    X_train_scaled,
    columns=X_train.columns,
    index=X_train.index
)

X_test_scaled = pd.DataFrame(
    X_test_scaled,
    columns=X_test.columns,
    index=X_test.index
)

print("\n--- FEATURE SCALING ---")
print("X_train_scaled:", X_train_scaled.shape)
print("X_test_scaled:", X_test_scaled.shape)

print("\n--- EXEMPLO ANTES DO SCALING ---")
print(X_train.head())

print("\n--- EXEMPLO DEPOIS DO SCALING ---")
print(X_train_scaled.head())