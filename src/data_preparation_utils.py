import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def carregar_dataset(caminho):
    return pd.read_csv(caminho)


def remover_colunas(df, colunas):
    return df.drop(columns=colunas)


def verificar_missing_values(df):
    return df.isnull().sum().sum()


def verificar_duplicados(df):
    return df.duplicated().sum()


def verificar_conflitos_target(df, target):
    features = df.drop(columns=[target])

    grupos = df.groupby(
        list(features.columns)
    )[target].nunique()

    conflitos = grupos[grupos > 1]

    return conflitos


def remover_duplicados(df):
    return df.drop_duplicates()


def guardar_dataset(df, caminho):
    df.to_csv(caminho, index=False)


def separar_features_target(df, target):
    X = df.drop(columns=[target])
    y = df[target]

    return X, y


def dividir_treino_validacao_teste(
    X,
    y,
    random_state=42
):
    # 70% treino e 30% temporário
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=random_state,
        stratify=y
    )

    # Divide os 30% temporários em:
    # 15% validação e 15% teste
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=random_state,
        stratify=y_temp
    )

    return (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    )

def standardizar_dados(
    X_train,
    X_val,
    X_test
):
    scaler = StandardScaler()

    # Aprende apenas com os dados de treino
    X_train_scaled = scaler.fit_transform(X_train)

    # Aplica a mesma transformação
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    X_train_scaled = pd.DataFrame(
        X_train_scaled,
        columns=X_train.columns,
        index=X_train.index
    )

    X_val_scaled = pd.DataFrame(
        X_val_scaled,
        columns=X_val.columns,
        index=X_val.index
    )

    X_test_scaled = pd.DataFrame(
        X_test_scaled,
        columns=X_test.columns,
        index=X_test.index
    )

    return (
        X_train_scaled,
        X_val_scaled,
        X_test_scaled,
        scaler
    )

def verificar_perfis_repetidos(df, target):
    features = df.drop(columns=[target])

    duplicados = features.duplicated(
        keep=False
    )

    return df[duplicados]


def distribuicao_classes(y):
    return y.value_counts(normalize=True) * 100