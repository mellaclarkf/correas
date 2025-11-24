# services/database_service.py
from sqlalchemy.orm import Session
from models.models import Historial
from typing import List
from datetime import datetime

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_defects(self) -> List[Historial]:
        return self.db.query(Historial).all()

    # database_service.py (modificado)
    def insertar_defectos(self, defects_data: List[dict]) -> bool:
        try:
            for defect in defects_data:
                registro = Historial(
                    name=defect.get('name', ''),
                    image_path=defect.get('image_path', ''),
                    eje_x=defect.get('eje_x', 0),
                    eje_y=defect.get('eje_y', 0),
                    eje_x2=defect.get('eje_x2', 0),
                    eje_y2=defect.get('eje_y2', 0),
                    largo=defect.get('largo', 0),
                    ancho=defect.get('ancho', 0),
                    etiqueta=defect.get('etiqueta', ''),
                    prediccion=defect.get('prediccion', ''),
                    modelo_correa=defect.get('modelo_correa', ''),
                    fecha_registro=defect.get('fecha_registro', datetime.now()),
                    tramo=defect.get('tramo', 0)
                )
                self.db.add(registro)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error insertando defectos: {e}")
            return False