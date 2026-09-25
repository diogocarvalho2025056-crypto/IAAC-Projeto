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


def dividir_treino_teste(
    X,
    y,
    test_size=0.20,
    random_state=42
):
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )


def standardizar_dados(X_train, X_test):
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

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

    return X_train_scaled, X_test_scaled, scaler