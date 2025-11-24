# utils/tramo_utils.py
import os
from pathlib import Path

def calcular_tramo_para_defecto(imagen_path, imagenes_completas, largo_total_correa, 
                               tramos_info=None, secciones_correa=5, desplazamiento_inicial=0):
    """
    Calcula el tramo para un defecto considerando el desplazamiento inicial
    """

    print(f"=== CÁLCULO TRAMO PARA: {os.path.basename(imagen_path)} ===")
    print(f"Total imágenes: {len(imagenes_completas) if imagenes_completas else 0}")
    print(f"Largo total correa: {largo_total_correa}")
    print(f"Desplazamiento inicial: {desplazamiento_inicial}")    
    print(f"=== CÁLCULO TRAMO PARA: {os.path.basename(imagen_path)} ===")
    if not imagenes_completas or not largo_total_correa:
        return 0
    
    try:
        # Encuentra el índice de la imagen actual
        imagen_actual = os.path.basename(imagen_path)
        indice = next((i for i, img in enumerate(imagenes_completas) 
                      if os.path.basename(img) == imagen_actual), 0)
        
        # Calcula metros DESDE EL INICIO DE LA CORREA (no desde el inicio de grabación)
        proporcion = indice / len(imagenes_completas)
        metros_desde_inicio_grabacion = proporcion * largo_total_correa
        
        # Ajustar para considerar el desplazamiento inicial
        metros_desde_inicio_correa = desplazamiento_inicial + metros_desde_inicio_grabacion
        
        # Si tenemos información específica de los tramos, usarla
        if tramos_info and len(tramos_info) == secciones_correa:
            return calcular_tramo_con_longitudes_reales(metros_desde_inicio_correa, tramos_info)
        else:
            # Fallback: cálculo uniforme
            return calcular_tramo_uniforme(metros_desde_inicio_correa, largo_total_correa, secciones_correa)
    
    except Exception as e:
        print(f"Error calculando tramo: {e}")
        return 0

def calcular_tramo_con_longitudes_reales(metros, tramos_info):
    """
    Calcula el tramo basado en las longitudes reales de cada tramo
    """
    metros_acumulados = 0
    
    for tramo in sorted(tramos_info, key=lambda x: x['numero']):
        metros_acumulados += tramo['largo']
        if metros <= metros_acumulados:
            return tramo['numero']
    
    return tramos_info[-1]['numero'] if tramos_info else 0

def calcular_tramo_uniforme(metros, largo_total, secciones_correa):
    """
    Calcula el tramo de manera uniforme
    """
    if largo_total <= 0 or secciones_correa <= 0:
        return 0
        
    metros_por_tramo = largo_total / secciones_correa
    tramo = min(int(metros // metros_por_tramo), secciones_correa - 1)
    return tramo + 1

# En video_processor.py o donde procesas el video
def calcular_desplazamiento_inicial(tramo_inicial, distancia_siguiente, tramos_info):
    """
    Calcula cuántos metros hay desde el INICIO de la correa hasta el PUNTO DE INICIO de grabación
    
    tramo_inicial: Número del tramo donde comienza la grabación
    distancia_siguiente: Metros que faltan para llegar al tramo_inicial
    tramos_info: Lista de tramos con sus longitudes
    """
    if not tramos_info:
        return 0
    
    # Ordenar tramos por número
    tramos_ordenados = sorted(tramos_info, key=lambda x: x['numero'])
    
    # Sumar longitudes de todos los tramos ANTERIORES al tramo_inicial
    metros_hasta_tramo = 0
    for tramo in tramos_ordenados:
        if tramo['numero'] < tramo_inicial:
            metros_hasta_tramo += tramo['largo']
        else:
            break
    
    # El punto de inicio está ANTES del tramo_inicial por la distancia_siguiente
    desplazamiento = metros_hasta_tramo - distancia_siguiente
    
    # Asegurar que no sea negativo
    return max(0, desplazamiento)