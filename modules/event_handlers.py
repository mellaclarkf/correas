from tkinter import messagebox
from views.ReportWindow import ReportWindow
from views.settings_window import SettingsWindow
import pandas as pd
import threading
import os

class EventHandlers:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def on_closing_main_window(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            self.main_window.destroy()
            self.main_window.master.destroy()
            
    def recargar_cambios(self):

        from helpers.treeview_helper import obtener_filas_modificadas
    
        # Usar el método que ya tienes para detectar cambios
        filas_modificadas = obtener_filas_modificadas(
            self.main_window.tree, 
            self.main_window.treeview_manager.etiquetas_originales
            )
            # Si NO hay cambios, mostrar mensaje y salir
        if not filas_modificadas:
            messagebox.showinfo("Re-entrenar", "No hay cambios en las etiquetas para re-entrenar.")
            return
        
        if messagebox.askyesno("Re-entrenar", "¿Deseas re-entrenar el modelo con las nuevas etiquetas?"):
            # Mostrar loading
            self.main_window.show_loading("Iniciando re-entrenamiento...")
            
            # Ejecutar en hilo separado
            thread = threading.Thread(target=self._reentrenar_en_hilo, daemon=True)
            thread.start()
            
    def _reentrenar_en_hilo(self):
        try:
            # Procesar cambios en etiquetas antes de reentrenar
            self._procesar_cambios_etiquetas()

            success, result, modelo_pkl, accuracy_porcentaje, nombre_modelo = self.main_window.controller.reentrenar_modelo()
            
            if success and accuracy_porcentaje is not None:
                # Programar la inserción en BD para ejecutarse en el hilo principal
                self.main_window.after(0, self._guardar_accuracy_en_bd, accuracy_porcentaje, nombre_modelo)
            
            # Actualizar UI en el hilo principal
            self.main_window.after(0, self._mostrar_resultado_reentrenamiento, success, result, modelo_pkl)
            
        except Exception as e:
            self.main_window.after(0, self._mostrar_error, str(e))
        finally:
            self.main_window.after(0, self.main_window.hide_loading)
    
    def _mostrar_resultado_reentrenamiento(self, success, result, modelo_pkl):
        if success:
            messagebox.showinfo("Re-entrenamiento", 
                              f"✅ Re-entrenamiento completado\n"
                              f"📊 mAP50: {result['mAP50']:.3f}\n"
                              f"💾 Modelo: {os.path.basename(modelo_pkl)}")
            self.main_window.actualizar_accuracy_display()
        else:
            messagebox.showerror("Error", f"❌ {result}")
    
    def _mostrar_error(self, error_msg):
        messagebox.showerror("Error", f"Error durante el re-entrenamiento: {error_msg}")
        
    def mostrar_reporte(self):
        ReportWindow(self.main_window)
        
    def open_settings_window(self):
        settings_window = SettingsWindow(self.main_window, self.main_window.controller)
        settings_window.grab_set()
        self.main_window.wait_window(settings_window)
        
    def eliminar_fila_por_id(self, item_id):
        self.main_window.treeview_manager.eliminar_fila_por_id(item_id)

    def _guardar_accuracy_en_bd(self, accuracy_porcentaje, nombre_modelo):
        """Guarda el accuracy solo si es mejor que el existente"""
        try:
            from services.modelo_service import ModeloService
            modelo_service = ModeloService(self.main_window.db_session)
            
            es_mejor = modelo_service.actualizar_si_es_mejor_modelo(accuracy_porcentaje, nombre_modelo)
            
            if es_mejor:
                print(f"✅ NUEVO MEJOR modelo: {nombre_modelo} ({accuracy_porcentaje:.2f}%)")
                # Actualizar el modelo en uso
                self.main_window.controller.boundingbox_service.cargar_mejor_modelo()
            else:
                print(f"ℹ️ Modelo {nombre_modelo} ({accuracy_porcentaje:.2f}%) no supera el mejor actual")
                
            # Actualizar el label de accuracy en la UI
            if hasattr(self.main_window, 'actualizar_accuracy_display'):
                self.main_window.actualizar_accuracy_display()
                
        except Exception as e:
            print(f"❌ Error guardando accuracy en BD: {e}")

    # Actualiza los archivos que se les ha cambiado etiqueta o agrega si es es un defecto nuevo
    def _procesar_cambios_etiquetas(self):
        """Procesa los cambios de etiquetas y actualiza los archivos correspondientes"""
        from helpers.treeview_helper import obtener_filas_modificadas
        from utils.folder_dataset import DatasetFolderManager
        from pathlib import Path
        
        # Obtener filas modificadas
        filas_modificadas = obtener_filas_modificadas(
            self.main_window.tree, 
            self.main_window.treeview_manager.etiquetas_originales
        )
        
        if not filas_modificadas:
            return
        
        # Procesar cada fila modificada
        for item_id, etiqueta_actual, etiqueta_original in filas_modificadas:
            valores = self.main_window.tree.item(item_id)["values"]
            
            if len(valores) < 8:
                continue
                
            imagen_path = valores[7]  # Ruta de la imagen
            defect_id = valores[0]    # ID del defecto
            
            # Obtener coordenadas del tag - LOS DEFECTOS MANUALES DEBEN TENER TAG
            tags = self.main_window.tree.item(item_id, "tags")
            coords_tag = next((tag for tag in tags if tag.startswith("coords_")), None)
            
            if not coords_tag:
                # ⚠️ ESTO ES UN ERROR: defecto manual sin coordenadas
                print(f"❌ ERROR: Defecto {defect_id} no tiene coordenadas (tag coords_)")
                continue  # Saltar este defecto - no podemos procesarlo
                
            # Extraer coordenadas del tag
            _, x1, y1, x2, y2 = coords_tag.split("_")
            x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
            
            # Actualizar archivo de etiqueta YOLO
            success_file = DatasetFolderManager.procesar_cambio_etiqueta(
                Path(imagen_path), x1, y1, x2, y2, etiqueta_actual
            )
            
            # Actualizar base de datos
            success_db = self._actualizar_bd_defecto(
                item_id,
                defect_id,           # Para saber si es manual o existente
                valores,             # Todos los valores
                etiqueta_actual,     # Nueva etiqueta  
                imagen_path,         # Ruta de imagen
                x1, y1, x2, y2      # Coordenadas
            )
            
            if success_file and success_db:
                # Actualizar la etiqueta original en el manager
                self.main_window.treeview_manager.etiquetas_originales[item_id] = etiqueta_actual
                print(f"✅ Etiqueta actualizada para {imagen_path}: {etiqueta_original} -> {etiqueta_actual}")
            else:
                print(f"❌ Error actualizando etiqueta para {imagen_path}")

    def _obtener_coordenadas_manuales(self, item_id, valores):
        """
        Intenta obtener coordenadas para defectos manuales que no tienen tag.
        Esto es un fallback para casos donde el tag coords_ no fue creado.
        """
        try:
            # Buscar en el historial o base de datos por el ID del defecto
            defect_id = valores[0]
            
            # Si es un defecto manual, podríamos tener las coordenadas almacenadas
            if hasattr(self.main_window, 'controller') and hasattr(self.main_window.controller, 'historial_repository'):
                defecto = self.main_window.controller.historial_repository.obtener_registro_por_id(defect_id)
                if defecto:
                    return (defecto['eje_x'], defecto['eje_y'], defecto['eje_x2'], defecto['eje_y2'])
            
            # Si no se encuentran coordenadas, usar valores por defecto (esto es un fallback)
            print(f"⚠️ Usando coordenadas por defecto para defecto manual {defect_id}")
            return (100, 100, 200, 200)  # Coordenadas por defecto
            
        except Exception as e:
            print(f"Error obteniendo coordenadas manuales: {e}")
            return (100, 100, 200, 200)  # Coordenadas por defecto

    # event_handlers.py - modificar _actualizar_bd_defecto()
    def _actualizar_bd_defecto(self, item_id, defect_id, valores, etiqueta_actual, imagen_path, x1, y1, x2, y2):
        """Actualiza la base de datos según el tipo de defecto"""
        try:
            # --- CALCULAR TRAMO PARA EL DEFECTO MANUAL ---
            tramo = 0
            if (hasattr(self.main_window, 'imagenes_completas') and 
                hasattr(self.main_window, 'largo_total_correa') and
                imagen_path):  # Solo si tenemos imagen_path
                
                from utils.tramo_utils import calcular_tramo_para_defecto
                
                # Obtener todos los parámetros necesarios
                imagenes_completas = self.main_window.imagenes_completas
                largo_total_correa = self.main_window.largo_total_correa
                tramos_info = getattr(self.main_window.treeview_manager, 'tramos_info', [])
                secciones_correa = getattr(self.main_window, 'secciones_correa', 5)
                desplazamiento_inicial = getattr(self.main_window, 'desplazamiento_inicial', 0)
                
                # Calcular el tramo para este defecto específico
                tramo = calcular_tramo_para_defecto(
                    imagen_path, 
                    imagenes_completas,
                    largo_total_correa,
                    tramos_info,
                    secciones_correa,
                    desplazamiento_inicial
                )
                
                print(f"✅ Tramo calculado para defecto manual: {tramo}")

            # Verificar si es un defecto manual (nuevo) o existente
            if str(defect_id).startswith('manual_'):
                # DEFECTO MANUAL: Insertar en BD (sin pasar el ID temporal)
                from datetime import datetime
                
                ancho_px = abs(x2 - x1)
                alto_px = abs(y2 - y1)   
                
                # Convertir a centímetros
                pixeles_por_metro = getattr(self.main_window, 'pixeles_por_metro', 1000)
                ancho_cm = (ancho_px / pixeles_por_metro) * 100
                alto_cm = (alto_px / pixeles_por_metro) * 100 
                
                # Buscar si ya existe un defecto de la misma imagen para obtener sus metadatos
                modelo_correa = getattr(self.main_window, 'maquina_seleccionada', '')
                
                # Si no encontramos tramo con el cálculo, usar valor por defecto del TreeView
                if tramo == 0:
                    tramo = valores[8] if len(valores) > 8 else 0  # Intentar con el valor actual
                                            
                # Crear el objeto completo para insertar
                defecto_manual = {
                    'name': os.path.basename(imagen_path),  # Nombre del archivo
                    'image_path': imagen_path,
                    'eje_x': int(x1),
                    'eje_y': int(y1),
                    'eje_x2': int(x2),
                    'eje_y2': int(y2),
                    'largo': int(ancho_cm),      # Ancho en cm
                    'ancho': int(alto_cm),       # Alto en cm
                    'etiqueta': etiqueta_actual,
                    'prediccion': etiqueta_actual,
                    'modelo_correa': modelo_correa,
                    'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'tramo': int(tramo)  # ← TRAMO CALCULADO CORRECTAMENTE
                }
                
                # INSERTAR EN BD (la BD asignará ID autoincremental)
                nuevo_id = self.main_window.controller.historial_repository.insertar_defecto_manual(defecto_manual)
                
                if nuevo_id:
                    # Actualizar el TreeView con el NUEVO ID de la BD
                    nuevos_valores = list(valores)
                    nuevos_valores[0] = nuevo_id  # Reemplazar ID temporal por real
                    nuevos_valores[8] = tramo     # Actualizar tramo en TreeView también
                    self.main_window.tree.item(item_id, values=tuple(nuevos_valores))
                    
                    # Actualizar diccionario de etiquetas originales
                    self.main_window.treeview_manager.etiquetas_originales[str(nuevo_id)] = etiqueta_actual
                    if defect_id in self.main_window.treeview_manager.etiquetas_originales:
                        del self.main_window.treeview_manager.etiquetas_originales[defect_id]
                        
                    return True
                return False
                
            else:
                # DEFECTO EXISTENTE: Solo actualizar etiqueta
                try:
                    id_int = int(defect_id)
                    return self.main_window.controller.historial_repository.actualizar_etiqueta_por_id(
                        id_int, etiqueta_actual
                    )
                except ValueError:
                    print(f"⚠️ ID inválido {defect_id} - no es numérico")
                    return False
                    
        except Exception as e:
            print(f"Error actualizando BD para defecto {defect_id}: {e}")
            return False
    
