import networkx as nx

# Variable global tiempo
global tiempo


def calcular_peso_dinamico(grafo, nodo1, nodo2, multiplicador_tiempo):
    """
    Calcula el peso dinámico de una arista basado en el tiempo global.
    
    Fórmula: peso_base + (multiplicador_tiempo * tiempo) + penalización_intervalo
    
    Si el tiempo cae dentro del intervalo_tiempo del nodo, retorna infinito.
    
    Parámetros:
    - grafo: Grafo con las aristas y atributos de nodo
    - nodo1, nodo2: Nodos conectados por la arista
    - multiplicador_tiempo: Factor por el que se multiplica el tiempo (default: 0.5)
    
    Retorna:
    - Peso dinámico (float) o infinito si está en intervalo de bloqueo
    """
    
    # Obtener peso base de la arista
    if grafo.has_edge(nodo1, nodo2):
        peso_base = grafo[nodo1][nodo2]['weight']
    else:
        return float('inf')

    tiempo+= peso_base*multiplicador_tiempo  # Incrementar tiempo global basado en el peso base (simulación de paso del tiempo)
    
    # Verificar si el tiempo cae en el intervalo de bloqueo del nodo2
    for nodo in [nodo2]:
        if grafo.has_node(nodo):
            atributos = grafo.nodes[nodo]
            intervalo = atributos.get('intervalo_tiempo', None)
            
            if intervalo is not None:
                inicio, fin = intervalo
                if inicio <= tiempo <= fin:
                    return float('inf')
    
    # Calcular peso: base + componente temporal

    atributos = grafo.nodes[nodo2]
    tiempoDeCarga = atributos.get('tiempo_carga', None)

    tiempo += tiempoDeCarga 
    return tiempo
                 
def calcular_costos_rutas(grafo, rutas, multiplicadores=None, multiplicador_tiempo=0.5):
    """
    Calcula el costo total de cada ruta en el grafo, considerando pesos dinámicos basados en tiempo.
    
    Parámetros:
    - grafo: Grafo de NetworkX con pesos en las aristas y atributos en nodos
    - rutas: Lista de rutas, donde cada ruta es una lista de nodos [nodo1, nodo2, ..., nodoN]
    - multiplicadores: Diccionario opcional para ajustar el peso de los atributos de nodo
    - multiplicador_tiempo: Factor por el que se multiplica el tiempo en el peso de aristas (default: 0.5)
    
    Retorna:
    - Lista de costos totales para cada ruta
    """
    if multiplicadores is None:
        multiplicadores = {}
    
    penalizacion_carga = multiplicadores.get('penalizacion_carga', 0.1)
    penalizacion_inactivo = multiplicadores.get('penalizacion_inactivo', 5)
    costo_base_nodo = multiplicadores.get('costo_base_nodo', 0)
    
    costos = []
    
    for ruta in rutas:
        tiempo = 0  # Reiniciar tiempo para cada ruta
        costo_total = 0
        ruta_valida = True
        
        # Calcular costo de aristas + factores de nodos
        for i in range(len(ruta) - 1):
            nodo_actual = ruta[i]
            nodo_siguiente = ruta[i + 1]
            
            # Costo de la arista (dinámico basado en tiempo)
            peso = calcular_peso_dinamico(grafo, nodo_actual, nodo_siguiente, multiplicador_tiempo)
            if peso == float('inf'):
                ruta_valida = False
                break
            costo_total += peso
            
        
        # Factores del último nodo
        if ruta_valida:
            ultimo_nodo = ruta[-1]
            peso = calcular_peso_dinamico(grafo, ruta[-1], ruta[0], multiplicador_tiempo)
            costo_total += peso
        
        if ruta_valida:
            costos.append((costo_total,ruta))
        else:
            costos.append(None)
    
    return costos