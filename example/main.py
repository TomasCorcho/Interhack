import networkx as nx
import random
import time
import pandas as pd
import os
import matplotlib.pyplot as plt
import funciones
import Calcular_costo
import clarke_wright
import paletizador
import math

print("--- INICIANDO SIMULADOR LOGÍSTICO (VRP REAL) ---")

# 1. Configuración del problema
CAPACIDAD_CAMION = 360 # 6 palets * 60 unidades

print("Cargando matriz de tiempos desde Excel...")
# Usamos os.path para que encuentre el Excel sin importar desde qué carpeta ejecutes el comando
script_dir = os.path.dirname(os.path.abspath(__file__))
ruta_excel = os.path.join(script_dir, 'matriz_tiempos_25kmh.xlsx')

try:
    df = pd.read_excel(ruta_excel, index_col=0)
except Exception as e:
    print(f"Error al cargar el Excel: {e}")
    exit(1)

nombres_nodos = list(df.columns)
NODO_INICIAL = nombres_nodos[0]
NUM_CLIENTES = len(nombres_nodos) - 1

print(f"Generando red de {NUM_CLIENTES} clientes con datos reales...")
G = nx.DiGraph()

# Agregar nodos y aristas desde el DataFrame
for origen in nombres_nodos:
    for destino in nombres_nodos:
        if origen != destino:
            tiempo = df.loc[origen, destino]
            G.add_edge(origen, destino, weight=tiempo)

total_demanda = 0
for nodo in G.nodes():
    if nodo == NODO_INICIAL:
        G.nodes[nodo]['demanda'] = 0
        G.nodes[nodo]['tiempo_carga'] = 0
    else:
        # Generamos un manifiesto de pedido aleatorio para cada cliente
        # Aumentamos la media y mucho la desviación para simular "grandes clientes"
        # y que el algoritmo pueda demostrar su capacidad de crear Palets Puros (54+ unidades)
        demanda_volumen = max(1.0, round(random.gauss(25, 20)))
        
        inventario = {'caja': 0, 'barril': 0, 'lata': 0}
        
        # Asignamos productos aleatoriamente hasta llegar al volumen de demanda
        vol_actual = 0.0
        while vol_actual < demanda_volumen:
            tipo = random.choice(['caja', 'barril', 'lata'])
            vol_tipo = {'caja': 1.0, 'barril': 4.0, 'lata': 0.8}[tipo]
            if vol_actual + vol_tipo <= demanda_volumen + 2: # Permitimos pasarnos un pelin
                inventario[tipo] += 1
                vol_actual += vol_tipo
            else:
                break
                
        G.nodes[nodo]['inventario'] = inventario
        G.nodes[nodo]['demanda'] = vol_actual
        total_demanda += vol_actual
        
        # El tiempo_carga se inicializa a 0, el paletizador lo reescribirá luego
        G.nodes[nodo]['tiempo_carga'] = 0

print(f"Total de demanda a repartir hoy: {total_demanda} unidades básicas.")
print("Calculando clusters de camiones con Clarke & Wright...")

# 2. Fase de Clustering
start_time = time.time()
clusters = clarke_wright.agrupar_en_clusters(G, NODO_INICIAL, CAPACIDAD_CAMION)
print(f"Clarke & Wright completado en {time.time() - start_time:.2f} segundos.")

num_camiones = len(clusters)
print(f"\nSe han asignado {num_camiones} camiones para la ruta de hoy.")
if num_camiones > 11:
    print("¡ALERTA! Se han superado los 11 camiones disponibles.")

# 3. Fase de Optimización de Rutas (2-Opt) por cada camión
print("\nOptimizando sub-rutas con 2-Opt...")
rutas_finales = []

for i, cluster in enumerate(clusters, 1):
    demanda_cluster = sum(G.nodes[n]['demanda'] for n in cluster)
    
    # --- BIN PACKING: LLAMADA AL PALETIZADOR ---
    palets_generados, tiempos_descarga = paletizador.empaquetar_cluster(cluster, G)
    
    # Inyectar los tiempos dinámicos en el grafo para este camión
    for c, tiempo in tiempos_descarga.items():
        G.nodes[c]['tiempo_carga'] = tiempo
        
    nodos_ruta = [NODO_INICIAL] + cluster
    subgrafo_dict = {u: {v: G[u][v]['weight'] for v in nodos_ruta if v != u} for u in nodos_ruta}
    
    # Num samples 1000 es rápido para clusters de ~15-20 clientes (que es lo que saldrá con 50 clientes y 3 camiones)
    top_paths = funciones.find_top_n_hamiltonian_paths_2opt(subgrafo_dict, n=1, start_node=NODO_INICIAL, num_samples=1000)
    
    mejor_peso, mejor_camino = top_paths[0]
    
    # 4. Calcular costo real (con tiempos de carga dinámicos calculados por el paletizador)
    costos_reales = Calcular_costo.calcular_costos_rutas(G, [mejor_camino], multiplicador_tiempo=1.0)
    costo_final, _ = costos_reales[0]
    
    rutas_finales.append({
        'camion': i,
        'clientes': len(cluster),
        'demanda': demanda_cluster,
        'ruta': mejor_camino,
        'tiempo_viaje': mejor_peso,
        'tiempo_real': costo_final,
        'palets': palets_generados
    })

# 5. Mostrar Resumen Final
print("\n" + "="*100)
print("RESUMEN DE FLOTA, RUTAS Y MANIFIESTO DE CARGA (DATOS REALES)")
print("="*100)

for rf in rutas_finales:
    camino = rf['ruta']
    # Mostramos nombres cortos para no saturar la pantalla
    nombres_cortos = [n.split(',')[0].strip() for n in camino]
    str_camino = " -> ".join(nombres_cortos)
        
    print(f"\n🚚 CAMIÓN {rf['camion']} | Carga Total: {rf['demanda']:.1f}/360 ud. | Entregas: {rf['clientes']} | Tiempo estimado: {rf['tiempo_real']:.0f} min")
    print(f"📍 Ruta: {str_camino}")
    print(f"📦 Manifiesto de Palets ({len(rf['palets'])} palets cargados):")
    
    for idx, p in enumerate(rf['palets'], 1):
        # Limpiar tipo de palet para que se lea mejor
        tipo_limpio = p['tipo'].replace('P1_', '').replace('P2_', '').replace('P3_', '').replace('P4_', '')
        print(f"   ► Palet {idx} [{p['tipo'][:2]}: {tipo_limpio}] - Llenado: {p['volumen_total']:.1f}/60 uds")
        
        # Agrupar contenidos para imprimirlos de forma bonita
        for item in p['contenido']:
            cliente_corto = item['cliente'].split(',')[0].strip()
            print(f"      • {item['cantidad']:>2} x {item['tipo']:<7} -> Destino: {cliente_corto}")
    print("-" * 80)

# 6. Visualización de Grafos
print("Generando visualizaciones lógicas de las rutas...")

for rf in rutas_finales:
    camion_id = rf['camion']
    camino = rf['ruta']
    # El camino ya es un ciclo cerrado, pero para los nodos tomamos los únicos
    nodos_cluster = list(set(camino))
    
    # Crear un subgrafo solo con estos nodos para que el Layout se vea amplio
    H = G.subgraph(nodos_cluster)
    
    # Calcular layout lógico
    pos = nx.spring_layout(H, seed=42)
    
    # Crear ventana con 3 gráficas (Cluster vs Ruta vs Carga)
    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    fig.suptitle(f"Camión {camion_id} - Entregas: {rf['clientes']} - Tiempo estimado: {rf['tiempo_real']:.0f} min", fontsize=16)
    
    # Diccionario de nombres cortos para que quepan en las burbujas
    labels = {n: n.split(',')[0].strip() for n in H.nodes()}
    
    # --- SUBPLOT 1: El Cluster de clientes ---
    ax1 = axes[0]
    ax1.set_title("Grupo de Clientes Asignados (Cluster)")
    # Destacar el almacén en otro color
    colores_cluster = ['orange' if n == NODO_INICIAL else 'lightblue' for n in H.nodes()]
    
    nx.draw_networkx_nodes(H, pos, ax=ax1, node_size=300, node_color=colores_cluster)
    nx.draw_networkx_labels(H, pos, labels, ax=ax1, font_size=8)
    # Dibujamos las conexiones muy tenues para no saturar
    nx.draw_networkx_edges(H, pos, ax=ax1, alpha=0.1)
    
    # --- SUBPLOT 2: La Ruta Óptima (Ciclo Hamiltonian) ---
    ax2 = axes[1]
    ax2.set_title("Ruta Óptima de Reparto (2-Opt)")
    
    colores_ruta = ['orange' if n == NODO_INICIAL else 'lightgreen' for n in H.nodes()]
    nx.draw_networkx_nodes(H, pos, ax=ax2, node_size=300, node_color=colores_ruta)
    nx.draw_networkx_labels(H, pos, labels, ax=ax2, font_size=8)
    
    # Crear las aristas del camino exacto con flechas marcadas
    path_edges = list(zip(camino, camino[1:]))
    nx.draw_networkx_edges(
        H, pos, edgelist=path_edges, ax=ax2, 
        edge_color="purple", width=2, arrows=True, arrowsize=15, 
        connectionstyle="arc3,rad=0.1" # Curvar aristas para ver viajes de ida y vuelta
    )
    
    # --- SUBPLOT 3: Gráfico de Carga de Palets (Tetris) ---
    ax3 = axes[2]
    ax3.set_title("Carga del Camión (Colores por Cliente)")
    
    # Generar paleta de colores para los clientes de este camión (hasta 20 colores distintos)
    cmap = plt.get_cmap('tab20')
    clientes_en_camion = list(set(item['cliente'] for p in rf['palets'] for item in p['contenido']))
    colores_cliente = {cliente: cmap(i % 20) for i, cliente in enumerate(clientes_en_camion)}
    
    x_labels = []
    
    # Línea que marca la capacidad máxima del palet (60 unidades básicas)
    ax3.axhline(y=60, color='red', linestyle='--', alpha=0.5, label='Límite Palet (60 uds)')
    
    for idx_palet, p in enumerate(rf['palets']):
        x_pos = idx_palet
        tipo_corto = p['tipo'].split('_')[0] # P1, P2, P3 o P4
        x_labels.append(f"Palet {idx_palet+1}\n({tipo_corto})")
        
        current_bottom = 0.0
        
        for item in p['contenido']:
            vol_item = item['cantidad'] * {'caja': 1.0, 'barril': 4.0, 'lata': 0.8}[item['tipo']]
            cliente = item['cliente']
            
            # Dibujar el bloque coloreado por cliente
            ax3.bar(x_pos, vol_item, bottom=current_bottom, color=colores_cliente[cliente], edgecolor='white', linewidth=1)
            
            # Etiqueta de texto dentro del bloque si es suficientemente grande para que se lea
            if vol_item > 4.0:
                cliente_str = cliente.split(',')[0].strip()[:12] # Acortar el nombre
                texto = f"{cliente_str}\n({item['cantidad']} {item['tipo']}s)"
                # Usamos color negro con negrita, que suele leerse bien sobre los colores pastel de tab20
                ax3.text(x_pos, current_bottom + (vol_item/2), texto, 
                         ha='center', va='center', color='black', fontsize=7, fontweight='bold')
            
            current_bottom += vol_item
            
    ax3.set_xticks(range(len(rf['palets'])))
    ax3.set_xticklabels(x_labels)
    ax3.set_ylabel("Volumen (Unidades Básicas)")
    ax3.set_ylim(0, 65)
    
    # No ponemos leyenda porque ocuparía demasiado espacio y ya tenemos los nombres escritos en los bloques
    
    plt.tight_layout()

print("Mostrando ventanas gráficas... (Cierra las ventanas emergentes para terminar el programa)")
plt.show()

print("--- FIN DE LA SIMULACIÓN ---")