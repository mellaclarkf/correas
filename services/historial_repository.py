# repositories/historial_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, text
from models.models import Historial
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from utils.database_connection import engine

class HistorialRepository:
    def __init__(self, db: Session):
        self.db = db

    def insertar_registro(self, registro: Dict) -> Optional[int]:
        try:
            nuevo = Historial(**registro)
            self.db.add(nuevo)
            self.db.commit()
            self.db.refresh(nuevo)
            return nuevo.id
        except Exception as e:
            self.db.rollback()
            print(f"Error insertando registro: {e}")
            return None

    def insertar_defectos(self, defects_data: List[dict]) -> List[int]:
        """Inserta múltiples defectos y retorna los IDs insertados"""
        try:
            objetos = []
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
                objetos.append(registro)
            
            self.db.add_all(objetos)
            self.db.commit()
            
            # Refrescar para obtener los IDs
            for obj in objetos:
                self.db.refresh(obj)
                
            # Retornar los IDs insertados
            return [obj.id for obj in objetos]
            
        except Exception as e:
            self.db.rollback()
            print(f"Error insertando defectos: {e}")
            return []  # Retornar lista vacía en caso de error

    # services/historial_repository.py - SOLO ESTE MÉTODO
    def insertar_varios_registros(self, lista_registros):
        """
        Inserta múltiples registros en la base de datos
        """
        try:
            # ✅ FILTRAR solo diccionarios y campos válidos
            registros_validos = []
            for reg in lista_registros:
                if isinstance(reg, dict):
                    # ✅ Crear nuevo dict solo con campos que EXISTEN en tu BD
                    registro_limpio = {
                        'name': reg.get('name'),
                        'image_path': reg.get('image_path'),
                        'eje_x': reg.get('eje_x', 0),
                        'eje_y': reg.get('eje_y', 0),
                        'eje_x2': reg.get('eje_x2', 0),
                        'eje_y2': reg.get('eje_y2', 0),
                        'largo': reg.get('largo', 0),
                        'ancho': reg.get('ancho', 0),
                        'etiqueta': reg.get('etiqueta'),
                        'prediccion': reg.get('prediccion', ''),
                        'modelo_correa': reg.get('modelo_correa', ''),
                        'fecha_registro': reg.get('fecha_registro'),
                        'fecha_video' : reg.get('fecha_video'),
                        'tramo': reg.get('tramo', 0)  
                    }
                    
                    # ✅ Eliminar campos None o vacíos
                    registro_limpio = {k: v for k, v in registro_limpio.items() if v is not None}
                    registros_validos.append(registro_limpio)
            
            if not registros_validos:
                return []
                
            # ✅ Insertar solo campos válidos
            objetos = []
            for reg in registros_validos:
                try:
                    objetos.append(Historial(**reg))
                except Exception as e:
                    print(f"Error creando objeto: {e}")
                    continue
            
            self.db.add_all(objetos)
            self.db.commit()
            
            return [obj.id for obj in objetos]
            
        except Exception as e:
            print(f"Error insertando múltiples registros: {e}")
            self.db.rollback()
            return []

    def actualizar_etiquetas(self, lista_etiquetas_id: List[tuple]) -> bool:
        try:
            for etiqueta, id_ in lista_etiquetas_id:
                if etiqueta and str(etiqueta).strip():
                    registro = self.db.query(Historial).filter(Historial.id == id_).first()
                    if registro:
                        registro.etiqueta = etiqueta
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error actualizando etiquetas: {e}")
            return False
        
    def obtener_registro_por_id(self, id_registro) -> Optional[Dict]:
        """Obtiene un registro por su ID y lo devuelve como diccionario"""
        try:
            # Convertir a entero si es string (para IDs manuales que no existen en BD)
            try:
                id_int = int(id_registro)
            except ValueError:
                # Si es un ID manual (ej: "manual_abc123"), no existe en BD aún
                return None
                
            registro = self.db.query(Historial).filter(Historial.id == id_int).first()
            if registro:
                return {
                    'id': registro.id,
                    'name': registro.name,
                    'image_path': registro.image_path,
                    'eje_x': registro.eje_x,
                    'eje_y': registro.eje_y,
                    'eje_x2': registro.eje_x2,
                    'eje_y2': registro.eje_y2,
                    'largo': registro.largo,
                    'ancho': registro.ancho,
                    'etiqueta': registro.etiqueta,
                    'prediccion': registro.prediccion,
                    'modelo_correa': registro.modelo_correa,
                    'fecha_registro': registro.fecha_registro,
                    'Tramo': registro.Tramo
                }
            return None
        except Exception as e:
            print(f"Error obteniendo registro por ID: {e}")
            return None        
        
    def actualizar_etiqueta_por_id(self, id_registro, nueva_etiqueta: str) -> bool:
        """Actualiza solo la etiqueta de un registro existente"""
        try:
            # Convertir a entero si es string
            try:
                id_int = int(id_registro)
            except ValueError:
                # Si es un ID manual, no existe en BD aún
                return False
                
            registro = self.db.query(Historial).filter(Historial.id == id_int).first()
            if registro:
                registro.etiqueta = nueva_etiqueta
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error actualizando etiqueta: {e}")
            return False

    def insertar_defecto_manual(self, defecto: Dict) -> Optional[int]:
        """Inserta un nuevo defecto manual en la base de datos con TODOS los campos"""
        try:
            # DEBUG: Imprimir lo que se está intentando insertar
            print(f"DEBUG: Intentando insertar defecto con datos:")
            for key, value in defecto.items():
                print(f"  {key}: {value} (tipo: {type(value)})")
            
            # Crear objeto Historial con TODOS los campos
            nuevo = Historial(
                name=defecto.get('name', ''),
                image_path=defecto.get('image_path', ''),
                eje_x=defecto.get('eje_x', 0),
                eje_y=defecto.get('eje_y', 0),
                eje_x2=defecto.get('eje_x2', 0),
                eje_y2=defecto.get('eje_y2', 0),
                largo=defecto.get('largo', 0),
                ancho=defecto.get('ancho', 0),
                etiqueta=defecto.get('etiqueta', ''),
                prediccion=defecto.get('prediccion', ''),
                modelo_correa=defecto.get('modelo_correa', ''),
                fecha_registro=defecto.get('fecha_registro'),
                tramo=defecto.get('tramo', 0)
            )
            
            self.db.add(nuevo)
            self.db.commit()
            self.db.refresh(nuevo)
            print(f"DEBUG: Insertado exitosamente con ID: {nuevo.id}")
            return nuevo.id
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error insertando defecto manual: {e}")
            import traceback
            print(f"❌ Traceback completo: {traceback.format_exc()}")
            return None
    ## para report
    def obtener_modelos_unicos(self):
        """Obtiene todos los modelos de correa únicos de la base de datos"""
        try:
            modelos = self.db.query(
                distinct(Historial.modelo_correa)
            ).filter(
                Historial.modelo_correa.isnot(None)
            ).order_by(
                Historial.modelo_correa
            ).all()
            
            return [modelo[0] for modelo in modelos if modelo[0]]
        except Exception as e:
            print(f"Error obteniendo modelos únicos: {e}")
            return []

    def obtener_tramos_por_modelo(self, modelo_correa):
        """Obtiene los tramos únicos para un modelo específico"""
        try:
            tramos = self.db.query(
                distinct(Historial.tramo)
            ).filter(
                Historial.modelo_correa == modelo_correa,
                Historial.tramo.isnot(None)
            ).order_by(
                Historial.tramo
            ).all()
            
            return [tramo[0] for tramo in tramos if tramo[0] is not None]
        except Exception as e:
            print(f"Error obteniendo tramos para modelo {modelo_correa}: {e}")
            return []

    def obtener_ultimas_fechas(self, modelo_correa, tramo=None):
        """Obtiene las últimas 2 fechas con datos para un modelo y tramo específico"""
        try:
            query = self.db.query(
                func.date(Historial.fecha_registro).label('fecha')
            ).filter(
                Historial.modelo_correa == modelo_correa,
                Historial.prediccion.isnot(None)
            ).distinct()
            
            if tramo is not None:
                query = query.filter(Historial.tramo == tramo)
            
            fechas = query.order_by(
                func.date(Historial.fecha_registro).desc()
            ).limit(2).all()
            
            return [fecha[0] for fecha in fechas if fecha[0]]
        except Exception as e:
            print(f"Error obteniendo últimas fechas: {e}")
            return []

    def obtener_defectos_por_prediccion(self, modelo_correa, fecha, tramo=None):
        """Obtiene la cantidad de defectos por tipo de predicción"""
        try:
            query = self.db.query(
                Historial.prediccion,
                func.count(Historial.id).label('cantidad')
            ).filter(
                Historial.modelo_correa == modelo_correa,
                func.date(Historial.fecha_video) == fecha,
                Historial.prediccion.isnot(None)
            ).group_by(
                Historial.prediccion
            )
            
            if tramo is not None:
                query = query.filter(Historial.tramo == tramo)
            
            resultados = query.order_by(
                func.count(Historial.id).desc()
            ).all()
            
            # Convertir a DataFrame
            data = [{'prediccion': r[0], 'cantidad': r[1]} for r in resultados]
            return pd.DataFrame(data)
            
        except Exception as e:
            print(f"Error obteniendo defectos por predicción: {e}")
            return pd.DataFrame()

    def obtener_comparativa_fechas(self, modelo_correa, fechas, tramo=None) -> pd.DataFrame:
        """Obtiene datos comparativos entre dos fechas"""
        try:
            query = self.db.query(
                func.date(Historial.fecha_registro).label('fecha'),
                Historial.prediccion.label('prediccion'),
                func.count(Historial.id).label('cantidad')
            ).filter(
                Historial.modelo_correa == modelo_correa,
                func.date(Historial.fecha_registro).in_(fechas),
                Historial.prediccion.isnot(None)
            ).group_by(
                func.date(Historial.fecha_registro),
                Historial.prediccion
            )

            if tramo is not None:
                query = query.filter(Historial.tramo == tramo)

            resultados = query.all()
            data = [{'fecha': r.fecha, 'prediccion': r.prediccion, 'cantidad': r.cantidad} for r in resultados]
            return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ Error en obtener_comparativa_fechas (modelo={modelo_correa}, fechas={fechas}, tramo={tramo}): {e}")
            return pd.DataFrame()

    def obtener_reparaciones_vs_desgaste(self, modelo_correa, fechas, predicciones=['Reparaciones', 'Desgaste']):
        """
        Obtiene datos de reparaciones vs desgaste por tramos
        """
        try:
            print(f"🔍 REPOSITORY - obtener_reparaciones_vs_desgaste")
            print(f"🔍 Modelo: {modelo_correa}, Fechas: {fechas}, Predicciones: {predicciones}")

            # ✅ NORMALIZAR FECHAS - Convertir todas a datetime.date
            fechas_normalizadas = []
            for fecha in fechas:
                if isinstance(fecha, str):
                    # Si es string, convertir a datetime.date
                    fecha_normalizada = pd.to_datetime(fecha).date()
                    fechas_normalizadas.append(fecha_normalizada)
                else:
                    # Si ya es datetime.date, usar directamente
                    fechas_normalizadas.append(fecha)
            
            print(f"🔍 Fechas normalizadas: {fechas_normalizadas}")

            # Query principal (usar fechas_normalizadas en lugar de fechas)
            query = self.db.query(
                Historial.tramo,
                func.date(Historial.fecha_video).label('fecha'),
                Historial.prediccion,
                func.count(Historial.id).label('cantidad')
            ).filter(
                Historial.modelo_correa == modelo_correa,
                func.date(Historial.fecha_video).in_(fechas_normalizadas),  # ✅ Usar las fechas normalizadas
                Historial.prediccion.in_(predicciones),
                Historial.tramo.isnot(None)
            ).group_by(
                Historial.tramo,
                func.date(Historial.fecha_video),
                Historial.prediccion
            ).order_by(
                Historial.tramo,
                func.date(Historial.fecha_video)
            )

            resultados = query.all()
            print(f"🔍 Resultados encontrados: {len(resultados)}")
            for r in resultados:
                print(f"   - Tramo: {r[0]}, Fecha: {r[1]}, Pred: {r[2]}, Cant: {r[3]}")

            # Convertir a DataFrame
            data = [{'Tramo': r[0], 'fecha': r[1], 'prediccion': r[2], 'cantidad': r[3]} for r in resultados]
            df = pd.DataFrame(data, columns=['Tramo', 'fecha', 'prediccion', 'cantidad'])

            print(f"🔍 DataFrame final: {df.shape}")
            print(f"🔍 Columnas en df: {df.columns.tolist()}")

            return df

        except Exception as e:
            self.db.rollback() if hasattr(self.db, 'rollback') else None
            print(f"❌ ERROR en obtener_reparaciones_vs_desgaste: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return pd.DataFrame(columns=['Tramo', 'fecha', 'prediccion', 'cantidad'])


    def obtener_distancias_fallas(self, modelo_correa, fechas) -> pd.DataFrame:
        """Obtiene distancias de fallas por tramo y tipo de defecto"""
        try:
            query = self.db.query(
                Historial.tramo.label("Tramo"),
                func.date(Historial.fecha_registro).label("fecha"),
                Historial.prediccion.label("prediccion"),
                func.sum(func.abs(Historial.eje_y2 - Historial.eje_y)).label('distancia_total'),
                func.count(Historial.id).label('cantidad_fallas')
            ).filter(
                Historial.modelo_correa == modelo_correa,
                func.date(Historial.fecha_registro).in_(fechas),
                Historial.prediccion.in_(['Reparaciones', 'Desgaste']),
                Historial.eje_y.isnot(None),
                Historial.eje_y2.isnot(None),
                Historial.tramo.isnot(None)
            ).group_by(
                Historial.tramo,
                func.date(Historial.fecha_registro),
                Historial.prediccion
            ).order_by(
                func.count(Historial.id).desc()
            )

            resultados = query.all()
            data = [{
                'Tramo': r.Tramo,
                'fecha': r.fecha,
                'prediccion': r.prediccion,
                'distancia_total': r.distancia_total if r.distancia_total else 0,
                'cantidad_fallas': r.cantidad_fallas
            } for r in resultados]

            return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ Error en obtener_distancias_fallas (modelo={modelo_correa}, fechas={fechas}): {e}")
            return pd.DataFrame()
        

    def obtener_fechas_video_por_modelo(self, modelo_correa):
        """Obtiene las fechas de video únicas para un modelo específico"""
        try:
            fechas = self.db.query(
                distinct(func.date(Historial.fecha_video))
            ).filter(
                Historial.modelo_correa == modelo_correa,
                Historial.fecha_video.isnot(None)
            ).order_by(
                func.date(Historial.fecha_video).desc()
            ).all()
            
            return [fecha[0] for fecha in fechas if fecha[0]]
        except Exception as e:
            print(f"Error obteniendo fechas de video para modelo {modelo_correa}: {e}")
            return []        
        
    def obtener_fecha_anterior(self, modelo_correa, fecha_actual, tramo=None):
        """Obtiene la fecha anterior más cercana a la fecha actual"""
        try:
            # PRIMERO aplicar todos los filtros, LUEGO el limit
            query = self.db.query(
                distinct(func.date(Historial.fecha_video))
            ).filter(
                Historial.modelo_correa == modelo_correa,
                func.date(Historial.fecha_video) < fecha_actual,
                Historial.fecha_video.isnot(None)
            )
            
            if tramo is not None:
                query = query.filter(Historial.tramo == tramo)
            
            # AHORA aplicar order_by y limit
            query = query.order_by(
                func.date(Historial.fecha_video).desc()
            ).limit(1)
            
            resultado = query.first()
            return resultado[0] if resultado else None
            
        except Exception as e:
            print(f"Error obteniendo fecha anterior: {e}")
            return None   