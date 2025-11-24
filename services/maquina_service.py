# services/maquina_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import Maquina, Tramo
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError

class MaquinaService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_maquinas(self) -> List[Maquina]:
        return self.db.query(Maquina).all()

    def obtener_nombres_maquinas(self) -> List[str]:
        maquinas = self.db.query(Maquina.nombre).all()
        return [m[0] for m in maquinas]

    def insertar_maquina(self, nombre: str, ubicacion: Optional[str] = None, 
                        largo: Optional[float] = None, direccion: bool = True) -> Optional[int]:
        try:
            nueva_maquina = Maquina(
                nombre=nombre,
                ubicacion=ubicacion,
                largo=largo,
                direccion=direccion
            )
            self.db.add(nueva_maquina)
            self.db.commit()
            self.db.refresh(nueva_maquina)
            return nueva_maquina.id
        except Exception as e:
            self.db.rollback()
            print(f"Error insertando máquina: {e}")
            return None

    def actualizar_maquina(self, id_maquina: int, nombre: Optional[str] = None, 
                          ubicacion: Optional[str] = None, largo: Optional[float] = None, 
                          direccion: Optional[bool] = None) -> bool:
        try:
            maquina = self.db.query(Maquina).filter(Maquina.id == id_maquina).first()
            if not maquina:
                return False
            
            if nombre is not None:
                maquina.nombre = nombre
            if ubicacion is not None:
                maquina.ubicacion = ubicacion
            if largo is not None:
                maquina.largo = largo
            if direccion is not None:
                maquina.direccion = direccion
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error actualizando máquina: {e}")
            return False

    def obtener_todas_maquinas(self) -> List[Maquina]:
        try:
            return self.db.query(Maquina).order_by(Maquina.nombre).all()
        except Exception as e:
            print(f"Error obteniendo máquinas: {e}")
            return []

    def obtener_direccion_maquina(self, id_maquina: int) -> Optional[bool]:
        try:
            maquina = self.db.query(Maquina).filter(Maquina.id == id_maquina).first()
            return maquina.direccion if maquina else None
        except Exception as e:
            print(f"Error al obtener dirección: {e}")
            return None

    def actualizar_direccion_maquina(self, id_maquina: int, direccion: bool) -> bool:
        try:
            maquina = self.db.query(Maquina).filter(Maquina.id == id_maquina).first()
            if maquina:
                maquina.direccion = direccion
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar dirección: {e}")
            return False

    def eliminar_maquina(self, id_maquina: int) -> bool:
        try:
            maquina = self.db.query(Maquina).filter(Maquina.id == id_maquina).first()
            if maquina:
                self.db.delete(maquina)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error eliminando máquina: {e}")
            return False

    def contar_tramos_de_maquina(self, id_maquina: int) -> int:
        return self.db.query(Tramo).filter(Tramo.id_maquina == id_maquina).count()

    def obtener_id_maquina_por_nombre(self, nombre_maquina: str) -> Optional[int]:
        maquina = self.db.query(Maquina).filter(Maquina.nombre == nombre_maquina).first()
        return maquina.id if maquina else None

    def obtener_tramos_por_maquina(self, id_maquina: int) -> List[Tramo]:
        return self.db.query(Tramo).filter(Tramo.id_maquina == id_maquina).order_by(Tramo.numero_tramo).all()

    # services/maquina_service.py
    def obtener_largo_total_por_tramos(self, id_maquina: int) -> float:
        try:
            # CORRECCIÓN: Esta es la sintaxis correcta
            result = self.db.query(func.sum(Tramo.largo_tramo)).filter(
                Tramo.id_maquina == id_maquina
            ).scalar()
            return result or 0.0
        except SQLAlchemyError as e:
            print(f"Error calculando largo total: {e}")
            return 0.0

    def insertar_tramo(self, id_maquina: int, numero_tramo: int, 
                      largo_tramo: Optional[float] = None, nota: Optional[str] = None) -> Optional[int]:
        try:
            # Verificar si ya existe
            existente = self.db.query(Tramo).filter(
                Tramo.id_maquina == id_maquina, 
                Tramo.numero_tramo == numero_tramo
            ).first()
            
            if existente:
                return None
            
            nuevo_tramo = Tramo(
                id_maquina=id_maquina,
                numero_tramo=numero_tramo,
                largo_tramo=largo_tramo,
                nota=nota
            )
            
            self.db.add(nuevo_tramo)
            self.db.commit()
            self.db.refresh(nuevo_tramo)
            return nuevo_tramo.id
        except Exception as e:
            self.db.rollback()
            print(f"Error insertando tramo: {e}")
            return None

    def actualizar_tramo(self, id_maquina: int, numero_tramo: int, 
                        largo_tramo: Optional[float] = None, nota: Optional[str] = None) -> bool:
        try:
            tramo = self.db.query(Tramo).filter(
                Tramo.id_maquina == id_maquina,
                Tramo.numero_tramo == numero_tramo
            ).first()
            
            if tramo:
                if largo_tramo is not None:
                    tramo.largo_tramo = largo_tramo
                if nota is not None:
                    tramo.nota = nota
                
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error actualizando tramo: {e}")
            return False

    def eliminar_tramo_por_numero(self, id_maquina: int, numero_tramo: int) -> bool:
        try:
            tramo = self.db.query(Tramo).filter(
                Tramo.id_maquina == id_maquina,
                Tramo.numero_tramo == numero_tramo
            ).first()
            
            if tramo:
                self.db.delete(tramo)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error eliminando tramo: {e}")
            return False