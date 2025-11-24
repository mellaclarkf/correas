import cv2
import os
import shutil
import time
from utils.folder_dataset import DatasetFolderManager

class VideoService:
    def __init__(self, images_folder="Imagenes/"):
        self.images_folder = images_folder
        # No limpiar automáticamente en __init__ para evitar problemas de permisos
        # La limpieza se hará explícitamente al extraer frames

    def limpiar_carpeta_imagenes(self):
        """Borra todas las imágenes anteriores de forma segura"""
        if os.path.exists(self.images_folder):
            try:
                # Intentar eliminar con varios intentos
                for intento in range(3):
                    try:
                        shutil.rmtree(self.images_folder)
                        break  # Salir si tiene éxito
                    except PermissionError:
                        if intento == 2:  # Último intento
                            raise
                        time.sleep(0.1)  # Esperar un poco antes de reintentar
            except Exception as e:
                print(f"⚠️ No se pudo limpiar carpeta {self.images_folder}: {e}")
                # Crear carpeta de todas formas
                pass
        
        # Asegurar que la carpeta existe
        os.makedirs(self.images_folder, exist_ok=True)

    def limpiar_archivos_imagenes(self):
        """Alternativa más segura: solo borra los archivos .jpg, no la carpeta"""
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder, exist_ok=True)
            return
        
        try:
            # Borrar solo archivos .jpg, no la carpeta completa
            for archivo in os.listdir(self.images_folder):
                if archivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                    archivo_path = os.path.join(self.images_folder, archivo)
                    try:
                        os.remove(archivo_path)
                    except PermissionError:
                        print(f"⚠️ No se pudo borrar {archivo_path}")
                        continue
        except Exception as e:
            print(f"⚠️ Error limpiando archivos: {e}")

    def extraer_frames(self, video_path, frame_skip=1):
        """Extrae TODOS los frames y los guarda en la carpeta Imagenes/"""
        # Limpiar solo los archivos de imagen, no la carpeta completa
        DatasetFolderManager.limpiar_todas_las_carpetas(self.images_folder)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir el video: {video_path}")
        
        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_skip == 0:
                # Guardar frame para reproducción
                frame_filename = f"{self.images_folder}frame_{saved_count:04d}.jpg"
                cv2.imwrite(frame_filename, frame)
                saved_count += 1
            
            frame_count += 1
        
        cap.release()
        print(f"✅ {saved_count} frames guardados en {self.images_folder}")
        return saved_count