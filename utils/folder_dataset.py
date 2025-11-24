########################################################
# Manejo de Creacion de carpetas para dataset
#########################################################

# utils/dataset_manager.py
from __future__ import annotations

import os
import sys
import math
import random
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict


class DatasetFolderManager:
    """
    Utilidades para gestionar la estructura de datasets dentro de:
        <instalación>/trained_models/

    Estructura base:
        trained_models/
        ├─ images/
        ├─ labels/
        ├─ datasets/
        │  ├─ dataset1/
        │  │  ├─ train/{images,labels}
        │  │  ├─ valid/{images,labels}
        │  │  ├─ test/{images,labels}
        │  │  └─ data.yaml
        │  ├─ dataset2/
        │  └─ ...
        └─ dataset_log.txt
    """

    # --- Rutas base ---
    # Obtiene ruta de instalacion de programa
    @staticmethod
    def obtener_ruta_instalacion() -> Path:
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        # Este archivo vive en utils/dataset_manager.py → subir un nivel para llegar al raíz del proyecto
        return Path(__file__).resolve().parent.parent

    #Crea (si no existe) y retorna <instalación>/trained_models.
    @staticmethod
    def obtener_ruta_trained_models() -> Path:
        base = DatasetFolderManager.obtener_ruta_instalacion()
        trained_models_dir = base / "trained_models"
        trained_models_dir.mkdir(parents=True, exist_ok=True)
        return trained_models_dir

    # --- Estructura base y creación de datasets ---
    # Crea subcarpetas base dentro de trained_models: images/, labels/, datasets/
    @staticmethod
    def crear_estructura_base(trained_models_path: Path) -> None:
        for nombre in ["images", "labels", "datasets"]:
            (trained_models_path / nombre).mkdir(parents=True, exist_ok=True)
    
    # Crea una nueva carpeta datasetN con la estructura:
    # train/images, train/labels, valid/images, valid/labels, test/images, test/labels
    # y un data.yaml. También registra la creación en dataset_log.txt.    
    @staticmethod
    def crear_dataset(datasets_path: Path) -> Path:
        # Detectar existentes válidos
        existentes = [
            d for d in datasets_path.iterdir()
            if d.is_dir() and d.name.startswith("dataset")
            and d.name.replace("dataset", "").isdigit()
        ]

        if not existentes:
            nuevo_dataset = datasets_path / "dataset1"
        else:
            numeros = [int(d.name.replace("dataset", "")) for d in existentes]
            nuevo_dataset = datasets_path / f"dataset{max(numeros) + 1}"

        # Subestructura
        subdirs = [
            "train/images", "train/labels",
            "valid/images", "valid/labels",
            "test/images",  "test/labels",
        ]
        for sub in subdirs:
            (nuevo_dataset / sub).mkdir(parents=True, exist_ok=True)

        # data.yaml (rutas relativas a la carpeta del dataset)
        yaml_path = nuevo_dataset / "data.yaml"
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(f"path: {nuevo_dataset}\n")
            f.write("train: train/images\n")
            f.write("val: valid/images\n")
            f.write("test: test/images\n")
            f.write(
                "names:\n"
                "  0: Defecto1\n"
                "  1: Defecto2\n"
                "  2: Defecto3\n"
                "  3: Defecto4\n"
                "  4: Defecto5\n"
            )

        # Log de creación
        trained_models_path = datasets_path.parent  # .../trained_models
        log_path = trained_models_path / "dataset_log.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}] Creado: {nuevo_dataset.name}\n")

        print(f"✅ Dataset creado: {nuevo_dataset.name}")
        return nuevo_dataset

    # --- Distribución de pares segun porcentaje imagen/label hacia un datasetN ---
    @staticmethod
    def distribuir_dataset(
        dataset_path: Path,
        source_root: Optional[Path] = None,
        ratios: Tuple[float, float, float] = (0.8, 0.1, 0.1),
        image_exts: Tuple[str, ...] = (".jpg", ".jpeg", ".png"),
        overwrite: bool = False,
        seed: Optional[int] = None,
    ) -> int:
        """
        Distribuye pares (imagen + label .txt) desde <source_root>/{images,labels}
        hacia <dataset_path>/{train,valid,test}/{images,labels} según 'ratios'.

        - dataset_path: ruta al datasetN recién creado (por ejemplo: .../trained_models/datasets/dataset3)
        - source_root: por defecto usa <instalación>/trained_models
        - overwrite: si False, no sobreescribe archivos ya copiados
        - seed: fija la aleatoriedad (útil para reproducibilidad)
        """
        # Validación de proporciones con tolerancia (evita problemas de float)
        if not math.isclose(sum(ratios), 1.0, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError("Las proporciones (ratios) deben sumar 1.0")

        # Origen por defecto: <instalación>/trained_models
        if source_root is None:
            source_root = DatasetFolderManager.obtener_ruta_trained_models()

        source_imgs = Path(source_root) / "images"
        source_labels = Path(source_root) / "labels"

        if not source_imgs.exists() or not source_labels.exists():
            raise FileNotFoundError(
                f"No se encontraron las carpetas de origen:\n"
                f" - {source_imgs}\n"
                f" - {source_labels}"
            )

        # Listar imágenes que tengan su .txt correspondiente
        imagenes = [f for f in os.listdir(source_imgs) if f.lower().endswith(image_exts)]
        pares = [f for f in imagenes if (source_labels / (Path(f).stem + ".txt")).exists()]

        if seed is not None:
            random.seed(seed)
        random.shuffle(pares)

        total = len(pares)
        if total == 0:
            print("⚠️ No hay pares (imagen+label) para distribuir.")
            return 0

        n_train = int(total * ratios[0])
        n_valid = int(total * ratios[1])

        conjuntos = {
            "train": pares[:n_train],
            "valid": pares[n_train:n_train + n_valid],
            "test": pares[n_train + n_valid:],
        }

        # Asegurar estructura destino (por si algo falta)
        for split in ["train", "valid", "test"]:
            (dataset_path / split / "images").mkdir(parents=True, exist_ok=True)
            (dataset_path / split / "labels").mkdir(parents=True, exist_ok=True)

        # Copiar archivos
        copiados = 0
        for split, archivos in conjuntos.items():
            for img_name in archivos:
                stem = Path(img_name).stem
                label_name = stem + ".txt"

                # Orígenes
                src_img = source_imgs / img_name
                src_label = source_labels / label_name

                # Destinos
                dst_img = dataset_path / split / "images" / img_name
                dst_label = dataset_path / split / "labels" / label_name

                # Control de overwrite
                if not overwrite and (dst_img.exists() or dst_label.exists()):
                    continue

                shutil.copy2(src_img, dst_img)
                shutil.copy2(src_label, dst_label)
                copiados += 1  # contamos pares

        print(f"✅ {copiados} pares distribuidos en {dataset_path} en proporción {ratios}")
        return copiados

    # --- Copia incremental desde datasetN-1 hacia datasetN ---
    @staticmethod
    def copiar_desde_dataset_anterior(
        nuevo_dataset_path: Path,
        datasets_root: Optional[Path] = None,
        exclude_exts: Tuple[str, ...] = (".pkl",),
        overwrite: bool = False,
        copiar_solo_pares_nuevos: bool = True,
        validar_despues: bool = True,
        log: bool = True,
    ) -> Dict[str, int] | Dict[str, object]:
        """
        Copia contenidos desde datasetN-1 -> datasetN, respetando estructura {train,valid,test}/{images,labels}.

        - copiar_solo_pares_nuevos=True: solo copia (img+label) cuyo par completo NO exista en destino.
          * Si falta una de las dos partes en destino, copia la que falta para completar el par.
        - overwrite=False: si un archivo ya existe y no falta su par, no lo reescribe.
        - validar_despues=True: ejecuta validación de pares en datasetN al terminar y lo incluye en el retorno.

        Devuelve dict con contadores y, si validar_despues=True, con resultado de validación.
        """
        # Raíz de datasets (.../trained_models/datasets)
        if datasets_root is None:
            trained_models = DatasetFolderManager.obtener_ruta_trained_models()
            datasets_root = trained_models / "datasets"
        else:
            datasets_root = Path(datasets_root)

        if not datasets_root.exists():
            print(" No existe la carpeta de datasets root:", datasets_root)
            return {"train": 0, "valid": 0, "test": 0, "total": 0}

        # Detectar datasets disponibles
        existentes = [
            d for d in datasets_root.iterdir()
            if d.is_dir() and d.name.startswith("dataset")
            and d.name.replace("dataset", "").isdigit()
        ]
        if len(existentes) < 2:
            print("ℹ️ No hay dataset anterior del cual copiar.")
            return {"train": 0, "valid": 0, "test": 0, "total": 0}

        # Ordenar y tomar el anterior (N-1)
        existentes.sort(key=lambda p: int(p.name.replace("dataset", "")))
        anterior_dataset_path = existentes[-2]

        print(f"⏳ Copiando datos desde {anterior_dataset_path.name} → {nuevo_dataset_path.name} ...")

        # Asegurar estructura destino (por si algo falta)
        for split in ["train", "valid", "test"]:
            (nuevo_dataset_path / split / "images").mkdir(parents=True, exist_ok=True)
            (nuevo_dataset_path / split / "labels").mkdir(parents=True, exist_ok=True)

        def _listar_archivos(dir_path: Path) -> set[str]:
            if not dir_path.exists():
                return set()
            return {p.name for p in dir_path.iterdir() if p.is_file()}

        def _copiar_split(split: str) -> int:
            """
            Copia por split:
            - En origen: considera solo imágenes que tengan su label.
            - En destino:
                * Si copiar_solo_pares_nuevos: copia solo si el par completo NO existe.
                * Si falta una parte del par, copia solo la parte faltante.
                * Si no, respeta 'overwrite'.
            """
            src_img_dir = anterior_dataset_path / split / "images"
            src_lbl_dir = anterior_dataset_path / split / "labels"
            dst_img_dir = nuevo_dataset_path / split / "images"
            dst_lbl_dir = nuevo_dataset_path / split / "labels"

            # Listados
            src_imgs = [p for p in (src_img_dir.iterdir() if src_img_dir.exists() else []) if p.is_file()]
            src_lbls_set = _listar_archivos(src_lbl_dir)
            dst_imgs_set = _listar_archivos(dst_img_dir)
            dst_lbls_set = _listar_archivos(dst_lbl_dir)

            copiados_archivos = 0
            for img_path in src_imgs:
                nombre = img_path.name
                if any(nombre.lower().endswith(ext.lower()) for ext in exclude_exts):
                    continue
                stem = img_path.stem
                lbl_name = f"{stem}.txt"

                # Solo consideramos pares válidos en origen
                if lbl_name not in src_lbls_set:
                    continue

                # Estado en destino
                tiene_img = nombre in dst_imgs_set
                tiene_lbl = lbl_name in dst_lbls_set

                if copiar_solo_pares_nuevos:
                    if not tiene_img and not tiene_lbl:
                        # Par totalmente nuevo → copia ambos
                        shutil.copy2(img_path, dst_img_dir / nombre)
                        shutil.copy2(src_lbl_dir / lbl_name, dst_lbl_dir / lbl_name)
                        copiados_archivos += 2
                        continue
                    # Completar par si falta una de las partes
                    if not tiene_img:
                        shutil.copy2(img_path, dst_img_dir / nombre)
                        copiados_archivos += 1
                    if not tiene_lbl:
                        shutil.copy2(src_lbl_dir / lbl_name, dst_lbl_dir / lbl_name)
                        copiados_archivos += 1
                else:
                    # Copia directa con control de overwrite
                    dst_img = dst_img_dir / nombre
                    dst_lbl = dst_lbl_dir / lbl_name
                    if (not dst_img.exists()) or overwrite:
                        shutil.copy2(img_path, dst_img)
                        copiados_archivos += 1
                    if (not dst_lbl.exists()) or overwrite:
                        shutil.copy2(src_lbl_dir / lbl_name, dst_lbl)
                        copiados_archivos += 1

            return copiados_archivos

        contadores: Dict[str, int] = {s: 0 for s in ["train", "valid", "test"]}
        for split in list(contadores.keys()):
            contadores[split] = _copiar_split(split)
        contadores["total"] = sum(contadores.values())

        print(f"✅ Copia completa. Archivos copiados: {contadores}")

        # Log opcional
        if log:
            trained_models_path = datasets_root.parent  # .../trained_models
            log_path = trained_models_path / "dataset_log.txt"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(
                    f"[{timestamp}] Copiados desde {anterior_dataset_path.name} "
                    f"a {nuevo_dataset_path.name}: {contadores} (solo_pares_nuevos={copiar_solo_pares_nuevos})\n"
                )

        # Validación post-copia
        if validar_despues:
            resultado_validacion = DatasetFolderManager.validar_pares_dataset(nuevo_dataset_path)
            # Adjuntar al dict de respuesta
            respuesta: Dict[str, object] = dict(contadores)
            respuesta["validacion"] = resultado_validacion
            return respuesta

        return contadores

    # --- Validación de pares en un datasetN ---
    @staticmethod
    def validar_pares_dataset(dataset_path: Path) -> Dict[str, object]:
        """
        Valida que en cada split {train,valid,test}:
          - Cada imagen tenga su .txt
          - Cada .txt tenga su imagen
        Devuelve un dict con totales y listas de huérfanos por split.
        """
        reporte: Dict[str, object] = {}
        totales = {"imgs": 0, "lbls": 0, "orphan_imgs": 0, "orphan_lbls": 0}

        def _ext_imagen_existente(imgs_dir: Path, stem: str) -> str:
            for ext in [".jpg", ".jpeg", ".png"]:
                if (imgs_dir / f"{stem}{ext}").exists():
                    return ext
            return ""

        for split in ["train", "valid", "test"]:
            split_dir = dataset_path / split
            imgs_dir = split_dir / "images"
            lbls_dir = split_dir / "labels"

            imgs = set(p.stem for p in (imgs_dir.glob("*") if imgs_dir.exists() else []) if p.is_file())
            lbls = set(p.stem for p in (lbls_dir.glob("*.txt") if lbls_dir.exists() else []) if p.is_file())

            orphan_imgs_stems = sorted(list(imgs - lbls))  # imagen sin label
            orphan_lbls_stems = sorted(list(lbls - imgs))  # label sin imagen

            reporte[split] = {
                "total_imgs": len(imgs),
                "total_labels": len(lbls),
                "orphan_images": [f"{name}{_ext_imagen_existente(imgs_dir, name)}" for name in orphan_imgs_stems],
                "orphan_labels": [f"{name}.txt" for name in orphan_lbls_stems],
            }
            totales["imgs"] += len(imgs)
            totales["lbls"] += len(lbls)
            totales["orphan_imgs"] += len(orphan_imgs_stems)
            totales["orphan_lbls"] += len(orphan_lbls_stems)

        reporte["totales"] = totales

        print(
            f"🔎 Validación '{dataset_path.name}': "
            f"{totales['imgs']} imgs, {totales['lbls']} labels, "
            f"{totales['orphan_imgs']} imágenes huérfanas, {totales['orphan_lbls']} labels huérfanos."
        )
        return reporte

    # --- Log --- Lee el archivo trained_models/dataset_log.txt si existe.
    @staticmethod
    def leer_log(trained_models_path: Path) -> List[str]:
        log_path = trained_models_path / "dataset_log.txt"
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                return f.readlines()
        return []

    # ===== FUNCIONES DE LIMPIEZA =====
    
    @staticmethod
    def limpiar_carpeta_imagenes(images_folder="Imagenes/"):
        """Limpia la carpeta de imágenes de reproducción"""
        try:
            images_path = Path(images_folder)
            
            if images_path.exists():
                # Borrar solo archivos de imagen, no la carpeta
                for archivo in images_path.iterdir():
                    if archivo.is_file():
                        if (archivo.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp'] or 
                            archivo.suffix.lower() == '.txt'):
                            try:
                                archivo.unlink()
                            except Exception as e:
                                print(f"⚠️ No se pudo borrar {archivo}: {e}")
                
                print(f"✅ Carpeta {images_folder} limpiada")
            else:
                # Crear carpeta si no existe
                images_path.mkdir(parents=True, exist_ok=True)
                
        except Exception as e:
            print(f"❌ Error limpiando carpeta {images_folder}: {e}")

    @staticmethod
    def limpiar_carpetas_entrenamiento():
        """Limpia las carpetas images y labels dentro de trained_models"""
        try:
            trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
            images_dir = trained_models_path / "images"
            labels_dir = trained_models_path / "labels"
            
            # Limpiar images
            if images_dir.exists():
                for item in images_dir.iterdir():
                    if item.is_file() and item.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                        try:
                            item.unlink()
                        except Exception as e:
                            print(f"⚠️ No se pudo borrar {item}: {e}")
                print(f"✅ Carpeta {images_dir} limpiada")
            
            # Limpiar labels
            if labels_dir.exists():
                for item in labels_dir.iterdir():
                    if item.is_file() and item.suffix == '.txt':
                        try:
                            item.unlink()
                        except Exception as e:
                            print(f"⚠️ No se pudo borrar {item}: {e}")
                print(f"✅ Carpeta {labels_dir} limpiada")
                
        except Exception as e:
            print(f"❌ Error limpiando carpetas de entrenamiento: {e}")

    @staticmethod
    def limpiar_todas_las_carpetas(images_folder="Imagenes/"):
        """Limpia todas las carpetas relevantes para un nuevo video"""
        DatasetFolderManager.limpiar_carpeta_imagenes(images_folder)
        DatasetFolderManager.limpiar_carpetas_entrenamiento()
        print("✅ Todas las carpetas limpiadas para nuevo video")

    # Para los reentrenamientos
    @staticmethod
    def obtener_ruta_imagenes() -> Path:
        """Obtiene la ruta de la carpeta images"""
        trained_models = DatasetFolderManager.obtener_ruta_trained_models()
        return trained_models / "images"
    
    @staticmethod
    def obtener_ruta_labels() -> Path:
        """Obtiene la ruta de la carpeta labels"""
        trained_models = DatasetFolderManager.obtener_ruta_trained_models()
        return trained_models / "labels"
    
    @staticmethod
    def mapeo_clases_yolo() -> Dict[str, int]:
        """Devuelve el mapeo de nombres de clase a índices YOLO"""
        return {
            "CORTES": 0,
            "CRISTALIZADO": 1,
            "DESGARROS": 2,
            "DESGASTE": 3,
            "DESPRENDIMIENTO": 4,
            "EMPALME": 5,
            "REPARACIONES": 6
        }
    
    @staticmethod
    def mapeo_clases_yolo_inverso() -> Dict[int, str]:
        """Devuelve el mapeo inverso de índices YOLO a nombres de clase"""
        return {v: k for k, v in DatasetFolderManager.mapeo_clases_yolo().items()}
    
    @staticmethod
    def coordenadas_a_formato_yolo(x1: float, y1: float, x2: float, y2: float, 
                                 img_width: int, img_height: int) -> Tuple[float, float, float, float]:
        """Convierte coordenadas absolutas a formato YOLO normalizado"""
        x_center = ((x1 + x2) / 2) / img_width
        y_center = ((y1 + y2) / 2) / img_height
        width = (x2 - x1) / img_width
        height = (y2 - y1) / img_height
        return x_center, y_center, width, height
    
    @staticmethod
    def actualizar_archivo_etiqueta(imagen_path: Path, clase_num: int, 
                                x_center: float, y_center: float, 
                                width: float, height: float,
                                x1: float = None, y1: float = None, 
                                x2: float = None, y2: float = None,
                                tolerancia: float = 0.01) -> bool:
        """
        Actualiza un archivo de etiqueta YOLO. Busca por coordenadas aproximadas
        y solo cambia el número de clase, manteniendo las coordenadas originales.
        """
        labels_dir = DatasetFolderManager.obtener_ruta_labels()
        label_nombre = imagen_path.stem + ".txt"
        label_path = labels_dir / label_nombre
        
        # Crear carpeta labels si no existe
        labels_dir.mkdir(parents=True, exist_ok=True)
        
        lineas_existentes = []
        if label_path.exists():
            with open(label_path, 'r', encoding='utf-8') as f:
                lineas_existentes = f.readlines()
        
        linea_actualizada = False
        
        # Buscar por coordenadas aproximadas si se proporcionan coordenadas originales
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            for i, linea in enumerate(lineas_existentes):
                try:
                    partes = linea.strip().split()
                    if len(partes) == 5:
                        linea_clase = partes[0]
                        linea_x_center = float(partes[1])
                        linea_y_center = float(partes[2])
                        linea_width = float(partes[3])
                        linea_height = float(partes[4])
                        
                        # Convertir de YOLO a coordenadas absolutas para comparación
                        linea_x1 = (linea_x_center - linea_width/2) 
                        linea_y1 = (linea_y_center - linea_height/2)
                        linea_x2 = (linea_x_center + linea_width/2)
                        linea_y2 = (linea_y_center + linea_height/2)
                        
                        # Comparar con tolerancia (usando coordenadas normalizadas)
                        if (abs(linea_x1 - x1) <= tolerancia and
                            abs(linea_y1 - y1) <= tolerancia and
                            abs(linea_x2 - x2) <= tolerancia and
                            abs(linea_y2 - y2) <= tolerancia):
                            
                            # Solo cambiar el número de clase, mantener las coordenadas originales
                            nueva_linea = f"{clase_num} {partes[1]} {partes[2]} {partes[3]} {partes[4]}\n"
                            lineas_existentes[i] = nueva_linea
                            linea_actualizada = True
                            break
                except (ValueError, IndexError):
                    continue
        
        # Si no se encontró por coordenadas, añadir nueva línea completa
        if not linea_actualizada:
            nueva_linea = f"{clase_num} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
            lineas_existentes.append(nueva_linea)
            linea_actualizada = True
        
        # Escribir el archivo actualizado
        if linea_actualizada:
            with open(label_path, 'w', encoding='utf-8') as f:
                f.writelines(lineas_existentes)
        
        return linea_actualizada
    
    @staticmethod
    def copiar_imagen_entrenamiento(imagen_path: Path) -> bool:
        """Copia una imagen a la carpeta de entrenamiento si no existe"""
        images_dir = DatasetFolderManager.obtener_ruta_imagenes()
        imagen_destino = images_dir / imagen_path.name
        
        # Crear carpeta images si no existe
        images_dir.mkdir(parents=True, exist_ok=True)
        
        if not imagen_destino.exists():
            try:
                shutil.copy2(imagen_path, imagen_destino)
                return True
            except Exception as e:
                print(f"Error copiando imagen: {e}")
                return False
        return True
    
    @staticmethod
    def procesar_cambio_etiqueta(imagen_path: Path, x1: float, y1: float, x2: float, y2: float,
                           etiqueta_actual: str) -> bool:
        """
        Procesa completo el cambio de una etiqueta
        """
        from PIL import Image
        try:
            # Copiar imagen si es necesario
            DatasetFolderManager.copiar_imagen_entrenamiento(Path(imagen_path))
            
            # Obtener dimensiones de la imagen
            with Image.open(imagen_path) as img:
                img_width, img_height = img.size
            
            # Convertir a formato YOLO
            x_center, y_center, width, height = DatasetFolderManager.coordenadas_a_formato_yolo(
                x1, y1, x2, y2, img_width, img_height
            )
            
            # Obtener clase numérica
            mapeo = DatasetFolderManager.mapeo_clases_yolo()
            clase_num = mapeo.get(etiqueta_actual.upper(), -1)
            if clase_num == -1:
                return False
            
            # Normalizar coordenadas para comparación (0-1)
            x1_norm = x1 / img_width
            y1_norm = y1 / img_height
            x2_norm = x2 / img_width
            y2_norm = y2 / img_height
            
            # Actualizar archivo de etiqueta usando coordenadas para búsqueda
            return DatasetFolderManager.actualizar_archivo_etiqueta(
                Path(imagen_path), clase_num, x_center, y_center, width, height,
                x1_norm, y1_norm, x2_norm, y2_norm
            )
            
        except Exception as e:
            print(f"Error procesando cambio de etiqueta: {e}")
            return False

