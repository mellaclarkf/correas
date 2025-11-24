import numpy as np
import pandas as pd

def normalizar_valor(valor):
    """
    Normaliza un valor para comparación (mayúsculas, sin espacios)
    """
    if valor is None:
        return None
    return str(valor).upper().strip()

def limpiar_valor(valor):
    """
    Limpia y normaliza un valor, manejando casos None y vacíos
    """
    if valor is None:
        return None
    valor_str = str(valor).strip()
    return valor_str.upper() if valor_str else None

def convertir_a_python(valor):
    if pd.isna(valor):
        return None
    elif isinstance(valor, (np.integer, np.int32, np.int64)):
        return int(valor)
    elif isinstance(valor, (np.floating, np.float32, np.float64)):
        return float(valor)
    elif isinstance(valor, (np.str_, str)):
        return str(valor)
    else:
        return valor