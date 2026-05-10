
"""
Sistema de organización de almacén

Estructura de entrada:
lista = [ [cliente_1, lista_obj_des, lista_objetos_Ndes], [...], ... ]

lista_obj_des = [ [obj_des_1, cant_1], [obj_des_2, cant_2], ... , ]
lista_objetos_Ndes = [ [obj_Ndes_1, cant_1], [obj_Ndes_2, cant_2], ... , ]
"""


def organizarAlmazen(lista, n_pal):
    """
    Procesa la lista de clientes y separa objetos deseados y no deseados
    
    Args:
        lista: [ [cliente_1, lista_obj_des, lista_objetos_Ndes], [...], ... ]
        n_pal: número de pallets
    
    Returns:
        objetos_deseados: [[cliente_1, objetos_des_1], [cliente_2, objetos_des_2], ...]
        objetos_no_deseados: [[cliente_1, objetos_Ndes_1], [cliente_2, objetos_Ndes_2], ...]
    """
    objetos_deseados = []
    objetos_no_deseados = []
    
    for cliente_data in lista:
        cliente = cliente_data[0]
        lista_obj_des = cliente_data[1]
        lista_obj_Ndes = cliente_data[2]
        
        objetos_deseados.append([cliente, lista_obj_des])
        objetos_no_deseados.append([cliente, lista_obj_Ndes])
    
    return objetos_deseados, objetos_no_deseados


def distribuirEnPallets(objetos_deseados, objetos_no_deseados, n_pal, max_por_tipo=10):
    """
    Distribuye los objetos en n_pal pallets, agrupando todos los objetos de cada cliente
    en el pallet más vacío disponible.
    Cada pallet tiene 2 listas: una para DESEADO (max 10) y otra para NO DESEADO (max 10)
    Total de almacenamiento por pallet: 20 objetos
    
    Args:
        objetos_deseados: [[cliente, [objetos]], ...]
        objetos_no_deseados: [[cliente, [objetos]], ...]
        n_pal: número de pallets
        max_por_tipo: máximo de objetos por tipo en cada pallet (default: 10)
    
    Returns:
        pallets: lista de n_pal diccionarios, cada uno con sublistas por tipo (max 20 objetos)
    """
    # Crear n_pal diccionarios con listas separadas por tipo
    pallets = [{"DESEADO": [], "NO DESEADO": []} for _ in range(n_pal)]
    
    # Crear diccionario con objetos agrupados por cliente
    clientes_objetos = {}
    
    # Agrupar objetos deseados por cliente
    for cliente, objetos in objetos_deseados:
        if cliente not in clientes_objetos:
            clientes_objetos[cliente] = {"DESEADO": [], "NO DESEADO": []}
        for objeto in objetos:
            clientes_objetos[cliente]["DESEADO"].append({"cliente": cliente, "objeto": objeto})
    
    # Agrupar objetos no deseados por cliente
    for cliente, objetos in objetos_no_deseados:
        if cliente not in clientes_objetos:
            clientes_objetos[cliente] = {"DESEADO": [], "NO DESEADO": []}
        for objeto in objetos:
            clientes_objetos[cliente]["NO DESEADO"].append({"cliente": cliente, "objeto": objeto})
    
    # Distribuir todos los objetos de cada cliente juntos
    for cliente in clientes_objetos:
        deseados = clientes_objetos[cliente]["DESEADO"]
        no_deseados = clientes_objetos[cliente]["NO DESEADO"]
        
        # Encontrar el pallet más vacío que pueda contener todos los objetos del cliente
        mejor_pallet = -1
        min_espacio_usado = float('inf')
        
        for idx, pallet in enumerate(pallets):
            espacio_usado_actual = len(pallet["DESEADO"]) + len(pallet["NO DESEADO"])
            espacio_disponible_des = max_por_tipo - len(pallet["DESEADO"])
            espacio_disponible_ndes = max_por_tipo - len(pallet["NO DESEADO"])
            
            # Verificar si caben todos los objetos del cliente en este pallet
            if len(deseados) <= espacio_disponible_des and len(no_deseados) <= espacio_disponible_ndes:
                if espacio_usado_actual < min_espacio_usado:
                    mejor_pallet = idx
                    min_espacio_usado = espacio_usado_actual
        
        if mejor_pallet != -1:
            pallets[mejor_pallet]["DESEADO"].extend(deseados)
            pallets[mejor_pallet]["NO DESEADO"].extend(no_deseados)
    
    # Convertir a lista de listas con nombre del palet
    palets = []
    for idx, pallet in enumerate(pallets):
        nombre = f"Pallet_{idx + 1}"
        palets.append([nombre, pallet["DESEADO"], pallet["NO DESEADO"]])
    
    return palets


# Ejemplo de uso
if __name__ == "__main__":
    lista = [
        ['Cliente_1', [['Objeto_A', 5], ['Objeto_B', 3], ['Objeto_C', 2], ['Objeto_D', 1]], [['Objeto_E', 2], ['Objeto_F', 1], ['Objeto_G', 1]]],
        ['Cliente_2', [['Objeto_H', 4], ['Objeto_I', 2]], [['Objeto_J', 1], ['Objeto_K', 2], ['Objeto_L', 1], ['Objeto_M', 1]]],
        ['Cliente_3', [['Objeto_N', 2], ['Objeto_O', 1]], [['Objeto_P', 3], ['Objeto_Q', 1], ['Objeto_R', 2]]],
        ['Cliente_4', [['Objeto_S', 1], ['Objeto_T', 2]], [['Objeto_U', 1], ['Objeto_V', 1]]],
    ]
    
    n_pal = 3
    
    des, no_des = organizarAlmazen(lista, n_pal)
    pallets = distribuirEnPallets(des, no_des, n_pal, max_por_tipo=10)
    print(pallets)



