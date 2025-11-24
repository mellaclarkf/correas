#############################################################
#  Clase para manejar las imagenes en canvas
#############################################################  
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import pandas as pd

class InteractiveImageCanvas:
    def __init__(self, parent_frame, controller, tree_widget):
        self.parent_frame = parent_frame #frame padre pasado por parámetro
        self.controller = controller     # Controlador Main_Controller
        self.tree_widget = tree_widget   # Treview pasado por parametro
        self.canvas = None               # Canvas de la Imagen
        self.current_image_path = None   # Path de la imagen mostrada al seleccionar treeview
        self.current_defects = []        # Almacena la informacion del defecto(s)
        self.pil_image = None            # Variable para manejar Imagen
        self.display_image = None        # Maneja imagen con defectos dibujados
        self.image_paths = []            # Ruta para recorrer las imagenes
        self.current_index = 0           # Contador del recorrido de las imagenes
        
        # Variables para dibujo
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.drawing_mode = False
        
        # Clases de defectos disponibles
        self.defect_classes = ["CORTES", "CRISTALIZADO", "DESGARROS", "DESGASTE", "DESPRENDIMIENTO","EMPALME","REPARACIONES"]
        self.setup_canvas()
        
    def setup_canvas(self):
        """Configura el canvas interactivo"""
        # Si ya hay canvas, se destruye
        if hasattr(self, 'canvas_container'):
            self.canvas_container.destroy()

        # Contenedor exclusivo para canvas
        self.canvas_container = tk.Frame(self.parent_frame)
        self.canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas
        self.canvas = tk.Canvas(self.canvas_container, bg='white', cursor='cross')
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        # Bindings para interacciones
        self.canvas.bind("<ButtonPress-1>", self.start_pan)      # Pan (arrastre)
        self.canvas.bind("<B1-Motion>", self.do_pan)             # Pan (arrastre)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)     # Zoom con scroll

        self.canvas.bind("<Button-3>", self.start_draw)          # Dibujo de defecto (click derecho)
        self.canvas.bind("<B3-Motion>", self.draw_rect)          # Dibujo de defecto (click derecho)
        self.canvas.bind("<ButtonRelease-3>", self.finish_draw)  # Dibujo de defecto (click derecho)

        self.canvas.bind("<Double-Button-1>", self.on_double_click)  # Re-etiquetado con doble click(no funcionando)

    # Carga una imagen y genera una imagen redimensionada donde dibuja los defectos existentes (no en disco)        
    def load_image_with_defects(self, image_path, defects_data=None):
        try:
            self.current_image_path = image_path
            self.current_defects = defects_data if defects_data else []
            
            # Cargar imagen
            #self.pil_image = Image.open(image_path)
            self.pil_image_original = Image.open(image_path)  # imagen sin escalar
            self.original_width, self.original_height = self.pil_image_original.size #guardo tamaño original

            self.pil_image = self.pil_image_original.copy()
            
            # Redimensionar si es muy grande
            max_size = (800, 600)
            self.pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Crear imagen de visualización con defectos dibujados
            self.display_image = self.pil_image.copy()
            #self.draw_existing_defects()
            
            # Mostrar en canvas
            self.tk_image = ImageTk.PhotoImage(self.display_image)
            self.canvas.config(width=self.display_image.width, height=self.display_image.height)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self.show_error_message()
            
    #"""Dibuja un defecto en la imagen escalada"""
    def draw_existing_defects(self, x1, y1, x2, y2, color="green", etiqueta=None):

        #draw = ImageDraw.Draw(self.display_image)
        try:
            scale_x = self.display_image.width / self.original_width
            scale_y = self.display_image.height / self.original_height

            # Ajustar coordenadas a escala del canvas
            x1_scaled = x1 * scale_x
            y1_scaled = y1 * scale_y
            x2_scaled = x2 * scale_x
            y2_scaled = y2 * scale_y

            # Dibujar rectángulo en canvas
            self.canvas.create_rectangle(
                x1_scaled, y1_scaled, x2_scaled, y2_scaled, outline=color, width=3
            )

            # Dibujar etiqueta si hay
            if etiqueta:
                self.canvas.create_text(
                    x1_scaled + 5, y1_scaled - 15, text=str(etiqueta), fill=color, anchor="nw"
                )
        except (ValueError, TypeError) as e:
                print(f"Error dibujando defecto: {e}")

    #Para que boton derecho despliegue un zoom(no implementado)       
    def on_single_click(self, event):
        defect = self.get_defect_at_position(event.x, event.y)
        if defect:
            self.zoom_to_defect(defect)
        # """Maneja click simple para mostrar zoom del defecto"""
        # defect = self.get_defect_at_position(event.x, event.y)
        # if defect:
        #     self.show_defect_zoom(defect, event.x, event.y)
            
    #Para doble clique re-etiquete un defecto(no implementado)
    def on_double_click(self, event):
        """Maneja doble click para re-etiquetar defecto"""
        defect = self.get_defect_at_position(event.x, event.y)
        if defect:
            self.show_relabel_dialog(defect)

    #""" Maneja el zoom de la rueda"""
    def on_mousewheel(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_image(factor)

    #Arraste de foto
    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    #Soltado de foto
    def do_pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    #zoom de la rueda en imagen implementación
    def zoom_image(self, factor):
        if self.display_image is None:
            return

        new_width = int(self.display_image.width * factor)
        new_height = int(self.display_image.height * factor)

        if new_width < 100 or new_width > 5000:
            return

        resized = self.pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.display_image = resized.copy()
        #self.draw_existing_defects()
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        # Actualizar scrollregion
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    #zoom al defecto, viene de click derecho(no implementado)
    def zoom_to_defect(self, defect):
        try:
            x1 = int(defect.get('eje_x', 0))
            y1 = int(defect.get('eje_y', 0))
            x2 = int(defect.get('eje_x2', x1 + 50))
            y2 = int(defect.get('eje_y2', y1 + 50))

            cropped = self.pil_image.crop((x1, y1, x2, y2))
            cropped = cropped.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), Image.Resampling.LANCZOS)

            self.display_image = cropped
            self.tk_image = ImageTk.PhotoImage(self.display_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        except Exception as e:
            print(f"Error haciendo zoom en defecto: {e}")

    #"""Encuentra el defecto en la posición dada""" (no implementado, viene de zoom para click)
    def get_defect_at_position(self, x, y):
        """Encuentra el defecto en la posición dada"""
        for defect in self.current_defects:
            try:
                x1 = int(defect.get('eje_x', 0))
                y1 = int(defect.get('eje_y', 0))
                x2 = int(defect.get('eje_x2', x1 + 50))
                y2 = int(defect.get('eje_y2', y1 + 50))
                
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return defect
            except (ValueError, TypeError):
                continue
        return None
        
    #"""Muestra zoom del defecto seleccionado"""(no implementado)
    def show_defect_zoom(self, defect, click_x, click_y):
        try:
            x1 = int(defect.get('eje_x', 0))
            y1 = int(defect.get('eje_y', 0))
            x2 = int(defect.get('eje_x2', x1 + 50))
            y2 = int(defect.get('eje_y2', y1 + 50))
            
            # Recortar área del defecto
            cropped = self.pil_image.crop((x1, y1, x2, y2))
            cropped = cropped.resize((300, 300), Image.Resampling.LANCZOS)
            
            # Crear ventana de zoom
            zoom_window = tk.Toplevel(self.canvas)
            zoom_window.title("Zoom del Defecto")
            zoom_window.geometry("320x350")
            
            # Canvas para mostrar zoom
            zoom_canvas = tk.Canvas(zoom_window, width=300, height=300)
            zoom_canvas.pack(pady=10)
            
            zoom_img = ImageTk.PhotoImage(cropped)
            zoom_canvas.create_image(0, 0, anchor="nw", image=zoom_img)
            zoom_canvas.image = zoom_img  # Mantener referencia
            
            # Información del defecto
            info_frame = tk.Frame(zoom_window)
            info_frame.pack(pady=5)
            
            tk.Label(info_frame, text=f"ID: {defect.get('id', 'N/A')}").pack()
            tk.Label(info_frame, text=f"Etiqueta: {defect.get('etiqueta', 'Sin etiqueta')}").pack()
            tk.Label(info_frame, text=f"Predicción: {defect.get('prediccion', 'N/A')}").pack()
            
        except Exception as e:
            print(f"Error mostrando zoom: {e}")
            
    #"""Muestra diálogo para re-etiquetar defecto""" (no Implementado)
    def show_relabel_dialog(self, defect):        
        relabel_window = tk.Toplevel(self.canvas)
        relabel_window.title("Re-etiquetar Defecto")
        relabel_window.geometry("250x300")
        relabel_window.grab_set()  # Modal
        
        tk.Label(relabel_window, text="Selecciona nueva etiqueta:", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Mostrar etiqueta actual
        current_label = defect.get('etiqueta', 'Sin etiqueta')
        tk.Label(relabel_window, text=f"Etiqueta actual: {current_label}", 
                fg="blue").pack(pady=5)
        
        def actualizar_etiqueta(nueva_etiqueta):
            try:
                # Actualizar defecto en memoria
                defect['etiqueta'] = nueva_etiqueta
                
                # Actualizar en TreeView
                self.update_treeview_defect(defect, nueva_etiqueta)
                
                # Redibujar imagen
                self.display_image = self.pil_image.copy()
                #self.draw_existing_defects()
                self.tk_image = ImageTk.PhotoImage(self.display_image)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
                
                relabel_window.destroy()
                messagebox.showinfo("Éxito", f"Defecto re-etiquetado como: {nueva_etiqueta}")
                
            except Exception as e:
                print(f"Error actualizando etiqueta: {e}")
                messagebox.showerror("Error", "No se pudo actualizar la etiqueta")
        
        # Botones para cada clase
        for clase in self.defect_classes:
            btn = tk.Button(relabel_window, text=clase, width=20,
                          command=lambda c=clase: actualizar_etiqueta(c))
            btn.pack(pady=2)
            
        # Botón cancelar
        tk.Button(relabel_window, text="❌ Cancelar", fg="red",
                 command=relabel_window.destroy).pack(pady=10)
                 
    # se supone agrega valor a treeview (no implementado)                 
    def update_treeview_defect(self, defect, nueva_etiqueta):
        """Actualiza el defecto en el TreeView"""
        defect_id = defect.get('id')
        if not defect_id:
            return
            
        # Buscar el item en el TreeView
        for item_id in self.tree_widget.get_children():
            values = self.tree_widget.item(item_id)["values"]
            if str(values[0]) == str(defect_id):
                # Actualizar la columna de etiqueta (índice 7)
                new_values = list(values)
                new_values[7] = nueva_etiqueta
                self.tree_widget.item(item_id, values=new_values)
                break
                
    #"""Inicia el dibujo de un nuevo rectángulo"""                
    def start_draw(self, event):
        self.start_x = self.canvas.canvasx(event.x)#self.start_x, self.start_y = event.x, event.y
        self.start_y = self.canvas.canvasy(event.y)

        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline="red", width=2, tags="new_defect"
        )
        self.drawing_mode = True
        
    #"""Actualiza el rectángulo mientras se dibuja"""        
    def draw_rect(self, event):
        if self.rect_id and self.drawing_mode:
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, current_x, current_y)

    #"""Finaliza el dibujo y muestra diálogo de clasificación"""   
    def finish_draw(self, event):
        if not self.drawing_mode or not self.rect_id:
            return
        
        # Obtener coordenadas finales
        x1, y1, x2, y2 = self.canvas.coords(self.rect_id)
        
        # Validar tamaño mínimo
        if abs(x2 - x1) < 20 or abs(y2 - y1) < 20:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            self.drawing_mode = False
            return
            
        # Normalizar coordenadas en canvas
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Escalar de canvas a imagen original
        scale_x = self.original_width / self.display_image.width
        scale_y = self.original_height / self.display_image.height

        x1_original = int(x1 * scale_x)
        y1_original = int(y1 * scale_y)
        x2_original = int(x2 * scale_x)
        y2_original = int(y2 * scale_y)

        # Guardar las coordenadas como atributos para usarlas en show_classification_dialog
        self.last_drawn_coords = (x1_original, y1_original, x2_original, y2_original)
        self.show_classification_dialog()
        
        #"""Muestra diálogo para clasificar nuevo defecto"""
    def show_classification_dialog(self):
        # Verificar que tenemos coordenadas
        if not hasattr(self, 'last_drawn_coords'):
            return
            
        x1_original, y1_original, x2_original, y2_original = self.last_drawn_coords
        
        class_window = tk.Toplevel(self.canvas)
        class_window.title("Clasificar Nuevo Defecto")
        class_window.geometry("300x400")
        class_window.grab_set()  # Modal
        
        tk.Label(class_window, text="Selecciona clase del defecto:", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # Mostrar preview del área seleccionada
        try:
            preview_area = self.pil_image_original.crop((x1_original, y1_original, x2_original, y2_original))
            preview_area = preview_area.resize((150, 150), Image.Resampling.LANCZOS)
            preview_img = ImageTk.PhotoImage(preview_area)
            
            preview_label = tk.Label(class_window, image=preview_img)
            preview_label.image = preview_img  # Mantener referencia
            preview_label.pack(pady=10)
        except Exception as e:
            print(f"Error mostrando preview: {e}")
        
        tk.Label(class_window, text=f"Coordenadas: ({x1_original}, {y1_original}) - ({x2_original}, {y2_original})").pack(pady=5)
        
        def guardar_nuevo_defecto(clase_defecto):
            try:
                # Crear nuevo defecto
                nuevo_defecto = self.create_new_defect(x1_original, y1_original, x2_original, y2_original, clase_defecto)
                
                if messagebox.askyesno("Confirmar", f"¿Guardar nuevo defecto como '{clase_defecto}'?"):
                                        
                    # Agregar a la lista de defectos actuales
                    self.current_defects.append(nuevo_defecto)
                    
                    # Agregar al TreeView
                    self.add_defect_to_treeview(nuevo_defecto)
                    
                    # Redibujar imagen
                    self.display_image = self.pil_image.copy()
                    self.tk_image = ImageTk.PhotoImage(self.display_image)
                    self.canvas.delete("all")
                    self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
                    
                    messagebox.showinfo("Éxito", "Nuevo defecto guardado correctamente")
                else:
                    # Cancelar - eliminar rectángulo
                    self.canvas.delete(self.rect_id)
                    
            except Exception as e:
                print(f"Error guardando defecto: {e}")
                messagebox.showerror("Error", "No se pudo guardar el defecto")
            finally:
                class_window.destroy()
                self.rect_id = None
                self.drawing_mode = False
        
        def cancelar_defecto():
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            self.drawing_mode = False
            class_window.destroy()
        
        # Botones para cada clase
        for clase in self.defect_classes:
            btn = tk.Button(class_window, text=clase, width=20,
                          command=lambda c=clase: guardar_nuevo_defecto(c))
            btn.pack(pady=2)
            
        # Botón cancelar
        tk.Button(class_window, text="❌ Cancelar", fg="red",
                 command=cancelar_defecto).pack(pady=10)

    #"""Crea un nuevo objeto defecto"""                 
    def create_new_defect(self, x1, y1, x2, y2, etiqueta):
        import os
        import datetime
        import uuid
        nombre_archivo = os.path.basename(self.current_image_path)
        defect_id = f"manual_{uuid.uuid4().hex[:8]}"
        return {
            'id': defect_id,
            'name': nombre_archivo,
            'image_path': self.current_image_path,
            'eje_x': x1,
            'eje_y': y1,
            'eje_x2': x2,
            'eje_y2': y2,
            'etiqueta': etiqueta,
            'prediccion': etiqueta,  # Para defectos manuales, predicción = etiqueta
            'fecha_registro': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
                    
    # image_helper.py - en el método add_defect_to_treeview
    def add_defect_to_treeview(self, defecto):
        import os
        try:
            # Obtener información necesaria para cálculos
            pixeles_por_metro = getattr(self.controller, 'pixeles_por_metro', 1000)
            largo_total_correa = getattr(self.controller, 'largo_total_correa', None)
            imagenes_completas = getattr(self.controller, 'imagenes_completas', [])
            secciones_correa = getattr(self.controller, 'secciones_correa', 5)
            
            # Obtener información de tramos si está disponible
            tramos_info = None
            if hasattr(self.controller, 'treeview_manager') and hasattr(self.controller.treeview_manager, 'tramos_info'):
                tramos_info = self.controller.treeview_manager.tramos_info
            
            # Obtener desplazamiento inicial si está disponible
            desplazamiento_inicial = getattr(self.controller, 'desplazamiento_inicial', 0)
            
            # Calcular dimensiones en centímetros
            ancho_cm = (abs(defecto['eje_x2'] - defecto['eje_x']) / pixeles_por_metro) * 100
            alto_cm = (abs(defecto['eje_y2'] - defecto['eje_y']) / pixeles_por_metro) * 100
            
            # Calcular distancia (mismos cálculos que en treeview_helper)
            distancia_m = 0.0
            if largo_total_correa and imagenes_completas and defecto['image_path']:
                try:
                    imagen_actual = os.path.basename(defecto['image_path'])
                    indice = next((i for i, img in enumerate(imagenes_completas) 
                                if os.path.basename(img) == imagen_actual), 0)
                    # ✅ METROS DESDE INICIO CORREA (no desde inicio grabación)
                    distancia_m = desplazamiento_inicial + ((indice / len(imagenes_completas)) * largo_total_correa)
                except Exception as e:
                    print(f"Error calculando distancia: {e}")
            
            # ✅ Calcular tramo USANDO LA NUEVA FUNCIÓN CON DESPLAZAMIENTO
            from utils.tramo_utils import calcular_tramo_para_defecto
            
            tramo = calcular_tramo_para_defecto(
                imagen_path=defecto['image_path'],
                imagenes_completas=imagenes_completas,
                largo_total_correa=largo_total_correa,
                tramos_info=tramos_info,
                secciones_correa=secciones_correa,
                desplazamiento_inicial=desplazamiento_inicial
            )

            nombre_archivo = os.path.basename(defecto['image_path'])
            coords_tag = f"coords_{defecto['eje_x']}_{defecto['eje_y']}_{defecto['eje_x2']}_{defecto['eje_y2']}"
            
            # Insertar en treeview con el mismo formato
            self.tree_widget.insert("", "end", values=(
                defecto['id'],
                nombre_archivo,
                f"{ancho_cm:.3f}",      # Alto en cm
                f"{alto_cm:.3f}",       # Largo en cm  
                f"{distancia_m:.3f}",   # Distancia en metros (DESDE INICIO CORREA)
                defecto['etiqueta'],
                defecto['prediccion'],
                defecto['image_path'],
                tramo  # ✅ TRAMO CALCULADO CORRECTAMENTE
            ),
            tags=(coords_tag,))
            
            if hasattr(self.controller, 'treeview_manager'):
                self.controller.treeview_manager.etiquetas_originales[defecto['id']] = defecto['etiqueta']
                
        except Exception as e:
            print(f"Error agregando al TreeView: {e}")
            
    #"""Muestra mensaje de error cuando no se puede cargar la imagen"""
    def show_error_message(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            200, 150, text="Imagen no disponible", 
            fill="red", font=("Arial", 16)
        )

    #Implementacion de Play/pause << y >> para recorrer los frames
    def set_image_list(self, image_paths):
        self.image_paths = image_paths
        self.current_index = 0
        if image_paths:
            self.load_image_with_defects(image_paths[0])

    # muestra imagen para  Play/pause
    def show_image_by_index(self, index):
        if not self.image_paths or not (0 <= index < len(self.image_paths)):
            return
        self.current_index = index
        image_path = self.image_paths[index]
        self.load_image_with_defects(image_path)

    # muestra imagen para >>
    def next_image(self):
        """Muestra la siguiente imagen en la lista"""
        if not self.image_paths:
            return False
            
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.show_image_by_index(self.current_index)
            
            # Actualizar kilómetros usando navigation_manager si existe
            if hasattr(self.parent_window, 'navigation_manager'):
                self.parent_window.navigation_manager.actualizar_kilometro()
            elif hasattr(self.parent_window, 'actualizar_kilometro'):
                # Mantener compatibilidad con versiones anteriores
                self.parent_window.actualizar_kilometro()
                
            return True
        return False

    def prev_image(self):
        if self.image_paths and self.current_index > 0:
            self.current_index -= 1
            self.show_image_by_index(self.current_index)
            # Actualizar kilómetros usando navigation_manager si existe
            if hasattr(self.parent_window, 'navigation_manager'):
                self.parent_window.navigation_manager.actualizar_kilometro()
            elif hasattr(self.parent_window, 'actualizar_kilometro'):
                # Mantener compatibilidad con versiones anteriores
                self.parent_window.actualizar_kilometro()
            return True
        return False
            
    def _actualizar_archivo_etiqueta(self, defecto):
        """Actualiza el archivo de etiqueta para un defecto recién creado"""
        from utils.folder_dataset import DatasetFolderManager
        from pathlib import Path
        
        success = DatasetFolderManager.procesar_cambio_etiqueta(
            Path(defecto['image_path']),
            defecto['eje_x'], defecto['eje_y'], defecto['eje_x2'], defecto['eje_y2'],
            defecto['etiqueta']
        )
        
        if not success:
            print(f"Error actualizando archivo de etiqueta para {defecto['image_path']}")