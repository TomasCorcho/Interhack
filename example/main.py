import networkx as nx
import matplotlib.pyplot as plt
import Calcular_costo
import random

# --- Grafo aleatorio de 20 nodos comentado ---
# import random
# G = nx.complete_graph(20)
# for (u, v) in G.edges():
#     G.edges[u, v]['weight'] = random.randint(1, 100)

# --- Nuevo grafo dirigido con los datos reales ---
G = nx.DiGraph()

edges_data = [
    # Desde DDI MOLLET
    ("DDI MOLLET", "Bar Esperanza", 6), ("DDI MOLLET", "Brother's", 7),
    ("DDI MOLLET", "MAFALDA", 7), ("DDI MOLLET", "C. Esclat", 6),
    ("DDI MOLLET", "Bar La Gamba", 9), ("DDI MOLLET", "Castellers", 8),
    
    # Desde Bar Esperanza
    ("Bar Esperanza", "DDI MOLLET", 8), ("Bar Esperanza", "Brother's", 3),
    ("Bar Esperanza", "MAFALDA", 7), ("Bar Esperanza", "C. Esclat", 1),
    ("Bar Esperanza", "Bar La Gamba", 6), ("Bar Esperanza", "Castellers", 6),
    
    # Desde Brother's
    ("Brother's", "DDI MOLLET", 8), ("Brother's", "Bar Esperanza", 2),
    ("Brother's", "MAFALDA", 7), ("Brother's", "C. Esclat", 2),
    ("Brother's", "Bar La Gamba", 5), ("Brother's", "Castellers", 5),
    
    # Desde MAFALDA
    ("MAFALDA", "DDI MOLLET", 8), ("MAFALDA", "Bar Esperanza", 1),
    ("MAFALDA", "Brother's", 4), ("MAFALDA", "C. Esclat", 2),
    ("MAFALDA", "Bar La Gamba", 5), ("MAFALDA", "Castellers", 5),
    
    # Desde C. Esclat
    ("C. Esclat", "DDI MOLLET", 7), ("C. Esclat", "Bar Esperanza", 1),
    ("C. Esclat", "Brother's", 2), ("C. Esclat", "MAFALDA", 2),
    ("C. Esclat", "Bar La Gamba", 7), ("C. Esclat", "Castellers", 7),
    
    # Desde Bar La Gamba
    ("Bar La Gamba", "DDI MOLLET", 10), ("Bar La Gamba", "Bar Esperanza", 4),
    ("Bar La Gamba", "Brother's", 4), ("Bar La Gamba", "MAFALDA", 9),
    ("Bar La Gamba", "C. Esclat", 5), ("Bar La Gamba", "Castellers", 6),
    
    # Desde Castellers
    ("Castellers", "DDI MOLLET", 10), ("Castellers", "Bar Esperanza", 5),
    ("Castellers", "Brother's", 5), ("Castellers", "MAFALDA", 10),
    ("Castellers", "C. Esclat", 6), ("Castellers", "Bar La Gamba", 2)
]

G.add_weighted_edges_from(edges_data)

# Añadir 5 minutos de tiempo de carga a todos los nodos
for nodo in G.nodes():
    G.nodes[nodo]['tiempo_carga'] = 5

# Intervalos de bloqueo: la mitad de los clientes no puede recibir de t=0 a t=30
nodos_bloqueados_1=["Bar Esperanza", "Bar La Gamba"]
for nodo in nodos_bloqueados_1:
        G.nodes[nodo]['intervalo_tiempo'] = (0, 30)

nodos_bloqueados_2 = ["Castellers","MAFALDA"]
for nodo in nodos_bloqueados_2:
    G.nodes[nodo]['intervalo_tiempo'] = (30, 100)

print(G.nodes())
print(G.edges(data=True))

pos = nx.spring_layout(G)

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=500,
    font_size=10,
    connectionstyle='arc3, rad=0.3'
)

labels = nx.get_edge_attributes(G, "weight")
if len(G.nodes()) <= 10:
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, label_pos=0.3)
plt.show()

# --- Integración con funciones.py ---
import funciones

# Preparar grafo para funciones.py (diccionario de adyacencia)
graph_dict = {}
for u, v, data in G.edges(data=True):
    weight = data.get('weight', 1)
    if u not in graph_dict: graph_dict[u] = {}
    if v not in graph_dict: graph_dict[v] = {}
    graph_dict[u][v] = weight
    graph_dict[v][u] = weight

# --- Función de Held-Karp comentada por tiempo de ejecución en grafos grandes ---
# min_weight, path = funciones.find_min_weight_hamiltonian_path(graph_dict)

# # Crear otra figura para el camino Hamiltoniano
# plt.figure()

# # Dibujar el grafo base pero más claro
# nx.draw(
#     G,
#     pos,
#     with_labels=True,
#     node_size=500,
#     font_size=10,
#     node_color='lightgreen',
#     edge_color='lightgray'
# )
# if len(G.nodes()) <= 10:
#     nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

# # Resaltar el camino Hamiltoniano si existe
# if path:
#     path_edges = list(zip(path, path[1:]))
#     nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3)
#     plt.title(f"Camino Hamiltoniano (Peso: {min_weight})\n{' -> '.join(map(str, path))}")
# else:
#     plt.title("No se encontró Camino Hamiltoniano")

# plt.show()

# --- Ejemplo de los N mejores caminos (con 2-Opt) ---
n_caminos = 1000
nodo_inicial = "DDI MOLLET" # Fijo en el vértice inicial

print("\nCalculando 1000 caminos con 2-Opt... (esto será rápido)")
top_paths = funciones.find_top_n_hamiltonian_paths_2opt(
    graph_dict, 
    n=n_caminos, 
    start_node=nodo_inicial, 
    num_samples=5000
)

print(f"\n--- Se encontraron {len(top_paths)} rutas únicas optimizadas ---")
print("Mostrando el top 15 en consola:")
for i, (weight, p) in enumerate(top_paths[:15], 1):
    print(f"{i}. Peso: {weight} | Camino: {' -> '.join(map(str, p))}")

# Dibujar SOLO los 15 mejores en una nueva figura con subplots para no colapsar la pantalla
paths_to_plot = top_paths[:15]
if paths_to_plot:
    import math
    num_plots = len(paths_to_plot)
    cols = min(5, num_plots)
    rows = math.ceil(num_plots / cols)
    
    plt.figure(figsize=(4 * cols, 4 * rows))
    
    for i, (weight, p) in enumerate(paths_to_plot, 1):
        plt.subplot(rows, cols, i)
        nx.draw(
            G, pos, with_labels=True, node_size=200, font_size=8,
            node_color='lightgreen', edge_color='lightgray',
            connectionstyle='arc3, rad=0.3'
        )
        # Se eliminaron los textos de pesos en los ejes para limpiar la visualización
        
        path_edges = list(zip(p, p[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='purple', width=2, connectionstyle='arc3, rad=0.3')
        plt.title(f"Top {i} (Peso: {weight})")
        
    plt.suptitle(f"Top {num_plots} Caminos Hamiltonianos encontrados con 2-Opt\n(Inicio forzado en el nodo {nodo_inicial})", fontsize=14)
    plt.tight_layout()
    plt.show()

# Imprimir el peor caso de la lista (el último encontrado)
if top_paths:
    print(top_paths[-1])

# --- EVALUACIÓN DE COSTO REAL ---
print("\n--- Evaluando Costo Real de las Rutas ---")
rutas_nodos = [p for w, p in top_paths]
rutas_con_costo = Calcular_costo.calcular_costos_rutas(G, rutas_nodos, multiplicador_tiempo=1.0)

print(f"Rutas válidas evaluadas: {len(rutas_con_costo)}")
print("Mostrando el top 15 con Costo Real (tiempo de viaje + 5 min carga/nodo):")
for i, (peso_real, p) in enumerate(rutas_con_costo[:15], 1):
    print(f"{i}. Costo Real: {peso_real} min | Camino: {' -> '.join(map(str, p))}")