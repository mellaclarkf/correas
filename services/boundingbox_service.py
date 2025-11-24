import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = "0"  # ¡CRÍTICO! Debe ir ANTES de cualquier import
# os.environ["OPENCV_IO_ENABLE_JASPER"] = "TRUE"
# os.environ["OPENCV_IMREAD_UNCHANGED"] = "1"
import sys
import site


# if hasattr(sys, '_MEIPASS'):
#     # Rutas específicas para OpenCV 4.8.1 en Conda
#     conda_paths = [
#         sys._MEIPASS,
#         os.path.join(sys._MEIPASS, 'Library', 'bin'),
#         os.path.join(sys._MEIPASS, 'bin'),
#         os.path.join(sys._MEIPASS, 'DLLs')
#     ]
    
#     for path in conda_paths:
#         if os.path.exists(path):
#             os.environ['PATH'] = path + ";" + os.environ['PATH']
#             try:
#                 os.add_dll_directory(path)
#             except:
#                 pass  # Para versiones de Python que no tienen add_dll_directory

# # importar OpenCV
# try:
#     import cv2
#     print(f"✅ OpenCV 4.8.1 cargado correctamente")
# except ImportError as e:
#     print(f"❌ Error cargando OpenCV: {e}")
#     # Fallback: intentar cargar manualmente
#     if hasattr(sys, '_MEIPASS'):
#         dll_path = os.path.join(sys._MEIPASS, 'Library', 'bin')
#         if os.path.exists(dll_path):
#             import ctypes
#             try:
#                 # Cargar DLLs específicas de OpenCV 4.8.1
#                 ctypes.CDLL(os.path.join(dll_path, 'opencv_core480.dll'))
#                 ctypes.CDLL(os.path.join(dll_path, 'opencv_imgproc480.dll'))
#                 import cv2
#                 print(f"✅ OpenCV cargado manualmente")
#             except Exception as manual_error:
#                 print(f"❌ Error carga manual: {manual_error}")
#                 raise

import pickle
import random
import numpy as np
import cv2
import pandas as pd
from datetime import datetime, timedelta
from ultralytics import YOLO
import shutil
import re
import threading
from utils.folder_dataset import DatasetFolderManager
from pathlib import Path

class BoundingBoxService:
    def __init__(self, model_pickle_path=None):
        # Determinar la ruta del modelo automáticamente
        if model_pickle_path is None:
            self.model_pickle_path = self._obtener_modelo_mas_reciente()
        else:
            self.model_pickle_path = model_pickle_path

        self.model = None
        self.modelo_correa_actual = "Desconocido"
        self.nuevo_dataset_path = None
        self.flag_creado = False
        self.prev_box = None
        self.repetidos = 0
        self.boxes_previas = []  # Mantener múltiples detecciones anteriores
        self.umbral_iou_x = 0.5
        self.umbral_dy = 100
        #self.cargar_modelo()
        self.cargar_mejor_modelo()

    #Deberia desaparecer esta funcion
    def cargar_modelo(self):
        """Carga el modelo desde el archivo pickle"""
        try:
            if os.path.exists(self.model_pickle_path):
                with open(self.model_pickle_path, "rb") as f:
                    self.model = pickle.load(f)
                print(f"✅ Modelo cargado desde {self.model_pickle_path}")
            else:
                print(f"⚠️ No se encontró el modelo en {self.model_pickle_path}")
                self.model = None
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            self.model = None

    def cargar_mejor_modelo(self):
        """Carga el modelo con mejor accuracy de la base de datos"""
        try:
            from services.modelo_service import ModeloService
            from utils.database_connection import get_db
            
            db_session = next(get_db())
            modelo_service = ModeloService(db_session)
            mejor_modelo = modelo_service.obtener_mejor_modelo()
            
            if mejor_modelo and mejor_modelo.nombre_modelo:
                # Buscar el archivo .pkl del mejor modelo
                modelo_path = self._buscar_modelo_por_nombre(mejor_modelo.nombre_modelo)
                if modelo_path and os.path.exists(modelo_path):
                    self.model_pickle_path = modelo_path
                    print(f"✅ Cargando MEJOR modelo: {mejor_modelo.nombre_modelo} ({mejor_modelo.accuracy:.2f}%)")
                else:
                    print(f"⚠️ Mejor modelo {mejor_modelo.nombre_modelo} no encontrado, usando default")
                    self.model_pickle_path = self._obtener_modelo_mas_reciente()
            else:
                print("ℹ️ No hay mejor modelo en BD, usando más reciente")
                self.model_pickle_path = self._obtener_modelo_mas_reciente()
                
            self.cargar_modelo()
            db_session.close()
            
        except Exception as e:
            print(f"❌ Error cargando mejor modelo: {e}")
            self.model_pickle_path = self._obtener_modelo_mas_reciente()
            self.cargar_modelo()

    def inicializar_modelo_base(self):
        """Inicializa el modelo base en la base de datos si no existe"""
        try:
            from services.modelo_service import ModeloService
            from utils.database_connection import get_db
            
            db_session = next(get_db())
            modelo_service = ModeloService(db_session)
            
            # Verificar si ya existe algún modelo
            if modelo_service.obtener_mejor_modelo() is None:
                # Estimar accuracy inicial del Modelo0 (puedes ajustar este valor)
                accuracy_estimado = 75.0  # Valor estimado inicial
                
                modelo_service.insertar_modelo(accuracy_estimado, "Modelo0")
                print(f"✅ Modelo base inicializado con accuracy estimado: {accuracy_estimado}%")
            
            db_session.close()
            
        except Exception as e:
            print(f"❌ Error inicializando modelo base: {e}")

    def _buscar_modelo_por_nombre(self, nombre_modelo):
        """Busca un modelo por nombre en las carpetas de modelos"""
        try:
            trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
            
            # Buscar en modelos_utilizados
            modelos_dir = trained_models_path / "modelos_utilizados"
            if modelos_dir.exists():
                for archivo in modelos_dir.iterdir():
                    if archivo.is_file() and archivo.suffix == '.pkl':
                        if nombre_modelo in archivo.stem:
                            return str(archivo)
            
            # Buscar en datasets
            datasets_path = trained_models_path / "datasets"
            if datasets_path.exists():
                for dataset_dir in datasets_path.iterdir():
                    if dataset_dir.is_dir() and dataset_dir.name.startswith("dataset"):
                        modelo_path = dataset_dir / f"{nombre_modelo}.pkl"
                        if modelo_path.exists():
                            return str(modelo_path)
            
            return None
            
        except Exception as e:
            print(f"❌ Error buscando modelo por nombre: {e}")
            return None
            
    # Detector de fallas en imagenes
    def detector(self, image_path: str, conf: float = 0.25, iou: float = 0.45):
        """
        Ejecuta detección usando un modelo YOLO.
        Devuelve:
        - array con [x1, y1, x2, y2, L, class_id]
        - Confianza
        - lista de nombres de clase detectadas
        """
        if self.model is None:  # ✅ Usa self.model
            print(" No hay modelo cargado")
            return np.zeros((0, 6), dtype=float), [], []

        try:
            results = self.model(image_path, conf=conf, iou=iou, device='cpu')  # ✅ Usa self.model
            r = results[0]

            if not hasattr(r, "boxes") or r.boxes.xyxy is None:
                return np.zeros((0, 6), dtype=float), [], []

            boxes_xyxy = r.boxes.xyxy.cpu().numpy()
            confidences = r.boxes.conf.cpu().numpy()
            class_ids = r.boxes.cls.cpu().numpy().astype(int)

            # L es un valor auxiliar generado aleatoriamente
            random_L = np.random.randint(0, 10, size=(boxes_xyxy.shape[0], 1))

            class_names = [self.model.names[cid] for cid in class_ids]  # ✅ Usa self.model.names

            output = np.hstack([
                boxes_xyxy,
                random_L.astype(float),
                class_ids.reshape(-1, 1).astype(float)
            ])

            return output, confidences, class_names

        except Exception as e:
            print(f" Error en detección: {type(e).__name__}: {e}")
            return np.zeros((0, 6), dtype=float), [], []


    def get_data(self, img_path):
        """
        Procesa una imagen y devuelve DataFrame con los defectos detectados
        """
        print(f"relizando deteccion en frame...")
        detecciones, confianzas, nombres_clases = self.detector(img_path)
        print(f"PASO DETECCION")
        if len(detecciones) > 0:
            # Aplicar filtro de defectos repetidos
            print(f"filtrando repetidos en frame...")
            es_repetido = self.filtrar_defectos_repetidos(detecciones)
            
            if not es_repetido:
                # GUARDAR IMAGEN Y ANOTACIONES solo si no es repetida
                print(f"gurdando imagen con defecto en frame...")
                img_original = cv2.imread(img_path)
                self.guardar_para_trained_models(detecciones, img_original, img_path)
            else:
                print(f"⚠️ Defecto repetido detectado en {img_path}, no se guardará")
                # Eliminar la imagen si es repetida
                try:
                    os.remove(img_path)
                    print(f"🗑️ Imagen repetida eliminada: {img_path}")
                except Exception as e:
                    print(f"⚠️ Error al eliminar imagen repetida: {e}")
                
                # Retornar DataFrame vacío para imágenes repetidas
                columns = ["name", "image_path", "eje_x", "eje_y", "eje_x2","eje_y2", "largo", 
                        "etiqueta", "prediccion", "modelo_correa", "fecha_registro", "confianza", "clase"]
                return pd.DataFrame(columns=columns)
        
        if detecciones.shape[0] == 0:
            # No hay detecciones, retornar DataFrame vacío
            columns = ["name", "image_path", "eje_x", "eje_y", "eje_x2","eje_y2", "largo", 
                    "etiqueta", "prediccion", "modelo_correa", "fecha_registro", "confianza", "clase"]
            return pd.DataFrame(columns=columns)

        # Convertir detecciones a formato requerido
        data_list = []
        base_date = datetime.now()

        nombre_archivo = os.path.basename(img_path)
        #  zip para iterar simultáneamente sobre los 3 arrays
        for i, (deteccion, confianza, nombre_clase) in enumerate(zip(detecciones, confianzas, nombres_clases)):
            # cada detección tiene 6 valores
            x1, y1, x2, y2, largo, class_id = deteccion
            
            # Generar datos según especificaciones
            name = f"{nombre_archivo}"
            image_path = img_path
            eje_x = int(x1)  # Primer punto X
            eje_y = int(y1)  # Primer punto Y  
            eje_x2 = int(x2)  # Primer punto X
            eje_y2 = int(y2)  # Segundo punto Y
            largo_val = int(largo)  # Último dato de la detección
            etiqueta = None
            prediccion = nombre_clase  # Usar el nombre real de la clase
            modelo_correa = self.modelo_correa_actual
            fecha_registro = (base_date).strftime("%Y-%m-%d %H:%M:%S")

            data_list.append([
                name, image_path, eje_x, eje_y, eje_x2, eje_y2, largo_val,
                etiqueta, prediccion, modelo_correa, fecha_registro,
                float(confianza), nombre_clase 
            ])

        # Crear DataFrame con columnas actualizadas
        columns = ["name", "image_path", "eje_x", "eje_y", "eje_x2","eje_y2", "largo",
                "etiqueta", "prediccion", "modelo_correa", "fecha_registro",
                "confianza", "clase"]
        
        return pd.DataFrame(data_list, columns=columns)
    
    def set_modelo_correa(self, modelo):
        """Establece el modelo de correa para todas las detecciones posteriores"""
        self.modelo_correa_actual = modelo    
    
    ########### Funciones Leonardo ################
    def guardar_detecciones_modelo(self, boxes_with_L, label_path: str, frame_shape):
        """Guarda detecciones en formato YOLO .txt"""
        if not self.flag_creado:
            trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
            datasets_path = trained_models_path / "datasets"
            self.nuevo_dataset_path = DatasetFolderManager.crear_dataset(datasets_path)
            self.flag_creado = True
        
        h, w = frame_shape[:2]
        with open(label_path, "w") as f:
            for box in boxes_with_L:
                x1, y1, x2, y2, _, class_id = box 
                cid = int(class_id)
                xc = ((x1 + x2) / 2) / w
                yc = ((y1 + y2) / 2) / h
                bw = (x2 - x1) / w
                bh = (y2 - y1) / h
                f.write(f"{cid} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

    def archivar_modelo(self, modelo_pkl_path: str):
        """Copia el modelo a la carpeta de modelos utilizados"""
        trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
        modelos_dir = trained_models_path / "modelos_utilizados"
        modelos_dir.mkdir(exist_ok=True)
        
        nombre_pkl = os.path.basename(modelo_pkl_path)
        destino = modelos_dir / nombre_pkl
        shutil.copy2(modelo_pkl_path, destino)
        print(f"✅ Modelo archivado en: {destino}")
        return str(destino)
    
    def reentrenar(self, epochs: int = 50, imgsz: int = 640):
        """
        Función completa de re-entrenamiento adaptada del programador novato
        """
        try:
            # 1. Crear estructura de dataset usando TU sistema
            trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
            datasets_path = trained_models_path / "datasets"
            
            #if not self.flag_creado:
            self.nuevo_dataset_path = DatasetFolderManager.crear_dataset(datasets_path)
            #    self.flag_creado = True
            
            # 2. Distribuir datos usando TU sistema
            DatasetFolderManager.distribuir_dataset(
                self.nuevo_dataset_path,
                source_root=trained_models_path,
                ratios=(0.8, 0.1, 0.1),
                overwrite=False,
                seed=42
            )
            
            # 3. Copiar datos anteriores usando TU sistema
            DatasetFolderManager.copiar_desde_dataset_anterior(
                self.nuevo_dataset_path,
                datasets_root=datasets_path,
                copiar_solo_pares_nuevos=True,
                overwrite=False
            )
            
            # 4. Validar dataset
            resultado_validacion = DatasetFolderManager.validar_pares_dataset(self.nuevo_dataset_path)
            
            # 5. Re-entrenamiento 
            root = str(datasets_path)
            existentes = [d for d in os.listdir(root)
                          if d.startswith("dataset") and os.path.isdir(os.path.join(root, d))]
            existentes.sort(key=lambda x: int(x.replace("dataset", "")))
            
            actual = os.path.basename(str(self.nuevo_dataset_path))
            idx = existentes.index(actual)
            
            if idx == 0:
                raise ValueError("No hay dataset anterior para reentrenar")
                
            anterior = existentes[idx-1]
            prev_num = int(anterior.replace("dataset", ""))
            modelo_prev = f"Modelo{prev_num}.pkl"
            modelo_base = os.path.normpath(os.path.join(root, anterior, modelo_prev))
            data_yaml = os.path.normpath(os.path.join(str(self.nuevo_dataset_path), "data.yaml"))
            output_dir = os.path.normpath(os.path.join(str(self.nuevo_dataset_path), "reentreno"))
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Cargar modelo base
            with open(modelo_base, "rb") as f:
                model = pickle.load(f)
            
            # Entrenar
            dataset_folder = os.path.basename(os.path.normpath(str(self.nuevo_dataset_path)))
            dataset_num = dataset_folder.replace("dataset", "")
            run_name = f"dataset{dataset_num}_reentreno"
            
            model.train(
                data=data_yaml,
                epochs=epochs,
                imgsz=imgsz,
                project=output_dir,
                name=run_name,
                exist_ok=True
            )
            
            # Evaluar
            results = model.val(data=data_yaml, verbose=False)
            metrics = {
                "mAP50": results.box.map50.cpu().item(),
                "mAP5095": results.box.map.cpu().item(),
                "precision": results.box.precision.cpu().item(),
                "recall": results.box.recall.cpu().item()
            }
            
            # Guardar nuevo modelo
            best_pt = os.path.join(output_dir, run_name, "weights", "best.pt")
            best_model = YOLO(best_pt)
            
            modelo_pkl = os.path.join(str(self.nuevo_dataset_path), f"Modelo{dataset_num}.pkl")
            with open(modelo_pkl, "wb") as f:
                pickle.dump(best_model, f)
            
            # Archivar modelo anterior
            self.archivar_modelo(modelo_base)
            
            print(f"✅ Reentrenamiento completo. Métricas: {metrics}")
            accuracy_porcentaje = metrics.get("mAP50", 0) * 100
            nombre_modelo = f"Modelo{dataset_num}"
            return True, metrics, modelo_pkl, accuracy_porcentaje, nombre_modelo
            
        except Exception as e:
            error_msg = f"❌ Error en re-entrenamiento: {str(e)}"
            print(error_msg)
            return False, error_msg, None

    # Funciones de filtrado de defectos repetidos 
    def iou_proyectado_en_x(self, box1, box2):
        x1A, x2A = box1[0], box1[2]
        x1B, x2B = box2[0], box2[2]
        inter_x = max(0, min(x2A, x2B) - max(x1A, x1B))
        ancho_A = x2A - x1A
        ancho_B = x2B - x1B
        union_x = ancho_A + ancho_B - inter_x
        return inter_x / (union_x + 1e-6)

    def es_repetido(self, box_actual, boxes_previas, umbral_iou_x=0.5, umbral_dy=30):
        for box in boxes_previas:
            dy = abs(box_actual[1] - box[1])
            if dy <= umbral_dy:
                iou_x = self.iou_proyectado_en_x(box_actual, box)
                if iou_x >= umbral_iou_x:
                    return True
        return False

    def filtrar_defectos_repetidos(self, detecciones):
        """Filtra defectos repetidos basado en detecciones anteriores"""
        if not detecciones.size > 0:
            return False
        
        # Si no hay detecciones anteriores, guardar las actuales y retornar False
        if not self.boxes_previas:
            self.boxes_previas = [det[:4].tolist() for det in detecciones]
            return False
        
        # Verificar si alguna detección actual es repetida
        es_repetido_total = False
        for deteccion in detecciones:
            box_actual = deteccion[:4].tolist()
            if self.es_repetido(box_actual, self.boxes_previas, self.umbral_iou_x, self.umbral_dy):
                es_repetido_total = True
                self.repetidos += 1
                break
        
        # Actualizar detecciones anteriores con las actuales
        self.boxes_previas = [det[:4].tolist() for det in detecciones]
        
        return es_repetido_total

    def resetear_filtro(self):
        """Resetea el estado del filtro de defectos repetidos"""
        self.boxes_previas = []
        self.repetidos = 0
        print("✅ Filtro de defectos repetidos reseteado")  

    def guardar_detecciones_modelo(self, boxes_with_L, label_path: str, frame_shape):
        """Guarda detecciones en formato YOLO .txt"""
        h, w = frame_shape[:2]
        with open(label_path, "w") as f:
            for box in boxes_with_L:
                x1, y1, x2, y2, _, class_id = box 
                cid = int(class_id)
                xc = ((x1 + x2) / 2) / w
                yc = ((y1 + y2) / 2) / h
                bw = (x2 - x1) / w
                bh = (y2 - y1) / h
                f.write(f"{cid} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")         

    # ===== GUARDADO PARA TRAINED_MODELS =====
    def guardar_para_trained_models(self, detecciones, frame, image_path_original):
        """Guarda COPIA de imagen y anotaciones en trained_models/"""
        trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
        images_dir = trained_models_path / "images"
        labels_dir = trained_models_path / "labels"
        
        images_dir.mkdir(exist_ok=True)
        labels_dir.mkdir(exist_ok=True)
        
        # COPIAR imagen (no moverla)
        image_name = os.path.basename(image_path_original)
        target_image_path = images_dir / image_name
        
        # Verificar si ya existe para evitar sobreescribir
        if not os.path.exists(target_image_path):
            cv2.imwrite(str(target_image_path), frame)
        
        # Guardar anotaciones YOLO
        label_name = os.path.splitext(image_name)[0] + ".txt"
        label_path = labels_dir / label_name
        
        h, w = frame.shape[:2]
        with open(label_path, "w") as f:
            for box in detecciones:
                x1, y1, x2, y2, _, class_id = box 
                cid = int(class_id)
                xc = ((x1 + x2) / 2) / w
                yc = ((y1 + y2) / 2) / h
                bw = (x2 - x1) / w
                bh = (y2 - y1) / h
                f.write(f"{cid} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

    # ===== CREACIÓN DE DATAFRAME PARA TREEVIEW =====
    def crear_dataframe_desde_detecciones(self, detecciones, confianzas, nombres_clases, image_path):
        """Crea DataFrame para mostrar en treeview"""
        if detecciones.shape[0] == 0:
            columns = ["name", "image_path", "eje_x", "eje_y", "eje_x2","eje_y2", "largo", 
                    "etiqueta", "prediccion", "modelo_correa", "fecha_registro", "confianza", "clase"]
            return pd.DataFrame(columns=columns)

        data_list = []
        base_date = datetime.now()

        for i, (deteccion, confianza, nombre_clase) in enumerate(zip(detecciones, confianzas, nombres_clases)):
            x1, y1, x2, y2, largo, class_id = deteccion
            
            name = f"Defecto_{i+1:03d}"
            eje_x = int(x1)
            eje_y = int(y1)
            eje_x2 = int(x2)
            eje_y2 = int(y2)
            largo_val = int(largo)
            etiqueta = None
            prediccion = nombre_clase
            modelo_correa = self.modelo_correa_actual
            fecha_registro = (base_date - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")

            data_list.append([
                name, image_path, eje_x, eje_y, eje_x2, eje_y2, largo_val,
                etiqueta, prediccion, modelo_correa, fecha_registro,
                float(confianza), nombre_clase
            ])

        columns = ["name", "image_path", "eje_x", "eje_y", "eje_x2","eje_y2", "largo",
                "etiqueta", "prediccion", "modelo_correa", "fecha_registro",
                "confianza", "clase"]
        
        return pd.DataFrame(data_list, columns=columns)

    def set_modelo_correa(self, modelo):
        """Establece el modelo de correa para todas las detecciones posteriores"""
        self.modelo_correa_actual = modelo      

    # ===== FUNCIÓN COMPLETA DE RE-ENTRENAMIENTO CORREGIDA =====
    def reentrenar(self, epochs: int = 50, imgsz: int = 640, progress_callback=None):
        """
        Función completa de re-entrenamiento adaptada del programador novato
        """
        try:
            # 1. Obtener paths base
            trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
            datasets_path = trained_models_path / "datasets"
            
            # 2. Crear nuevo dataset
            self.nuevo_dataset_path = DatasetFolderManager.crear_dataset(datasets_path)
            
            # 3. Distribuir datos desde trained_models/images y /labels
            DatasetFolderManager.distribuir_dataset(
                self.nuevo_dataset_path,
                source_root=trained_models_path,
                ratios=(0.8, 0.1, 0.1),
                overwrite=False,
                seed=42
            )
            
            # 4. VERIFICAR SI ES PRIMER RE-ENTRENAMIENTO O NO
            existentes = [d for d in os.listdir(datasets_path) 
                         if d.startswith("dataset") and os.path.isdir(datasets_path / d)]
            existentes.sort(key=lambda x: int(x.replace("dataset", "")))
            
            if len(existentes) <= 1:  # Primer re-entrenamiento
                print("🚀 Primer re-entrenamiento - Usando Modelo0.pkl como base")
                modelo_base = self._obtener_modelo_base_primer_entrenamiento(trained_models_path)
            else:
                # 5. Copiar datos desde dataset anterior (para re-entrenamientos posteriores)
                DatasetFolderManager.copiar_desde_dataset_anterior(
                    self.nuevo_dataset_path,
                    datasets_root=datasets_path,
                    copiar_solo_pares_nuevos=True,
                    overwrite=False
                )
                
                # 6. Identificar modelo anterior
                actual = os.path.basename(str(self.nuevo_dataset_path))
                idx = existentes.index(actual)
                
                if idx == 0:
                    modelo_base = self._obtener_modelo_base_primer_entrenamiento(trained_models_path)
                else:
                    anterior = existentes[idx-1]
                    prev_num = int(anterior.replace("dataset", ""))
                    modelo_prev = f"Modelo{prev_num}.pkl"
                    modelo_base = datasets_path / anterior / modelo_prev
            
            # 7. Validar dataset
            resultado_validacion = DatasetFolderManager.validar_pares_dataset(self.nuevo_dataset_path)
            print(f"✅ Dataset validado: {resultado_validacion['totales']}")
            
            # 8. Configurar paths
            data_yaml = self.nuevo_dataset_path / "data.yaml"
            output_dir = self.nuevo_dataset_path / "reentreno"
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"🔍 Modelo base: {modelo_base}")
            print(f"🗂  data.yaml: {data_yaml}")
            print(f"📁 Salida: {output_dir}")
            
            # 9. Cargar modelo base
            if not os.path.exists(modelo_base):
                raise FileNotFoundError(f"No se encontró el modelo base: {modelo_base}")
                
            # Cargar modelo base
            with open(modelo_base, "rb") as f:
                model = pickle.load(f)
            
            # Variable para almacenar resultados del entrenamiento
            training_results = {}
            
            # Función que se ejecutará en el hilo
            def train_and_evaluate():
                try:
                    if progress_callback:
                        progress_callback("Entrenando modelo...")
                    
                    # Entrenar
                    dataset_folder = os.path.basename(os.path.normpath(str(self.nuevo_dataset_path)))
                    dataset_num = dataset_folder.replace("dataset", "")
                    run_name = f"dataset{dataset_num}_reentreno"
                    
                    model.train(
                        data=data_yaml,
                        epochs=epochs,
                        imgsz=imgsz,
                        project=output_dir,
                        name=run_name,
                        exist_ok=True
                    )
                    
                    if progress_callback:
                        progress_callback("Evaluando modelo...")
                    
                    # Evaluar
                    results = model.val(data=data_yaml, verbose=False)
                    
                    # Las métricas pueden ser tensores o valores numéricos directamente
                    def safe_extract_metric(metric_value):
                        if hasattr(metric_value, 'cpu'):
                            return metric_value.cpu().item()
                        elif hasattr(metric_value, 'item'):
                            return metric_value.item()
                        else:
                            return float(metric_value)
                    
                    metrics = {
                        "mAP50": safe_extract_metric(results.box.map50),
                        "mAP5095": safe_extract_metric(results.box.map),
                        "precision": safe_extract_metric(results.box.mp),  # mp es mean precision
                        "recall": safe_extract_metric(results.box.mr)      # mr es mean recall
                    }
                    
                    if progress_callback:
                        progress_callback("Guardando modelo entrenado...")
                    
                    # Guardar nuevo modelo
                    best_pt = os.path.join(output_dir, run_name, "weights", "best.pt")
                    best_model = YOLO(best_pt)
                    
                    modelo_pkl = os.path.join(str(self.nuevo_dataset_path), f"Modelo{dataset_num}.pkl")
                    with open(modelo_pkl, "wb") as f:
                        pickle.dump(best_model, f)
                    
                    training_results.update({
                        'success': True,
                        'metrics': metrics,
                        'modelo_pkl': modelo_pkl,
                        'best_pt': best_pt,
                        'accuracy_porcentaje': metrics["mAP50"] * 100,
                        'nombre_modelo': f"Modelo{dataset_num}" 
                    })
                    
                except Exception as e:
                    training_results['error'] = str(e)
                    training_results['success'] = False
                    import traceback
                    traceback.print_exc()
            
            # Crear y ejecutar el hilo para entrenamiento
            train_thread = threading.Thread(target=train_and_evaluate)
            train_thread.start()
            
            # Esperar a que el hilo termine
            while train_thread.is_alive():
                # Aquí puedes actualizar la barra de progreso si lo deseas
                if progress_callback:
                    progress_callback("Entrenamiento en progreso...")
                train_thread.join(timeout=1)  # Esperar 1 segundo y verificar de nuevo
            
            # Verificar resultados del entrenamiento
            if 'error' in training_results:
                raise Exception(training_results['error'])
            
            if not training_results.get('success', False):
                raise Exception("El entrenamiento falló sin error específico")
            
            metrics = training_results['metrics']
            modelo_pkl = training_results['modelo_pkl']
            best_pt = training_results['best_pt']
            
            if progress_callback:
                progress_callback("Archivando modelo anterior...")
            
            # Archivar modelo anterior
            if progress_callback:
                progress_callback("Archivando modelo anterior...")
            
            print(f"✅ Reentrenamiento completo. Métricas: {metrics}")
            return True, metrics, modelo_pkl, training_results.get('accuracy_porcentaje'), training_results.get('nombre_modelo')
            
        except Exception as e:
            error_msg = f"❌ Error en re-entrenamiento: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return False, error_msg, None, None, None

    def _obtener_modelo_base_primer_entrenamiento(self, trained_models_path):
        """
        Obtiene el Modelo0.pkl para el primer re-entrenamiento
        """
        modelo0_path = trained_models_path / "modelos_utilizados" / "Modelo0.pkl"
        
        if not modelo0_path.exists():
            # Buscar en otras ubicaciones posibles
            modelo0_alternativo = trained_models_path / "Modelo0.pkl"
            if modelo0_alternativo.exists():
                return modelo0_alternativo
            else:
                raise FileNotFoundError(
                    "No se encontró Modelo0.pkl para el primer re-entrenamiento. "
                    "Coloca Modelo0.pkl en trained_models/modelos_utilizados/"
                )
        
        return modelo0_path

    def archivar_modelo(self, modelo_pkl_path: str):
        """Archiva el modelo anterior, excepto Modelo0"""

        if isinstance(modelo_pkl_path, Path):
            modelo_pkl_path = str(modelo_pkl_path)

        if "Modelo0.pkl" in modelo_pkl_path:
            print("ℹ️ Modelo0 no se archiva (es el modelo base)")
            return None
            
        try:
            trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
            modelos_dir = trained_models_path / "modelos_utilizados"
            modelos_dir.mkdir(exist_ok=True)
            
            nombre_pkl = os.path.basename(modelo_pkl_path)
            destino = modelos_dir / nombre_pkl
            
            if not destino.exists():
                shutil.copy2(modelo_pkl_path, destino)
                print(f"📦 Modelo archivado: {destino}")
            else:
                print(f"ℹ️ Modelo ya archivado: {destino}")
                
            return str(destino)
            
        except Exception as e:
            print(f"⚠️ Error archivando modelo: {e}")
            return None
        
    def _obtener_modelo_mas_reciente(self):
        """
        Busca y retorna la ruta del modelo .pkl más reciente en modelos_utilizados/
        Si no hay modelos, usa ModeloBase.pkl como fallback
        """
        try:
            trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
            modelos_dir = trained_models_path / "modelos_utilizados"
            
            # Buscar todos los archivos .pkl en la carpeta
            modelos = []
            if modelos_dir.exists():
                for archivo in modelos_dir.iterdir():
                    if archivo.is_file() and archivo.suffix == '.pkl':
                        modelos.append(archivo)
            
            # También buscar en la raíz de trained_models por compatibilidad
            for archivo in trained_models_path.iterdir():
                if archivo.is_file() and archivo.suffix == '.pkl' and archivo.name != "ModeloBase.pkl":
                    modelos.append(archivo)
            
            if not modelos:
                # No hay modelos, usar ModeloBase.pkl como último recurso
                modelo_base = trained_models_path / "ModeloBase.pkl"
                if modelo_base.exists():
                    print(f"⚠️ No hay modelos en modelos_utilizados/, usando ModeloBase.pkl")
                    return str(modelo_base)
                else:
                    raise FileNotFoundError("No se encontró ningún modelo .pkl")
            
            # Extraer números de modelo y encontrar el más reciente
            modelo_mas_reciente = None
            numero_mas_alto = -1
            
            for modelo_path in modelos:
                nombre = modelo_path.stem  # Nombre sin extensión
                
                # Buscar patrones: ModeloX.pkl donde X es número
                match = re.search(r'Modelo(\d+)', nombre)
                if match:
                    numero = int(match.group(1))
                    if numero > numero_mas_alto:
                        numero_mas_alto = numero
                        modelo_mas_reciente = modelo_path
                elif nombre == "ModeloBase":
                    # ModeloBase tiene prioridad baja (número 0)
                    if numero_mas_alto < 0:
                        numero_mas_alto = 0
                        modelo_mas_reciente = modelo_path
            
            if modelo_mas_reciente:
                print(f"✅ Cargando modelo más reciente: {modelo_mas_reciente.name}")
                return str(modelo_mas_reciente)
            else:
                # Si no se encontraron modelos con patrón, usar el primero
                print(f"⚠️ No se encontraron modelos con patrón ModeloX, usando: {modelos[0].name}")
                return str(modelos[0])
                
        except Exception as e:
            print(f"❌ Error buscando modelo más reciente: {e}")
            # Fallback a ModeloBase.pkl
            trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
            modelo_base = trained_models_path / "ModeloBase.pkl"
            if modelo_base.exists():
                return str(modelo_base)
            else:
                raise FileNotFoundError("No se pudo encontrar ningún modelo .pkl")

    def procesar_video(self, video_path, frame_interval=1):
        """
        Procesa un video extrayendo frames y guardando en carpeta Imagenes
        """
        try:
            import cv2
            import os
            
            print(f"🎥 Procesando video: {video_path}")
            
            all_detections = []
            frame_count = 0
            
            # USAR TU CARPETA "Imagenes" 
            output_dir = os.path.join(os.getcwd(), "Imagenes")
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"📁 Guardando frames en: {output_dir}")
            
            # Abrir video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"❌ No se pudo abrir el video: {video_path}")
                return all_detections
            
            # Procesar video
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Procesar cada frame_interval frames
                if frame_count % frame_interval == 0:
                    # Guardar frame en CARPETA IMAGENES
                    frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
                    cv2.imwrite(frame_path, frame)
                    
                    # Procesar frame con get_data()
                    print(f"Procesando frame: {frame_count}")
                    frame_results = self.get_data(frame_path)
                    
                    if not frame_results.empty:
                        print(f"   📸 Frame {frame_count}: {len(frame_results)} defectos")
                        all_detections.append(frame_results)
                
                frame_count += 1
            
            cap.release()
            
            # Combinar todos los resultados
            if all_detections:
                final_results = pd.concat(all_detections, ignore_index=True)
                print(f"✅ Video procesado: {frame_count} frames, {len(final_results)} defectos totales")
            else:
                final_results = pd.DataFrame()
                print("ℹ️ No se encontraron defectos en el video")
            
            return final_results
                
        except Exception as e:
            print(f"❌ Error procesando video: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()