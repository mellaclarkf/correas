# treeview_manager.py
import os
from helpers.treeview_helper import insertar_defectos_en_treeview, ajustar_ancho_columnas
from helpers.combobox_helper import crear_combobox_etiquetas
from helpers.context_menu_helper import ContextMenuHelper
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from utils.tramo_utils import calcular_tramo_para_defecto

class TreeViewManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_combobox = None
        self.etiquetas_originales = {}
        self.tramos_info = []  #información de tramos
        
    def setup_treeview(self, parent_frame):
        columns = ("ID", "Nombre", "Alto[cm]", "Largo[cm]", "Distancia[m]", "Etiqueta", "Predicción", "Path", "Tramo")
        self.main_window.tree = ttk.Treeview(parent_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.main_window.tree.heading(col, text=col)
            if col == "Path" or col == "Tramo":
                self.main_window.tree.column(col, width=0, stretch=False)
            elif col in ("Alto[cm]", "Largo[cm]", "Distancia[m]"):
                self.main_window.tree.column(col, width=90, anchor="center")
            else:
                self.main_window.tree.column(col, width=70, anchor="center")
                
        self.main_window.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.main_window.tree.yview)
        self.main_window.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill="y")
        
        self.main_window.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
        self.main_window.context_menu_helper = ContextMenuHelper(
            self.main_window,
            self.main_window.tree,
            lambda: self.main_window.tree["columns"],
            self.eliminar_fila_por_id
        )
        
    def obtener_info_tramos(self, nombre_maquina):
        """Obtiene la información de los tramos desde la base de datos"""
        try:
            # Obtener ID de la máquina
            id_maquina = self.main_window.maquina_service.obtener_id_maquina_por_nombre(nombre_maquina)
            if not id_maquina:
                return []
            
            # Obtener tramos de la máquina
            tramos = self.main_window.maquina_service.obtener_tramos_por_maquina(id_maquina)
            
            # Convertir a formato esperado
            tramos_info = []
            for tramo in tramos:
                tramos_info.append({
                    'numero': tramo.numero_tramo,
                    'largo': tramo.largo_tramo or 0  # Usar 0 si es None
                })
            
            # Ordenar por número de tramo
            tramos_info.sort(key=lambda x: x['numero'])
            return tramos_info
            
        except Exception as e:
            print(f"Error obteniendo información de tramos: {e}")
            return []
        
    def on_item_select(self, event):
        selected_item = self.main_window.tree.selection()
        if not selected_item:
            return
            
        item_id = selected_item[0]
        values = self.main_window.tree.item(item_id, "values")
        
        if len(values) < 8:
            return
            
        defect_id = values[0]
        image_path = values[7]
        
        self.main_window.interactive_canvas.load_image_with_defects(image_path, [])
        
        tags = self.main_window.tree.item(item_id, "tags") or ()
        if tags and tags[0].startswith("coords_"):
            try:
                _, x1, y1, x2, y2 = tags[0].split("_")
                self.main_window.interactive_canvas.draw_existing_defects(
                    float(x1), float(y1), float(x2), float(y2),
                    "lime green", values[1]
                )
            except Exception as e:
                print(f"Error dibujando: {e}")
                
        self._actualizar_kilometros(item_id, values, image_path)
        self._mostrar_combobox_etiquetas(item_id, values, defect_id)
        
    def _actualizar_kilometros(self, item_id, values, image_path):
        try:
            if hasattr(self.main_window, 'imagenes_completas') and hasattr(self.main_window, 'largo_total_correa'):
                # Usar la utilidad centralizada
                tramo = calcular_tramo_para_defecto(
                    image_path, 
                    self.main_window.imagenes_completas,
                    self.main_window.largo_total_correa,
                    self.tramos_info,
                    getattr(self.main_window, 'secciones_correa', 5)
                )
                
                # Actualizar valores
                new_values = list(values)
                if len(new_values) > 8:  # Si existe columna Tramo
                    new_values[8] = tramo
                self.main_window.tree.item(item_id, values=tuple(new_values))
                
        except Exception as e:
            print(f"Error actualizando kilómetros: {e}")
            
    def calcular_metros_con_tramos_reales(self, indice_imagen):
        """Calcula los metros usando las longitudes reales de los tramos"""
        if not self.tramos_info or not self.main_window.imagenes_completas:
            return 0
            
        total_imagenes = len(self.main_window.imagenes_completas)
        proporcion = indice_imagen / total_imagenes
        
        # Calcular metros acumulados hasta el tramo correspondiente
        metros_acumulados = 0
        metros_totales = self.main_window.largo_total_correa
        
        for tramo in self.tramos_info:
            proporcion_tramo = tramo['largo'] / metros_totales
            if proporcion <= (metros_acumulados + tramo['largo']) / metros_totales:
                # Esta imagen está en este tramo
                metros_en_tramo = (proporcion - metros_acumulados/metros_totales) * metros_totales
                return metros_acumulados + metros_en_tramo
            metros_acumulados += tramo['largo']
        
        return metros_acumulados  # Último tramo
            
    def _mostrar_combobox_etiquetas(self, item_id, values, defect_id):
        if self.current_combobox:
            self.current_combobox.destroy()

        bbox = self.main_window.tree.bbox(item_id, 5)
        if bbox:
            x, y, width, height = bbox
            valor_actual = values[5] if len(values) > 5 else ""
            if valor_actual:
                valor_actual = valor_actual.upper()
                
            self.current_combobox = crear_combobox_etiquetas(
                self.main_window.tree, x, y, width, height, valor_actual,
                lambda e: self.save_label(defect_id, item_id)
            )
            
    def save_label(self, defect_id, item_id):
        new_label = self.current_combobox.get()
        new_label = new_label.upper() if new_label else new_label
        self.main_window.tree.set(item_id, "Etiqueta", new_label)
        self.current_combobox.destroy()
        self.current_combobox = None
        
    def eliminar_fila_por_id(self, item_id):
        if self.current_combobox:
            self.current_combobox.destroy()
            self.current_combobox = None
        self.main_window.tree.delete(item_id)
            

    def actualizar_treeview_con_defectos(self, resultado_df):
        """Actualiza el treeview con los defectos detectados"""
        try:
            self.main_window.tree.delete(*self.main_window.tree.get_children())
            self.etiquetas_originales = {}
            
            # Obtener información necesaria para cálculos
            imagenes_completas = getattr(self.main_window, 'imagenes_completas', [])
            largo_total_correa = getattr(self.main_window, 'largo_total_correa', None)
            secciones_correa = getattr(self.main_window, 'secciones_correa', 5)
            
            # ✅ OBTENER DESPLAZAMIENTO INICIAL - NUEVO
            desplazamiento_inicial = getattr(self.main_window, 'desplazamiento_inicial', 0)
            
            # ✅ LLAMAR A LA FUNCIÓN ACTUALIZADA CON DESPLAZAMIENTO
            from helpers.treeview_helper import insertar_defectos_en_treeview
            
            insertar_defectos_en_treeview(
                self.main_window.tree, 
                resultado_df, 
                "", 
                self.etiquetas_originales,
                self.main_window.pixeles_por_metro,
                largo_total_correa,
                imagenes_completas,
                secciones_correa,
                tramos_info=self.tramos_info,
                desplazamiento_inicial=desplazamiento_inicial  # ✅ NUEVO PARÁMETRO
            )
            
            ajustar_ancho_columnas(self.main_window.tree)
            
        except Exception as e:
            print(f"Error actualizando treeview: {e}")
            messagebox.showwarning("Advertencia", 
                                "Se completó el procesamiento pero hubo problemas mostrando los resultados.")