# models/defect.py
from datetime import datetime

class Defect:
    def __init__(self, id: int = None, name: str = "", image_path: str = "", 
                 eje_x: int = 0, eje_y: int = 0, eje_x2: int = 0, eje_y2: int = 0, 
                 largo: int = 0, ancho: int = 0, etiqueta: str = "", 
                 prediccion: str = "", modelo_correa: str = "", 
                 fecha_registro: datetime = None, tramo: int = 0):
        self.id = id
        self.name = name
        self.image_path = image_path
        self.eje_x = eje_x
        self.eje_y = eje_y
        self.eje_x2 = eje_x2
        self.eje_y2 = eje_y2
        self.largo = largo
        self.ancho = ancho
        self.etiqueta = etiqueta
        self.prediccion = prediccion
        self.modelo_correa = modelo_correa
        self.fecha_registro = fecha_registro or datetime.now()
        self.tramo = tramo