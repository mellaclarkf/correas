# services/modelo_service.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.models import Modelo
from typing import Optional, Dict

class ModeloService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_ultimo_modelo(self) -> Optional[Modelo]:
        """Obtiene el último modelo registrado por fecha"""
        return self.db.query(Modelo).order_by(desc(Modelo.fecha_creacion)).first()

    def insertar_modelo(self, accuracy: float, nombre_modelo: str) -> Optional[int]:
        try:
            accuracy_float = float(accuracy)
            
            from sqlalchemy import text
            
            # Insertar sin especificar ID (deja que la BD lo auto-genere)
            result = self.db.execute(
                text("INSERT INTO modelo (accuracy, nombre_modelo) VALUES (:accuracy, :nombre)"),
                {"accuracy": accuracy_float, "nombre": nombre_modelo}
            )
            self.db.commit()
            
            # Obtener el ID insertado
            last_id_result = self.db.execute(text("SELECT LAST_INSERT_ID()"))
            modelo_id = last_id_result.scalar()
            
            print(f"✅ Modelo insertado (SQL directo): {nombre_modelo} - {accuracy_float}% (ID: {modelo_id})")
            return modelo_id
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error insertando modelo con SQL directo: {e}")
            return None

    def obtener_accuracy_ultimo_modelo(self) -> Dict:
        """
        Obtiene el accuracy del último modelo.
        Retorna: {'accuracy': float, 'nombre_modelo': str, 'mensaje': str}
        """
        ultimo_modelo = self.obtener_ultimo_modelo()
        
        if ultimo_modelo and ultimo_modelo.accuracy is not None:
            return {
                'accuracy': ultimo_modelo.accuracy,
                'nombre_modelo': ultimo_modelo.nombre_modelo or "Modelo sin nombre",
                'mensaje': f"{ultimo_modelo.accuracy:.2f}%"
            }
        else:
            return {
                'accuracy': None,
                'nombre_modelo': None,
                'mensaje': "Sin datos aún"
            }
        
    def obtener_mejor_modelo(self) -> Optional[Modelo]:
        """Obtiene el modelo con el accuracy más alto"""
        try:
            mejor = self.db.query(Modelo).order_by(desc(Modelo.accuracy)).first()
            print(f"🔍 Mejor modelo en BD: {mejor.accuracy if mejor else 'None'}%")
            return mejor
        except Exception as e:
            print(f"❌ Error obteniendo mejor modelo: {e}")
            return None

    def obtener_accuracy_mejor_modelo(self) -> Dict:
        """Obtiene el accuracy del mejor modelo"""
        mejor_modelo = self.obtener_mejor_modelo()
        if mejor_modelo and mejor_modelo.accuracy is not None:
            return {
                'accuracy': mejor_modelo.accuracy,
                'nombre_modelo': mejor_modelo.nombre_modelo or "Mejor Modelo",
                'mensaje': f"{mejor_modelo.accuracy:.2f}% (Mejor)"
            }
        else:
            return {'accuracy': None, 'mensaje': "Sin datos aún"}

    def actualizar_si_es_mejor_modelo(self, accuracy: float, nombre_modelo: str) -> bool:
        """
        Inserta el modelo solo si tiene mejor accuracy que el existente
        Retorna True si es el nuevo mejor modelo
        """
        mejor_actual = self.obtener_mejor_modelo()
        
        print(f"🔍 COMPARACIÓN: Nuevo {accuracy}% vs Mejor actual: {mejor_actual.accuracy if mejor_actual else 'None'}%")
        
        # Si no hay modelos existentes o este es mejor
        if mejor_actual is None or accuracy > mejor_actual.accuracy:
            modelo_id = self.insertar_modelo(accuracy, nombre_modelo)
            print(f"✅ INSERTANDO nuevo mejor modelo: {accuracy}% > {mejor_actual.accuracy if mejor_actual else 'N/A'}%")
            return modelo_id is not None
        else:
            print(f"ℹ️ NO insertando: {accuracy}% <= {mejor_actual.accuracy}%")
            return False