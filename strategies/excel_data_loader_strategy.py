import pandas as pd
from strategies.data_loader_strategy import DataLoaderStrategy
import sqlite3

class ExcelDataLoadStrategy(DataLoaderStrategy):
    def load_data(self):
        # Cargar datos desde un archivo Excel
        df = pd.read_excel("path_to_excel_file.xlsx")

        # Conectar a la base de datos
        conn = sqlite3.connect("defectos.db")
        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO defects (name, eje_x, eje_y, largo, ancho, etiqueta) VALUES (?, ?, ?, ?, ?, ?)",
                (row["name"], row["eje_x"], row["eje_y"], row["largo"], row["ancho"], row["etiqueta"])
            )
        
        conn.commit()
        conn.close()
