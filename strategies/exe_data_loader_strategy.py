import os
import sqlite3
from strategies.data_loader_strategy import DataLoaderStrategy

class ExeDataLoadStrategy(DataLoaderStrategy):
    def load_data(self):
        # Ejecutar el EXE que genera datos (ajusta la ruta real de tu ejecutable)
        os.system("path_to_your_exe.exe")

        # Luego de ejecutar el EXE, cargar los datos desde la base de datos
        return self.load_from_db()

    def load_from_db(self):
        conn = sqlite3.connect("defectos.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, eje_x, eje_y, largo, ancho, etiqueta, prediccion FROM defects")
        rows = cursor.fetchall()

        conn.close()
        return rows
    
