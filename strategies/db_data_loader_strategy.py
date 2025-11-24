import sqlite3
from strategies.data_loader_strategy import DataLoaderStrategy
from factories.defect_factory import DefectFactory

class DBLoader(DataLoaderStrategy):
    def __init__(self, db_path):
        self.db_path = db_path

    def load_data(self):
        # Cargar datos desde una base de datos SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, image_path, eje_x, eje_y, largo, ancho, etiqueta, prediccion, modelo_correa, fecha_registro FROM defects")
        rows = cursor.fetchall()
        defects = [DefectFactory.create_from_row(row) for row in rows]
        conn.close()
        return defects
