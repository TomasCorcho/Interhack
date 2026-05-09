import networkx as nx

def calcular_peso_dinamico(grafo, nodo1, nodo2, multiplicador_tiempo, tiempo_actual):
    """
    Calcula el tiempo de llegada al nodo2, considerando el tiempo de viaje y pausas.
    """
    if not grafo.has_edge(nodo1, nodo2):
        return float('inf')

    # Sumamos el tiempo de viaje
    peso_base = grafo[nodo1][nodo2]['weight']
    tiempo_llegada = tiempo_actual + (peso_base * multiplicador_tiempo)
    
    # Comprobamos intervalos de bloqueo en el nodo destino
    atributos = grafo.nodes[nodo2] if grafo.has_node(nodo2) else {}
    intervalo = atributos.get('intervalo_tiempo', None)
    
    if intervalo is not None:
        inicio, fin = intervalo
        if inicio <= tiempo_llegada <= fin:
            return float('inf')  # Choca con un bloqueo
            
    # Añadimos el tiempo de carga en el nodo destino
    tiempo_carga = atributos.get('tiempo_carga', 0)
    tiempo_salida = tiempo_llegada + tiempo_carga
    
    return tiempo_salida
                 
def calcular_costos_rutas(grafo, rutas, multiplicador_tiempo=1.0):
    """
    Calcula el tiempo total real de cada ruta en el grafo.
    """
    costos = []
    
    for ruta in rutas:
        tiempo_actual = 0  # Empezamos en el minuto 0
        ruta_valida = True
        
        for i in range(len(ruta) - 1):
            nodo_actual = ruta[i]
            nodo_siguiente = ruta[i + 1]
            
            tiempo_actual = calcular_peso_dinamico(grafo, nodo_actual, nodo_siguiente, multiplicador_tiempo, tiempo_actual)
            
            if tiempo_actual == float('inf'):
                ruta_valida = False
                break
                
        # Calcular el regreso al nodo inicial
        if ruta_valida:
            tiempo_actual = calcular_peso_dinamico(grafo, ruta[-1], ruta[0], multiplicador_tiempo, tiempo_actual)
            if tiempo_actual == float('inf'):
                ruta_valida = False
                
        if ruta_valida:
            costos.append((tiempo_actual, ruta))
    
    # Ordenar por el tiempo total (costo real)
    costos.sort(key=lambda x: x[0])
    return costos