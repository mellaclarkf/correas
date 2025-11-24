from utils.value_utils import normalizar_valor, limpiar_valor
from tkinter import font as tkFont
import pandas as pd
import os
from utils.tramo_utils import calcular_tramo_para_defecto

"""
    Inserta los defectos en el Treeview y guarda las etiquetas originales.
    Actualizado para incluir eje_y2.
"""
def insertar_defectos_en_treeview(treeview, resultado, file_path, etiquetas_originales, pixeles_por_metro=1000, 
                                  largo_total_correa=None, imagenes_completas=None, secciones_correa=5, tramos_info=None
                                  , desplazamiento_inicial=0):
    if resultado.empty:
        return

    # Prepara un diccionario para mapear nombres de imagen a índices
    imagen_a_indice = {os.path.basename(img): i for i, img in enumerate(imagenes_completas)} if imagenes_completas else {}

    for index, row in resultado.iterrows():
        id_registro = row.get("id")
        if pd.isna(id_registro) or id_registro == "" or str(id_registro) in treeview.get_children():
            id_registro = f"{index}"

        # OBTENER LA RUTA CORRECTA DE LA IMAGEN
        imagen_path = row.get("image_path", "")
        
        # Si no hay ruta de imagen, buscar una alternativa válida
        if not imagen_path or not os.path.exists(imagen_path):
            # Intentar encontrar la imagen correspondiente en imagenes_completas
            if imagenes_completas and index < len(imagenes_completas):
                imagen_path = imagenes_completas[index]
            else:
                # Si no se puede encontrar, usar un valor por defecto seguro
                imagen_path = ""

        # Calcular dimensiones en metros (ancho y alto)
        ancho = abs(float(row["eje_x2"]) - float(row["eje_x"])) / pixeles_por_metro
        alto = abs(float(row["eje_y2"]) - float(row["eje_y"])) / pixeles_por_metro

        # Calcular distancia real
        largo = 0.0
        if largo_total_correa and imagenes_completas and imagen_path:
            try:
                imagen_registro = os.path.basename(imagen_path)
                if imagen_registro in imagen_a_indice:
                    indice = imagen_a_indice[imagen_registro]
                    # METROS DESDE INICIO CORREA (no desde inicio grabación)
                    largo = desplazamiento_inicial + ((indice / len(imagenes_completas)) * largo_total_correa)
            except Exception as e:
                print(f"Error calculando distancia: {e}")

        # Cálculo del tramo CON DESPLAZAMIENTO
        tramo = calcular_tramo_para_defecto(
            imagen_path=imagen_path,
            imagenes_completas=imagenes_completas,
            largo_total_correa=largo_total_correa,
            tramos_info=tramos_info,
            secciones_correa=secciones_correa,
            desplazamiento_inicial=desplazamiento_inicial  
        )

        # Crear tag con coordenadas
        coords_tag = f"coords_{row['eje_x']}_{row['eje_y']}_{row['eje_x2']}_{row['eje_y2']}"
        nombre_archivo = os.path.basename(imagen_path)
        # Insertar en treeview CON LA RUTA CORRECTA
        treeview.insert("", "end", 
                      iid=str(id_registro),
                      tags=(coords_tag,),
                      values=(
                          id_registro,
                          nombre_archivo,
                          f"{ancho:.3f}",
                          f"{alto:.3f}",
                          f"{largo:.3f}",  # Distancia real en metros
                          row["etiqueta"] if row["etiqueta"] is not None else "CONFIRMAR",
                          row.get("prediccion", ""),
                          imagen_path,  
                          tramo
                      ))

        etiquetas_originales[str(id_registro)] = row["etiqueta"]

def insertar_defecto_individual(treeview, registro, etiquetas_originales, pixeles_por_metro=1000):
    correlativo = len(treeview.get_children())
    id_registro = str(correlativo)

    # Calcular dimensiones
    ancho = abs(float(registro['x2']) - float(registro['x'])) / pixeles_por_metro
    alto = abs(float(registro['y2']) - float(registro['y'])) / pixeles_por_metro
    largo = float(registro.get('largo', 0)) / pixeles_por_metro

    # Crear tag con coordenadas
    coords_tag = f"coords_{registro['x']}_{registro['y']}_{registro['x2']}_{registro['y2']}"

    treeview.insert("", "end",
                  iid=id_registro,
                  tags=(coords_tag,),
                  values=(
                      id_registro,
                      f"Falla_{correlativo}",
                      f"{ancho:.3f}",
                      f"{alto:.3f}",
                      f"{largo:.3f}",
                      registro['defecto'],
                      registro.get('prediccion', registro['defecto']),
                      registro['image_path']
                  ))

    etiquetas_originales[id_registro] = registro['defecto']

def obtener_filas_modificadas(treeview, etiquetas_originales):
    """
    Obtiene las filas con etiquetas modificadas en el Treeview.
    Devuelve lista de tuplas: (item_id, etiqueta_actual, etiqueta_original)
    """
    filas_modificadas = []

    for item_id in treeview.get_children():
        valores = treeview.item(item_id)["values"]
        
        # Asegurar que hay suficientes columnas
        if len(valores) < 6:  # Solo necesitamos hasta la columna Etiqueta (índice 5)
            continue
            
        id_registro = valores[0]
        etiqueta_actual = valores[5]  # Columna Etiqueta
        
        # Limpiar y normalizar valores
        etiqueta_actual_limpia = limpiar_valor(etiqueta_actual)
        etiqueta_original = etiquetas_originales.get(str(id_registro), None)
        etiqueta_original_limpia = limpiar_valor(etiqueta_original) if etiqueta_original else None
        
        es_modificado = False
        
        if etiqueta_original_limpia is None or etiqueta_original_limpia == "CONFIRMAR":
            # Caso 1: Original era None/Confirmar, actual es diferente
            if etiqueta_actual_limpia and etiqueta_actual_limpia != "CONFIRMAR":
                es_modificado = True
        else:
            # Caso 2: Original tenía valor, verificar si cambió
            if etiqueta_actual_limpia != etiqueta_original_limpia:
                es_modificado = True
        
        if es_modificado:
            filas_modificadas.append((item_id, etiqueta_actual_limpia, etiqueta_original_limpia))

    return filas_modificadas

def configurar_columnas_treeview(treeview, columnas):
    """
    Configura las columnas de un Treeview dado.
    """
    for col in columnas:
        treeview.heading(col, text=col)
        treeview.column(col, width=70, anchor="center", stretch=True)

def ajustar_ancho_columnas(treeview):
    """
    Ajusta el ancho de las columnas según su contenido,
    asegurando que la columna 'Path' permanezca oculta.
    """
    f = tkFont.Font()
    for col in treeview["columns"]:
        # --- oculta columna Path ---
        if col == "Path":
            # Asegurarse de que la columna 'Path' permanezca oculta
            treeview.column(col, width=0, stretch=False)
            continue  # Salta el resto del bucle para esta columna y pasa a la siguiente

        max_width = f.measure(col)  # Ancho inicial basado en el título de la columna

        # Recorre todos los elementos (filas) para encontrar el ancho máximo del contenido
        for item in treeview.get_children():
            try:
                # Obtener el valor de la celda para la columna actual
                # treeview["columns"] devuelve los nombres de las columnas, necesitamos su índice
                col_index = list(treeview["columns"]).index(col)
                cell_value = treeview.item(item, "values")[col_index]
                
                if cell_value is not None:
                    max_width = max(max_width, f.measure(str(cell_value)))
            except (ValueError, IndexError):
                # Manejar casos donde la columna no se encuentra o el índice es inválido
                pass

        # Añade un pequeño padding para que el texto no quede pegado
        max_width += 10 

# def calcular_tramo(imagen_path, imagenes_completas, largo_total, secciones_correa, tramos_info=None):
#     """
#     Calcula el tramo basado en la posición de la imagen y las longitudes reales de los tramos.
    
#     Args:
#         imagen_path: Ruta de la imagen actual
#         imagenes_completas: Lista de todas las imágenes
#         largo_total: Largo total de la correa
#         secciones_correa: Número de tramos
#         tramos_info: Lista de diccionarios con información de cada tramo [OPCIONAL]
#                     Ejemplo: [{'numero': 1, 'largo': 800}, {'numero': 2, 'largo': 600}, ...]
    
#     Returns:
#         Número del tramo (1-based)
#     """
#     if not imagenes_completas or not largo_total or not secciones_correa:
#         return 0
    
#     try:
#         # Encuentra el índice de la imagen actual
#         imagen_actual = os.path.basename(imagen_path)
#         indice = next((i for i, img in enumerate(imagenes_completas) 
#                       if os.path.basename(img) == imagen_actual), 0)
        
#         # Calcula metros (usando el sistema actual)
#         proporcion = indice / len(imagenes_completas)
#         metros = proporcion * largo_total
        
#         # Si tenemos información específica de los tramos, usarla
#         if tramos_info and len(tramos_info) == secciones_correa:
#             return calcular_tramo_con_longitudes_reales(metros, tramos_info)
#         else:
#             # Fallback: cálculo uniforme (como antes)
#             return calcular_tramo_uniforme(metros, largo_total, secciones_correa)
    
#     except Exception as e:
#         print(f"Error calculando tramo: {e}")
#         return 0
    
# def calcular_tramo_con_longitudes_reales(metros, tramos_info):
#     """
#     Calcula el tramo basado en las longitudes reales de cada tramo.
    
#     Args:
#         metros: Posición actual en metros
#         tramos_info: Lista de diccionarios con información de cada tramo
#                     Debe estar ordenada por número de tramo
#                     Ejemplo: [{'numero': 1, 'largo': 800}, {'numero': 2, 'largo': 600}, ...]
    
#     Returns:
#         Número del tramo (1-based)
#     """
#     metros_acumulados = 0
    
#     for tramo in sorted(tramos_info, key=lambda x: x['numero']):
#         metros_acumulados += tramo['largo']
#         if metros <= metros_acumulados:
#             return tramo['numero']
    
#     # Si excede el último tramo, retornar el último
#     return tramos_info[-1]['numero']
    
# def calcular_tramo_uniforme(metros, largo_total, secciones_correa):
#     """
#     Calcula el tramo de manera uniforme (para cuando no hay información específica).
#     """
#     metros_por_tramo = largo_total / secciones_correa
#     tramo = min(int(metros // metros_por_tramo), secciones_correa - 1)
#     return tramo + 1  # Retorna tramo 1-based (1, 2, 3...)