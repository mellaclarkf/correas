import tkinter as tk
from tkinter import ttk
from helpers.correa_helper import CorreaCanvasHelper
from helpers.image_helper import InteractiveImageCanvas
from helpers.frame_navigator import FrameNavigator

class UIComponents:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def setup_main_frame(self):
        self.main_window.main_frame = tk.Frame(self.main_window)
        self.main_window.main_frame.pack(fill=tk.BOTH, expand=True)
        
    def setup_button_frame(self):
        button_frame = tk.Frame(self.main_window.main_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        load_video_button = ttk.Button(button_frame, text="📂 Cargar Video", 
                                    command=self.main_window.video_processor.cargar_video)
        load_video_button.pack(side=tk.LEFT, padx=10)
        
        boton_recargar = ttk.Button(button_frame, text="🔄 Re-Entrenar", 
                                command=self.main_window.event_handlers.recargar_cambios)
        boton_recargar.pack(side=tk.LEFT, padx=10)
        
        self.main_window.btn_informe = ttk.Button(button_frame, text="📊 Generar Informe", 
                                                command=self.main_window.event_handlers.mostrar_reporte)
        self.main_window.btn_informe.pack(side=tk.LEFT, padx=10)
        
        # Label de estado - CREAR SI NO EXISTE
        if not hasattr(self.main_window, 'status_label') or self.main_window.status_label is None:
            self.main_window.status_label = tk.Label(button_frame, text="Listo", fg="green")
            self.main_window.status_label.pack(side=tk.LEFT, padx=20)
        
        # Label para fecha - CREAR SI NO EXISTE
        if not hasattr(self.main_window, 'fecha_label') or self.main_window.fecha_label is None:
            self.main_window.fecha_label = tk.Label(button_frame, text="Fecha: No seleccionada")
            self.main_window.fecha_label.pack(side=tk.LEFT, padx=5)
        
        # Label para máquina - CREAR SI NO EXISTE
        if not hasattr(self.main_window, 'maquina_label') or self.main_window.maquina_label is None:
            self.main_window.maquina_label = tk.Label(button_frame, text="Máquina: No seleccionada")
            self.main_window.maquina_label.pack(side=tk.LEFT, padx=5)

        # Label para accuracy del modelo
        if not hasattr(self.main_window, 'accuracy_label') or self.main_window.accuracy_label is None:
            self.main_window.accuracy_label = tk.Label(
                button_frame, 
                text="Accuracy: Sin datos aún",
                fg="blue",
                font=("Arial", 9, "bold")
            )
            self.main_window.accuracy_label.pack(side=tk.LEFT, padx=10)
        
        # Actualizar el accuracy al iniciar
        self.actualizar_accuracy_label()            

    # actualizar_accuracy_label
    def actualizar_accuracy_label(self):
        """Actualiza el label con el accuracy del MEJOR modelo"""
        from services.modelo_service import ModeloService
        modelo_service = ModeloService(self.main_window.db_session)
        info_accuracy = modelo_service.obtener_accuracy_mejor_modelo()
        
        self.main_window.accuracy_label.config(text=f"Mejor Accuracy: {info_accuracy['mensaje']}")
        
        # Opcional: cambiar color según el valor de accuracy
        if info_accuracy['accuracy'] is not None:
            if info_accuracy['accuracy'] >= 90:
                self.main_window.accuracy_label.config(fg="green")
            elif info_accuracy['accuracy'] >= 70:
                self.main_window.accuracy_label.config(fg="orange")
            else:
                self.main_window.accuracy_label.config(fg="red")

    def setup_content_frame(self):
        content_frame = tk.Frame(self.main_window.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        table_frame = tk.Frame(content_frame)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        self.main_window.treeview_manager.setup_treeview(table_frame)
        
        canvas_frame = tk.Frame(content_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.main_window.correa_helper = CorreaCanvasHelper(
            canvas_frame, 
            self.main_window.secciones_correa or 5, 
            on_tramo_selected=self.main_window.navigation_manager.tramo_seleccionado
        )
        self.main_window.correa_canvas = self.main_window.correa_helper.get_canvas()
        self.main_window.correa_canvas.pack(pady=5)
        
        navigator_button_frame = tk.Frame(canvas_frame)
        navigator_button_frame.pack(pady=5)
        
        self.main_window.interactive_canvas = InteractiveImageCanvas(
            canvas_frame, 
            self.main_window.controller, 
            self.main_window.tree
        )
        self.main_window.interactive_canvas.parent_window = self.main_window
        
        self.main_window.navigator = FrameNavigator(
            self.main_window.interactive_canvas, 
            self.main_window
        )
        
        self.main_window.navigation_manager.setup_navigation_buttons(navigator_button_frame)
        
    def setup_menu_bar(self):
        menubar = tk.Menu(self.main_window)
        self.main_window.config(menu=menubar)
        
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opciones", menu=options_menu)
        options_menu.add_command(label="Configuración...", 
                                command=self.main_window.event_handlers.open_settings_window)
        options_menu.add_separator()
        options_menu.add_command(label="Salir", command=self.main_window.master.quit)