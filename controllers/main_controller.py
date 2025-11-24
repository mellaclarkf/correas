from services.boundingbox_service import BoundingBoxService
from services.historial_repository import HistorialRepository
from factories.data_load_factory import DataLoadFactory
from utils.folder_dataset import DatasetFolderManager
import os
import shutil
import pandas as pd 
from utils.tramo_utils import calcular_tramo_para_defecto, calcular_desplazamiento_inicial

class MainController:
    def __init__(self, window,db_session):
        self.window = window
        self.db_session = db_session
        self.boundingbox_service = BoundingBoxService()
        self.boundingbox_service.inicializar_modelo_base()
        self.historial_repository = HistorialRepository(db_session)

        self.data_load_factory = DataLoadFactory(
            boundingbox_service=self.boundingbox_service,
            historial_repository=self.historial_repository,
            images_folder="Imagenes/"
        )

    # def cargar_imagen_y_generar_datos(self, file_path):
    #     self.boundingbox_service.resetear_filtro()
    #     bounding_boxes = self.boundingbox_service.get_data(file_path)
        
    #     # Insertar en BD y obtener IDs
    #     ids = self.historial_repository.insertar_varios_registros(bounding_boxes)
        
    #     # Crear una copia de bounding_boxes y asignar los IDs
    #     resultado = bounding_boxes.copy()
    #     resultado['id'] = ids
        
    #     return bounding_boxes, resultado

    def actualizar_etiquetas(self, lista_etiquetas_id):
        lista_filtrada = [(etiqueta, id_) for etiqueta, id_ in lista_etiquetas_id if etiqueta is not None and str(etiqueta).strip() != ""]
        self.historial_repository.actualizar_etiquetas(lista_filtrada)

    def cargar_datos_desde_fuente(self, tipo_fuente, ruta, insertar_en_bd=False):
        """
        Carga datos desde la fuente especificada
        """
        try:
            # LIMPIAR carpeta de imágenes de reproducción y labels
            DatasetFolderManager.limpiar_carpeta_imagenes("Imagenes/")
            trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
            DatasetFolderManager.limpiar_carpeta_imagenes(trained_models_path / "images")
            DatasetFolderManager.limpiar_carpeta_imagenes(trained_models_path / "labels")
            
            # 1. Obtener las detecciones
            if tipo_fuente == "video":
                # Para video - usa el método que ya tienes implementado
                resultados = self._procesar_video_completo(ruta)
            elif tipo_fuente == "imagen":
                # Para imagen: usar directamente get_data()
                resultados = self.boundingbox_service.get_data(ruta)
            else:
                raise ValueError(f"Tipo de fuente no válido: {tipo_fuente}")
            
            # 2. Convertir a DataFrame (ahora pd está importado)
            if resultados is None:
                df_resultados = pd.DataFrame()
            elif isinstance(resultados, pd.DataFrame):
                df_resultados = resultados
            else:
                df_resultados = pd.DataFrame(resultados)
            
            print(f"DEBUG: Resultados obtenidos: {len(df_resultados)} filas")
            
            return df_resultados
                
        except Exception as e:
            print(f"❌ Error en cargar_datos_desde_fuente: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return pd.DataFrame()  

    ######################## FUNCIONES DE REENTRENAMIENTO #########################   
    def reentrenar_modelo(self, progress_callback=None):
        """
        Ejecuta el proceso de re-entrenamiento del modelo con actualizaciones de progreso
        """
        if self.window:
            self.window.status_label.config(text="Re-entrenando modelo...", fg="orange")
            self.window.update_idletasks()
        
        try:
            success, result, modelo_pkl, accuracy_porcentaje, nombre_modelo = self.boundingbox_service.reentrenar(
                epochs=5, 
                imgsz=640,
                progress_callback=progress_callback
            )
            
            if self.window:
                if success:
                    message = f"Re-entrenamiento exitoso. mAP50: {result['mAP50']:.3f}"
                    self.window.status_label.config(text=message, fg="green")
                else:
                    self.window.status_label.config(text=result, fg="red")
            
            return success, result if success else result, modelo_pkl, accuracy_porcentaje, nombre_modelo
            
        except Exception as e:
            error_msg = f"Error en re-entrenamiento: {str(e)}"
            if self.window:
                self.window.status_label.config(text=error_msg, fg="red")

            return False, error_msg, None, None, None

    def guardar_detecciones_para_reentrenamiento(self, boxes_with_L, image_path, frame_shape):
        """
        Guarda detecciones para posterior re-entrenamiento
        """
        trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
        labels_dir = trained_models_path / "labels"
        labels_dir.mkdir(exist_ok=True)
        
        # Crear nombre del archivo .txt
        image_name = os.path.basename(image_path)
        label_name = os.path.splitext(image_name)[0] + ".txt"
        label_path = labels_dir / label_name
        
        self.boundingbox_service.guardar_detecciones_modelo(boxes_with_L, str(label_path), frame_shape)
        
        # También copiar la imagen a la carpeta images
        images_dir = trained_models_path / "images"
        images_dir.mkdir(exist_ok=True)
        target_image_path = images_dir / image_name
        shutil.copy2(image_path, str(target_image_path))
        
        return str(label_path)   

    # En tu MainController class
    def guardar_resultados_en_bd(self, resultado_df, imagenes_completas=None, 
                            largo_total_correa=None, tramos_info=None, 
                            secciones_correa=5, desplazamiento_inicial=0):
        """Guarda los resultados en la base de datos"""
        try:
            # Calcular tramo para cada defecto
            if (imagenes_completas is not None and largo_total_correa is not None and 
                not resultado_df.empty):
                
                resultado_df['tramo'] = resultado_df['image_path'].apply(
                    lambda path: calcular_tramo_para_defecto(
                        path, imagenes_completas, largo_total_correa, tramos_info,
                        secciones_correa, desplazamiento_inicial
                    )
                )
            
            # CONVERTIR a lista de diccionarios (CORRECTAMENTE)
            if hasattr(resultado_df, 'to_dict'):
                registros = resultado_df.to_dict('records')
            else:
                registros = resultado_df
            
            # DEBUG del formato
            print(f"DEBUG: Tipo de registros a enviar: {type(registros)}")
            if registros and len(registros) > 0:
                print(f"DEBUG: Ejemplo de registro: {registros[0]}")
                print(f"DEBUG: Tipo del ejemplo: {type(registros[0])}")
            
            # Insertar en el historial
            ids = self.historial_repository.insertar_varios_registros(registros)
            print(f"Insertados {len(ids)} registros en BD con tramos calculados")
            return ids
            
        except Exception as e:
            print(f"Error guardando en BD: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _procesar_video_completo(self, video_path):
        """
        Procesa un video completo usando el método de boundingbox_service
        """
        try:
            # procesar_video
            if hasattr(self.boundingbox_service, 'procesar_video'):
                print("DEBUG: Usando método procesar_video")
                resultados = self.boundingbox_service.procesar_video(video_path)
                return resultados
            else:
                print("⚠️ Método procesar_video no disponible en boundingbox_service")
                return []
            
        except Exception as e:
            print(f"❌ Error en _procesar_video_completo: {e}")
            return []
        
    def _convertir_a_dataframe_seguro(self, datos):
        """
        Convierte datos a DataFrame de forma segura
        """
        try:
            # Caso 1: Ya es DataFrame
            if isinstance(datos, pd.DataFrame):
                return datos
            
            # Caso 2: Es una lista de diccionarios (resultado de procesar_video)
            if isinstance(datos, list) and len(datos) > 0 and isinstance(datos[0], dict):
                return pd.DataFrame(datos)
            
            # Caso 3: Lista vacía, None, u otros formatos
            return pd.DataFrame()
            
        except Exception as e:
            print(f"⚠️ Error en conversión a DataFrame: {e}")
            return pd.DataFrame()        