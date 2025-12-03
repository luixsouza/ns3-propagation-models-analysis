import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

num_seeds = 50
models = {
    0: 'Friis',
    1: 'FixedRss',
    2: 'ThreeLog',
    3: 'TwoRay',
    4: 'Nakagami'
}

avg_data = {}

print("--- ETAPA 1: Processando dados e calculando médias ---")

for model_id, model_name in models.items():
    all_runs = []
    
    for s in range(1, num_seeds + 1):
        filename = f"ns_{model_name}_S{s}.csv"
        
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce')
                df['Throughput'] = pd.to_numeric(df['Throughput'], errors='coerce')
                df['RSS'] = pd.to_numeric(df['RSS'], errors='coerce')
                df.dropna(inplace=True)
                
                if not df.empty:
                    df['Seed'] = s 
                    all_runs.append(df)
            except Exception as e:
                pass
        
    if all_runs:
        big_df = pd.concat(all_runs)
        mean_df = big_df.groupby('Distancia').mean().reset_index()
        avg_data[model_name] = mean_df
        print(f"Modelo {model_name}: OK ({len(all_runs)} seeds).")
    else:
        print(f"Aviso: Sem dados para {model_name}")

print("\n--- ETAPA 2: Gerando Gráficos Solicitados ---")

plt.figure(figsize=(10, 6))
for name, df in avg_data.items():
    plt.plot(df['Distancia'], df['Throughput'], label=name, linewidth=2)

plt.xlabel('Distância (m)')
plt.ylabel('Throughput Médio (Mbps)')
plt.title('1. Throughput vs. Distância')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig('grafico1_throughput_distancia.png')
print("Salvo: grafico1_throughput_distancia.png")
plt.close()

plt.figure(figsize=(10, 6))
for name, df in avg_data.items():
    df_clean = df[df['RSS'] > -95]
    plt.plot(df_clean['Distancia'], df_clean['RSS'], label=name, linewidth=2)

plt.xlabel('Distância (m)')
plt.ylabel('RSS Médio (dBm)')
plt.title('2. RSS vs. Distância')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig('grafico2_rss_distancia.png')
print("Salvo: grafico2_rss_distancia.png")
plt.close()

plt.figure(figsize=(10, 6))
for name, df in avg_data.items():
    plt.scatter(df['RSS'], df['Throughput'], label=name, alpha=0.6, s=15)

plt.xlabel('RSS (dBm)')
plt.ylabel('Throughput (Mbps)')
plt.title('3. Correlação: Throughput vs. RSS')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig('grafico3_dispersao_rss_throughput.png')
print("Salvo: grafico3_dispersao_rss_throughput.png")
plt.close()

target_distances = [30, 80, 130, 180, 230, 280, 330]
plt.figure(figsize=(12, 6))

bar_width = 0.15
x_indices = np.arange(len(target_distances))

for i, (name, df) in enumerate(avg_data.items()):
    y_values = []
    for target in target_distances:
        idx = (df['Distancia'] - target).abs().idxmin()
        val = df.loc[idx, 'Throughput']
        y_values.append(val)
    plt.bar(x_indices + (i * bar_width), y_values, width=bar_width, label=name)

plt.xlabel('Distância Alvo (m)')
plt.ylabel('Throughput (Mbps)')
plt.title('4. Comparação de Throughput em Pontos Específicos')
plt.xticks(x_indices + bar_width * 2, target_distances)
plt.legend()
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.savefig('grafico4_barras_distancias.png')
print("Salvo: grafico4_barras_distancias.png")
plt.close()

plt.figure(figsize=(10, 6))
threshold_distances = []
model_names = []

drop_threshold = 10.0 

for name, df in avg_data.items():
    drops = df[df['Throughput'] < drop_threshold]
    
    if not drops.empty:
        first_drop_dist = drops.iloc[0]['Distancia']
    else:
        first_drop_dist = df['Distancia'].max()
        
    threshold_distances.append(first_drop_dist)
    model_names.append(name)

colors = ['blue', 'orange', 'green', 'red', 'purple']
plt.barh(model_names, threshold_distances, color=colors, alpha=0.7)
plt.xlabel('Distância Máxima Operacional (m)')
plt.title(f'5. Limiar de Queda de Conexão (< {drop_threshold} Mbps)')
plt.grid(True, axis='x', linestyle='--', alpha=0.7)

for index, value in enumerate(threshold_distances):
    plt.text(value, index, f' {value:.1f}m', va='center')

plt.savefig('grafico5_limiares_queda.png')
print("Salvo: grafico5_limiares_queda.png")
plt.close()

if 'Nakagami' in avg_data:
    plt.figure(figsize=(10, 6))
    raw_dfs = []
    for s in range(1, num_seeds + 1):
        f = f"ns_Nakagami_S{s}.csv"
        if os.path.exists(f):
            d = pd.read_csv(f)
            d['Distancia'] = pd.to_numeric(d['Distancia'], errors='coerce')
            d['Throughput'] = pd.to_numeric(d['Throughput'], errors='coerce')
            d.dropna(inplace=True)
            raw_dfs.append(d)
    
    if raw_dfs:
        big_naka = pd.concat(raw_dfs)
        grouped = big_naka.groupby('Distancia')['Throughput']
        mean = grouped.mean()
        std = grouped.std().fillna(0)
        
        x = mean.index.to_numpy()
        y = mean.to_numpy()
        e = std.to_numpy()

        plt.plot(x, y, label='Média Nakagami', color='purple')
        plt.fill_between(x, y - e, y + e, color='purple', alpha=0.2, label='Desvio Padrão')
        plt.xlabel('Distância (m)')
        plt.ylabel('Throughput (Mbps)')
        plt.title('Extra: Estabilidade do Modelo Nakagami')
        plt.legend()
        plt.grid(True)
        plt.savefig('grafico_extra_nakagami.png')
        print("Salvo: grafico_extra_nakagami.png")
        plt.close()

print("\nConcluído! Todos os 5 gráficos (+1 extra) foram gerados.")