import os
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

class NavigationManager:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def setup_navigation_buttons(self, parent_frame):
        self.main_window.btn_prev = ttk.Button(parent_frame, text="⏮", command=self.retroceder_foto)
        self.main_window.btn_play_pause = ttk.Button(parent_frame, text="▶", command=self.toggle_play_pause)
        self.main_window.btn_next = ttk.Button(parent_frame, text="⏭", command=self.avanzar_foto)
        self.main_window.label_kilometro = tk.Label(parent_frame, text=" 0.00 m")
        
        self.main_window.btn_prev.pack(side=tk.LEFT, padx=5)
        self.main_window.btn_play_pause.pack(side=tk.LEFT, padx=5)
        self.main_window.btn_next.pack(side=tk.LEFT, padx=5)
        self.main_window.label_kilometro.pack(side=tk.LEFT, padx=10)
        
        self.main_window.entry_metros = ttk.Entry(parent_frame, width=8)
        self.main_window.entry_metros.pack(side=tk.LEFT, padx=(5, 0))
        
        btn_ir_metros = ttk.Button(
            parent_frame,
            text="Ir",
            command=self.ir_a_metros,
            width=4
        )
        btn_ir_metros.pack(side=tk.LEFT, padx=(0, 5))
        
        self.main_window.btn_play_pause["state"] = "disabled"
        self.main_window.btn_prev["state"] = "disabled"
        self.main_window.btn_next["state"] = "disabled"
        
    def configurar_navegacion_video(self):
        image_paths = self.cargar_imagenes_desde_carpeta()
        self.main_window.imagenes_completas = image_paths # agrego listado de imagenes completo
        self.main_window.imagenes_actuales = self.main_window.imagenes_completas[:] #imagenes para trabajar y recorrer canvas por tramo
        self.main_window.interactive_canvas.set_image_list(image_paths)

        self.main_window.btn_play_pause["state"] = "normal"
        self.main_window.btn_prev["state"] = "normal"
        self.main_window.btn_next["state"] = "normal"
        self.main_window.btn_informe.state(["!disabled"])
        
    def cargar_imagenes_desde_carpeta(self):
        carpeta = os.path.join(os.getcwd(), "Imagenes")
        extensiones_validas = (".jpg", ".jpeg", ".png", ".bmp")

        image_paths = [
            os.path.join(carpeta, f)
            for f in os.listdir(carpeta)
            if f.lower().endswith(extensiones_validas)
        ]

        return sorted(image_paths)
        
    def toggle_play_pause(self):
        if self.main_window.navigator.playing:
            self.main_window.navigator.pause()
            self.main_window.btn_play_pause.config(text="▶")
            self.main_window.btn_prev["state"] = "normal"
            self.main_window.btn_next["state"] = "normal"
        else:
            self.main_window.navigator.play()
            self.main_window.btn_play_pause.config(text="⏸")
            self.main_window.btn_prev["state"] = "disabled"
            self.main_window.btn_next["state"] = "disabled"
            
    def tramo_seleccionado(self, index):
        if not hasattr(self.main_window, 'imagenes_completas') or not self.main_window.imagenes_completas:
            messagebox.showinfo("Sin imágenes", "Debes cargar un video antes de seleccionar un tramo.")
            return

        # Obtener información de tramos si está disponible
        tramos_info = getattr(self.main_window.treeview_manager, 'tramos_info', [])
        
        if index is None:
            self.main_window.imagenes_actuales = self.main_window.imagenes_completas[:]
            self.main_window.offset_tramo = 0
        elif tramos_info and len(tramos_info) > index:
            # Usar longitudes reales de tramos
            total_imagenes = len(self.main_window.imagenes_completas)
            metros_totales = self.main_window.largo_total_correa
            
            # Calcular metros acumulados hasta este tramo
            metros_acumulados = 0
            for i in range(index):
                if i < len(tramos_info):
                    metros_acumulados += tramos_info[i]['largo']
            
            # Calcular rango de imágenes para este tramo
            proporcion_inicio = metros_acumulados / metros_totales
            proporcion_fin = (metros_acumulados + tramos_info[index]['largo']) / metros_totales
            
            inicio_index = int(proporcion_inicio * total_imagenes)
            fin_index = int(proporcion_fin * total_imagenes)
            
            self.main_window.offset_tramo = inicio_index
            self.main_window.imagenes_actuales = self.main_window.imagenes_completas[inicio_index:fin_index]
        else:
            # Fallback: división uniforme
            total = len(self.main_window.imagenes_completas)
            tramos = self.main_window.correa_helper.tramos
            self.main_window.offset_tramo = index * (total // tramos)
            fin = self.main_window.offset_tramo + (total // tramos)
            self.main_window.imagenes_actuales = self.main_window.imagenes_completas[self.main_window.offset_tramo:fin]
        
        self.main_window.navigator.reset(self.main_window.imagenes_actuales)
        self.main_window.interactive_canvas.current_index = 0
        self.actualizar_kilometro()
        
    def actualizar_kilometro(self):
        if not hasattr(self.main_window, 'imagenes_completas') or not hasattr(self.main_window, 'largo_total_correa'):
            return
        
        total_imagenes = len(self.main_window.imagenes_completas)
        if total_imagenes == 0 or self.main_window.largo_total_correa <= 0:
            return

        # Obtener desplazamiento inicial (0 si no existe)
        desplazamiento = getattr(self.main_window, 'desplazamiento_inicial', 0)
        
        # Calcular metros ACUMULADOS desde inicio de correa
        indice_global = getattr(self.main_window, 'offset_tramo', 0) + self.main_window.interactive_canvas.current_index
        metros_desde_inicio_grabacion = (indice_global / total_imagenes) * self.main_window.largo_total_correa
        metros_totales = desplazamiento + metros_desde_inicio_grabacion
        
        # Mostrar con 2 decimales
        self.main_window.label_kilometro.config(text=f"{metros_totales:.2f} m")
        
        # Debug
        print(f"Índice Global: {indice_global}/{total_imagenes}, Metros desde inicio: {metros_totales:.2f}")
        
    def avanzar_foto(self):
        if not self.main_window.navigator.playing:
            self.main_window.navigator.next()
            self.actualizar_kilometro()

    def retroceder_foto(self):
        if not self.main_window.navigator.playing:
            self.main_window.navigator.previous()
            self.actualizar_kilometro()
            
    def ir_a_metros(self):
        if not hasattr(self.main_window, 'imagenes_completas') or not hasattr(self.main_window, 'largo_total_correa'):
            messagebox.showerror("Error", "Primero carga un video")
            return

        try:
            metros_ingresados = float(self.main_window.entry_metros.get())
        except ValueError:
            messagebox.showerror("Error", "Ingresa un valor numérico válido")
            return

        if hasattr(self.main_window, 'offset_tramo') and hasattr(self.main_window.correa_helper, 'selected_tramo') \
        and self.main_window.correa_helper.selected_tramo is not None:
            tramos = self.main_window.correa_helper.tramos
            largo_tramo = self.main_window.largo_total_correa / tramos
            inicio_tramo = self.main_window.correa_helper.selected_tramo * largo_tramo
            metros_absolutos = inicio_tramo + metros_ingresados
            metros_absolutos = min(inicio_tramo + largo_tramo, metros_absolutos)
        else:
            metros_absolutos = metros_ingresados

        if metros_absolutos < 0:
            messagebox.showwarning("Advertencia", "No se permiten valores negativos")
            return
        elif metros_absolutos > self.main_window.largo_total_correa:
            messagebox.showwarning("Advertencia", f"El valor máximo permitido es {self.main_window.largo_total_correa:.2f} metros")
            metros_absolutos = self.main_window.largo_total_correa

        total_imagenes = len(self.main_window.imagenes_completas)
        proporcion = metros_absolutos / self.main_window.largo_total_correa
        indice_global = round(proporcion * (total_imagenes - 1))
        
        if hasattr(self.main_window, 'offset_tramo'):
            indice_local = indice_global - self.main_window.offset_tramo
            self.main_window.interactive_canvas.current_index = max(0, min(indice_local, len(self.main_window.imagenes_actuales) - 1))
        else:
            self.main_window.interactive_canvas.current_index = indice_global
        
        self.main_window.interactive_canvas.show_image_by_index(self.main_window.interactive_canvas.current_index)
        self.actualizar_kilometro()
        self.main_window.entry_metros.delete(0, tk.END)

