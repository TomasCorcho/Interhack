import math

def empaquetar_cluster(nodos_cluster, grafo):
    """
    Recibe la lista de clientes de un camión y el grafo con sus inventarios.
    Aplica 4 prioridades para empaquetar en palets de 60 uds básicas.
    Retorna los palets generados y los minutos de descarga por cliente.
    """
    CAPACIDAD_PALET = 60.0
    UMBRAL_PURO = 54.0 # 90%
    volumen_tipo = {'caja': 1.0, 'barril': 4.0, 'lata': 0.8}
    
    palets_generados = []
    
    # Clonar el inventario para ir restando lo que empaquetamos
    pendientes = {}
    for c in nodos_cluster:
        inv = grafo.nodes[c].get('inventario', {})
        if inv:
            pendientes[c] = inv.copy()

    def crear_palet(tipo_palet, cliente_exclusivo=None):
        return {
            'tipo': tipo_palet, 
            'cliente': cliente_exclusivo,
            'contenido': [], 
            'volumen_total': 0.0
        }

    # --- PRIORIDAD 1: Puro Cliente + Producto (>= 54 vol) ---
    for c, inventario in pendientes.items():
        for tipo, cant in list(inventario.items()):
            vol_unit = volumen_tipo[tipo]
            while cant * vol_unit >= UMBRAL_PURO:
                # Metemos hasta 60 uds físicas
                max_uds_posibles = math.floor(CAPACIDAD_PALET / vol_unit)
                uds_a_meter = min(cant, max_uds_posibles)
                
                p = crear_palet('P1_ClienteProducto', c)
                p['contenido'].append({'cliente': c, 'tipo': tipo, 'cantidad': uds_a_meter})
                p['volumen_total'] = uds_a_meter * vol_unit
                palets_generados.append(p)
                
                cant -= uds_a_meter
                pendientes[c][tipo] = cant

    # --- PRIORIDAD 2: Puro Cliente (Mix de productos) >= 54 vol ---
    for c, inventario in pendientes.items():
        vol_restante_cliente = sum(cant * volumen_tipo[t] for t, cant in inventario.items())
        while vol_restante_cliente >= UMBRAL_PURO:
            p = crear_palet('P2_PuroCliente', c)
            espacio_libre = CAPACIDAD_PALET
            
            for tipo in list(inventario.keys()):
                cant = inventario[tipo]
                if cant == 0: continue
                vol_unit = volumen_tipo[tipo]
                
                uds_que_caben = math.floor(espacio_libre / vol_unit)
                if uds_que_caben > 0:
                    uds_a_meter = min(cant, uds_que_caben)
                    p['contenido'].append({'cliente': c, 'tipo': tipo, 'cantidad': uds_a_meter})
                    p['volumen_total'] += uds_a_meter * vol_unit
                    espacio_libre -= uds_a_meter * vol_unit
                    inventario[tipo] -= uds_a_meter
            
            palets_generados.append(p)
            vol_restante_cliente = sum(cant * volumen_tipo[t] for t, cant in inventario.items())

    # --- PRIORIDAD 3: Puro Producto (Multi-cliente) >= 54 vol ---
    for tipo in ['barril', 'caja', 'lata']:
        vol_unit = volumen_tipo[tipo]
        while sum(pendientes[c].get(tipo, 0) for c in pendientes) * vol_unit >= UMBRAL_PURO:
            p = crear_palet('P3_PuroProducto')
            espacio_libre = CAPACIDAD_PALET
            
            for c in list(pendientes.keys()):
                cant = pendientes[c].get(tipo, 0)
                if cant == 0: continue
                
                uds_que_caben = math.floor(espacio_libre / vol_unit)
                if uds_que_caben > 0:
                    uds_a_meter = min(cant, uds_que_caben)
                    p['contenido'].append({'cliente': c, 'tipo': tipo, 'cantidad': uds_a_meter})
                    p['volumen_total'] += uds_a_meter * vol_unit
                    espacio_libre -= uds_a_meter * vol_unit
                    pendientes[c][tipo] -= uds_a_meter
                    
            palets_generados.append(p)

    # --- PRIORIDAD 4: Tetris Mixto ---
    p_actual = crear_palet('P4_Mixto')
    for c, inventario in pendientes.items():
        for tipo, cant in list(inventario.items()):
            while cant > 0:
                vol_unit = volumen_tipo[tipo]
                uds_que_caben = math.floor((CAPACIDAD_PALET - p_actual['volumen_total']) / vol_unit)
                
                if uds_que_caben == 0: # Palet lleno
                    if p_actual['volumen_total'] > 0:
                        palets_generados.append(p_actual)
                    p_actual = crear_palet('P4_Mixto')
                    continue
                    
                uds_a_meter = min(cant, uds_que_caben)
                p_actual['contenido'].append({'cliente': c, 'tipo': tipo, 'cantidad': uds_a_meter})
                p_actual['volumen_total'] += uds_a_meter * vol_unit
                cant -= uds_a_meter
                pendientes[c][tipo] -= uds_a_meter
                
    if p_actual['volumen_total'] > 0:
        palets_generados.append(p_actual)
        
    # --- CALCULAR TIEMPOS DE DESCARGA DINÁMICOS ---
    # 1 min si te dejan el palet exclusivo
    # 10 mins si el chófer tiene que buscar tus cosas en un palet mixto
    tiempos_descarga = {c: 0 for c in nodos_cluster}
    
    for p in palets_generados:
        if p['tipo'] in ['P1_ClienteProducto', 'P2_PuroCliente'] and p['cliente'] is not None:
            tiempos_descarga[p['cliente']] += 1
        elif p['tipo'] in ['P3_PuroProducto', 'P4_Mixto']:
            clientes_implicados = set(item['cliente'] for item in p['contenido'])
            for c in clientes_implicados:
                tiempos_descarga[c] += 10
                
    # Si algún cliente no recibió palets (pedido 0), le ponemos 5 min por si acaso
    for c in tiempos_descarga:
        if tiempos_descarga[c] == 0:
            tiempos_descarga[c] = 5
            
    return palets_generados, tiempos_descarga
