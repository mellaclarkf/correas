import cv2
import os
from services.video_service import VideoService
import pandas as pd

class VideoLoaderStrategy:
    def __init__(self, boundingbox_service, historial_repository, images_folder):
        self.boundingbox_service = boundingbox_service
        self.historial_repository = historial_repository
        self.images_folder = images_folder
        self.video_service = None

    # def cargar_datos(self, video_path):
    #     self.video_service = VideoService(self.images_folder)

    #     # Limpieza de Carpetas
    #     cantidad_frames = self.video_service.extraer_frames(video_path)
        
    #     cantidad_frames = self.video_service.extraer_frames(video_path)
    #     resultados_totales = []
    #     frames_con_defectos = 0
    #     frames_repetidos = 0

    #     for i in range(cantidad_frames):
    #         # RUTA ORIGINAL en carpeta "Imagenes/" ← PARA CANVAS Y TREEVIEW
    #         imagen_path_original = f"{self.images_folder}frame_{i:04d}.jpg"
            
    #         frame = cv2.imread(imagen_path_original)
    #         if frame is None:
    #             print(f"⚠️ No se pudo cargar frame {imagen_path_original}")
    #             continue
            
    #         try:
    #             detecciones, confianzas, nombres_clases = self.boundingbox_service.detector(imagen_path_original)
    #         except Exception as e:
    #             print(f"❌ Error en detección: {e}")
    #             continue
            
    #         if detecciones.shape[0] > 0:
    #             try:
    #                 es_repetido = self.boundingbox_service.filtrar_defectos_repetidos(detecciones)
    #             except Exception as e:
    #                 print(f"⚠️ Error en filtrado: {e}")
    #                 es_repetido = False
                
    #             if not es_repetido:
    #                 try:
    #                     # GUARDAR COPIA en trained_models ← SOLO PARA RE-ENTRENAMIENTO
    #                     # Pero mantener la ruta original en el treeview
    #                     self.boundingbox_service.guardar_para_trained_models(
    #                         detecciones, frame, imagen_path_original
    #                     )
    #                 except Exception as e:
    #                     print(f"⚠️ Error guardando para trained_models: {e}")
                
    #             # CREAR DATAFRAME CON RUTA ORIGINAL ← PARA TREEVIEW Y CANVAS
    #             try:
    #                 dataframe = self.boundingbox_service.crear_dataframe_desde_detecciones(
    #                     detecciones, confianzas, nombres_clases, imagen_path_original  # ← RUTA ORIGINAL
    #                 )
    #             except Exception as e:
    #                 print(f"❌ Error creando DataFrame: {e}")
    #                 continue
                
    #             try:
    #                 ids = self.historial_repository.insertar_varios_registros(dataframe)
    #                 dataframe['id'] = ids
    #                 resultados_totales.append(dataframe)
    #                 frames_con_defectos += 1
    #             except Exception as e:
    #                 print(f"❌ Error insertando en BD: {e}")

    #     print(f"📊 {frames_con_defectos} frames con defectos detectados")
    #     print(f"📊 {frames_repetidos} frames repetidos descartados")

    #     resultado_df = pd.concat(resultados_totales, ignore_index=True) if resultados_totales else pd.DataFrame()
    #     return resultado_df