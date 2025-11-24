import sqlite3
from strategies.data_loader_strategy import DataLoaderStrategy

class TxtDataLoadStrategy(DataLoaderStrategy):
    def load_data(self):
        # Cargar datos desde un archivo de texto
        with open("path_to_txt_file.txt", "r") as file:
            lines = file.readlines()

        # Conectar a la base de datos
        conn = sqlite3.connect("defectos.db")
        cursor = conn.cursor()

        for line in lines:
            data = line.strip().split(",")  # Asumiendo que los datos están separados por comas
            cursor.execute(
                "INSERT INTO defects (name, eje_x, eje_y, largo, ancho, etiqueta) VALUES (?, ?, ?, ?, ?, ?)",
                (data[0], data[1], data[2], data[3], data[4], data[5])
            )
        
        conn.commit()
        conn.close()

