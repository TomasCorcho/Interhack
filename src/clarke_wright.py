import networkx as nx

def agrupar_en_clusters(grafo, nodo_inicial, capacidad_maxima):
    """
    Agrupa nodos usando el algoritmo de Ahorros de Clarke y Wright.
    Retorna una lista de clusters (cada cluster es una lista de nodos).
    """
    # 1. Obtener todos los clientes (excluyendo el nodo inicial)
    clientes = [n for n in grafo.nodes() if n != nodo_inicial]
    
    # 2. Inicializar rutas individuales y demandas
    rutas = {c: [c] for c in clientes} # clave: ID de cliente, valor: lista de nodos en la ruta
    demandas_ruta = {c: grafo.nodes[c].get('demanda', 0) for c in clientes}
    
    # Un diccionario rápido para saber a qué ruta pertenece un cliente
    cliente_a_ruta = {c: c for c in clientes}
    
    # 3. Calcular matriz de ahorros
    # Ahorro S(i,j) = Costo(DDI, i) + Costo(j, DDI) - Costo(i, j)
    ahorros = []
    for i in clientes:
        for j in clientes:
            if i != j:
                # Nos aseguramos de que existan las aristas
                if grafo.has_edge(nodo_inicial, i) and grafo.has_edge(j, nodo_inicial) and grafo.has_edge(i, j):
                    c_0i = grafo[nodo_inicial][i]['weight']
                    c_j0 = grafo[j][nodo_inicial]['weight']
                    c_ij = grafo[i][j]['weight']
                    
                    ahorro = c_0i + c_j0 - c_ij
                    ahorros.append((ahorro, i, j))
                    
    # 4. Ordenar ahorros de mayor a menor
    ahorros.sort(key=lambda x: x[0], reverse=True)
    
    # 5. Fusión de rutas
    for ahorro, i, j in ahorros:
        ruta_i_id = cliente_a_ruta[i]
        ruta_j_id = cliente_a_ruta[j]
        
        # Si ya están en la misma ruta, saltar
        if ruta_i_id == ruta_j_id:
            continue
            
        ruta_i = rutas[ruta_i_id]
        ruta_j = rutas[ruta_j_id]
        
        # Para unir i con j, 'i' debe ser el último de su ruta y 'j' el primero de la suya
        if ruta_i[-1] == i and ruta_j[0] == j:
            # Comprobar capacidad
            demanda_total = demandas_ruta[ruta_i_id] + demandas_ruta[ruta_j_id]
            
            if demanda_total <= capacidad_maxima:
                # FUSIONAR!
                # La nueva ruta será la unión. Mantenemos el ID de ruta_i_id
                nueva_ruta = ruta_i + ruta_j
                rutas[ruta_i_id] = nueva_ruta
                demandas_ruta[ruta_i_id] = demanda_total
                
                # Actualizar el diccionario de referencias para todos los nodos movidos
                for nodo_movido in ruta_j:
                    cliente_a_ruta[nodo_movido] = ruta_i_id
                    
                # Eliminar la ruta antigua de j
                del rutas[ruta_j_id]
                del demandas_ruta[ruta_j_id]

    # Extraer las listas finales
    clusters = list(rutas.values())
    return clusters
