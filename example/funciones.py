def find_min_weight_hamiltonian_path(graph):
    """
    Encuentra el camino Hamiltoniano de menor peso en un grafo ponderado.
    Utiliza el algoritmo de Held-Karp (Programación Dinámica).
    
    Args:
        graph (dict): Un diccionario que representa la lista de adyacencia del grafo.
                      Ejemplo: {0: {1: 10, 2: 15}, 1: {0: 10, 2: 20}, 2: {0: 15, 1: 20}}
                      
    Returns:
        tuple: (peso_minimo, camino)
               Si no existe un camino Hamiltoniano, devuelve (float('inf'), [])
    """
    nodes = list(graph.keys())
    n = len(nodes)
    if n == 0:
        return 0, []
    if n == 1:
        return 0, [nodes[0]]
        
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    idx_to_node = {i: node for i, node in enumerate(nodes)}
    
    # dp[mask][i] = mínimo peso de un camino que visita el subconjunto de nodos
    # representado por `mask` y termina en el nodo `i`
    dp = [[float('inf')] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]
    
    # Casos base: caminos que comienzan en cada nodo (peso 0 para el primer nodo)
    for i in range(n):
        dp[1 << i][i] = 0
        
    for mask in range(1, 1 << n):
        for u in range(n):
            # Si el nodo u no está en el subconjunto `mask`, saltar
            if not (mask & (1 << u)):
                continue
                
            # Intentar extender el camino desde u hacia sus vecinos v
            for v_node, weight in graph.get(idx_to_node[u], {}).items():
                if v_node not in node_to_idx:
                    continue
                v = node_to_idx[v_node]
                
                # Si v no ha sido visitado en la `mask` actual
                if not (mask & (1 << v)):
                    new_mask = mask | (1 << v)
                    if dp[mask][u] + weight < dp[new_mask][v]:
                        dp[new_mask][v] = dp[mask][u] + weight
                        parent[new_mask][v] = u
                        
    # Encontrar el peso mínimo entre todos los caminos que visitan todos los nodos
    all_visited_mask = (1 << n) - 1
    min_weight = float('inf')
    last_node = -1
    
    for i in range(n):
        if dp[all_visited_mask][i] < min_weight:
            min_weight = dp[all_visited_mask][i]
            last_node = i
            
    if min_weight == float('inf'):
        return float('inf'), []
        
    # Reconstruir el camino desde el final hasta el principio
    path = []
    curr_mask = all_visited_mask
    curr_node = last_node
    
    while curr_node != -1:
        path.append(idx_to_node[curr_node])
        prev_node = parent[curr_mask][curr_node]
        curr_mask ^= (1 << curr_node)
        curr_node = prev_node
        
    # Invertir el camino ya que lo reconstruimos desde el final
    return min_weight, path[::-1]

def find_top_n_hamiltonian_paths(graph, n=1):
    """
    Encuentra los n caminos Hamiltonianos de menor peso en un grafo ponderado.
    Utiliza búsqueda en profundidad (DFS) para explorar todos los caminos posibles.
    
    Args:
        graph (dict): Un diccionario que representa la lista de adyacencia del grafo.
        n (int): El número de caminos a devolver.
                      
    Returns:
        list: Una lista de tuplas (peso, camino) ordenada de menor a mayor peso.
              Si hay menos de n caminos, devuelve todos los encontrados.
    """
    nodes = list(graph.keys())
    num_nodes = len(nodes)
    
    if num_nodes == 0:
        return []
    if num_nodes == 1:
        return [(0, [nodes[0]])]
        
    all_paths = []
    
    def dfs(current_node, visited, current_path, current_weight):
        # Si hemos visitado todos los nodos, es un camino Hamiltoniano
        if len(visited) == num_nodes:
            all_paths.append((current_weight, list(current_path)))
            return
            
        # Explorar vecinos
        for neighbor, weight in graph.get(current_node, {}).items():
            if neighbor not in visited:
                visited.add(neighbor)
                current_path.append(neighbor)
                
                dfs(neighbor, visited, current_path, current_weight + weight)
                
                # Backtracking
                current_path.pop()
                visited.remove(neighbor)
                
    # Iniciar DFS desde cada nodo
    for start_node in nodes:
        dfs(start_node, {start_node}, [start_node], 0)
        
    # Ordenar todos los caminos encontrados por peso (de menor a mayor)
    all_paths.sort(key=lambda x: x[0])
    
    return all_paths[:n]

def find_top_n_hamiltonian_paths_pruned(graph, n=1):
    """
    Encuentra los n caminos Hamiltonianos de menor peso en un grafo ponderado.
    Utiliza búsqueda en profundidad (DFS) con Poda Inteligente (Branch & Bound).
    
    Args:
        graph (dict): Un diccionario que representa la lista de adyacencia del grafo.
        n (int): El número de caminos a devolver.
                      
    Returns:
        list: Una lista de tuplas (peso, camino) ordenada de menor a mayor peso.
    """
    nodes = list(graph.keys())
    num_nodes = len(nodes)
    
    if num_nodes == 0:
        return []
    if num_nodes == 1:
        return [(0, [nodes[0]])]
        
    top_paths = []
    
    def dfs(current_node, visited, current_path, current_weight):
        # 1. PODA (Branch & Bound):
        # Si ya tenemos 'n' caminos, verificamos el peso del peor de ellos.
        # Si el peso actual ya es mayor o igual, podamos (dejamos de explorar esta rama).
        if len(top_paths) == n:
            worst_best_weight = top_paths[-1][0]
            if current_weight >= worst_best_weight:
                return
                
        # Si hemos visitado todos los nodos, es un camino Hamiltoniano
        if len(visited) == num_nodes:
            top_paths.append((current_weight, list(current_path)))
            # Ordenamos para mantener el peor al final
            top_paths.sort(key=lambda x: x[0])
            # Si nos pasamos de n, eliminamos el peor
            if len(top_paths) > n:
                top_paths.pop()
            return
            
        # 2. HEURÍSTICA: Ordenar vecinos por peso de menor a mayor
        # Esto ayuda a encontrar soluciones buenas súper rápido,
        # lo que hace que la poda (Branch & Bound) empiece a descartar ramas mucho antes.
        neighbors = graph.get(current_node, {})
        sorted_neighbors = sorted(neighbors.items(), key=lambda item: item[1])
        
        for neighbor, weight in sorted_neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                current_path.append(neighbor)
                
                dfs(neighbor, visited, current_path, current_weight + weight)
                
                # Backtracking
                current_path.pop()
                visited.remove(neighbor)
                
    # Iniciar DFS desde cada nodo
    for start_node in nodes:
        dfs(start_node, {start_node}, [start_node], 0)
        
    return top_paths

import random

def _calculate_path_weight(graph, path):
    weight = 0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        if v not in graph.get(u, {}):
            return float('inf')
        weight += graph[u][v]
    return weight

def find_top_n_hamiltonian_paths_2opt(graph, n=1000, start_node=None, num_samples=5000):
    """
    Encuentra los n mejores caminos aproximados usando la heurística 2-Opt.
    
    Args:
        graph (dict): Lista de adyacencia del grafo.
        n (int): Número de caminos a devolver.
        start_node (any): Vértice inicial obligatorio.
        num_samples (int): Cuántos caminos aleatorios generar y optimizar.
        
    Returns:
        list: Lista de los n mejores caminos encontrados [(peso, camino), ...]
    """
    nodes = list(graph.keys())
    if not nodes:
        return []
    if len(nodes) == 1:
        return [(0, [nodes[0]])]
        
    if start_node is None:
        start_node = nodes[0]
        
    other_nodes = [node for node in nodes if node != start_node]
    
    unique_paths = set()
    
    for _ in range(num_samples):
        # 1. Generar camino aleatorio que empieza en start_node
        current_path = [start_node] + random.sample(other_nodes, len(other_nodes))
        current_weight = _calculate_path_weight(graph, current_path)
        
        if current_weight != float('inf'):
            unique_paths.add((current_weight, tuple(current_path)))
            
        # 2. Optimización 2-Opt
        improved = True
        while improved:
            improved = False
            best_new_path = None
            best_new_weight = current_weight
            
            # i empieza en 1 para fijar el start_node en la posición 0
            for i in range(1, len(current_path) - 1):
                for j in range(i + 1, len(current_path)):
                    # Invertir el subsegmento desde i hasta j
                    new_path = current_path[:i] + current_path[i:j+1][::-1] + current_path[j+1:]
                    new_weight = _calculate_path_weight(graph, new_path)
                    
                    if new_weight != float('inf'):
                        unique_paths.add((new_weight, tuple(new_path)))
                        
                    if new_weight < best_new_weight:
                        best_new_weight = new_weight
                        best_new_path = new_path
                        
            if best_new_path is not None:
                current_path = best_new_path
                current_weight = best_new_weight
                improved = True
                
    # Ordenar por peso
    sorted_paths = sorted(list(unique_paths), key=lambda x: x[0])
    
    # Devolver los n mejores
    return [(w, list(p)) for w, p in sorted_paths[:n]]
