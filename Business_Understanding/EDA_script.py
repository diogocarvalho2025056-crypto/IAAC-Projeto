import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Carga dos dados
df = pd.read_csv('../data/raw/ransom.csv')

print(f"Dimensão do dataset: {df.shape[0]} amostras, {df.shape[1]} colunas.")

# 2. Distribuição das Variáveis Alvo
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Classe Binária
sns.countplot(data=df, x='Class', ax=axes[0], palette='viridis')
axes[0].set_title('Distribuição da Classe (Benigno vs Malware)')

# Categoria de Malware
sns.countplot(data=df, x='Category', ax=axes[1], palette='magma')
axes[1].set_title('Distribuição por Categoria')
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('class_distribution.png')
plt.show()

# 3. Análise de Atributos Comportamentais
behavioral_cols = ['registry_write', 'network_connections', 'processes_malicious', 'files_malicious', 'apis']
print("\nResumo Estatístico dos Atributos Comportamentais:")
print(df[behavioral_cols].groupby(df['Category']).mean())