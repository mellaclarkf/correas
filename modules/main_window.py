import tkinter as tk
from tkinter import ttk
import os

# Importaciones que no causan circularidad
from helpers.correa_helper import CorreaCanvasHelper
from helpers.image_helper import InteractiveImageCanvas
from helpers.frame_navigator import FrameNavigator
from helpers.context_menu_helper import ContextMenuHelper
from helpers.loading_indicator import LoadingWindow
from views.date_popup import DatePopup
from views.settings_window import SettingsWindow
from views.ReportWindow import ReportWindow
from services.maquina_service import MaquinaService

class MainWindow(tk.Toplevel):
    def __init__(self, parent_root, controller):
        super().__init__(parent_root)
        self.controller = controller
        self.title("Defectos en Correas - Versión Interactiva")
        self.geometry("1400x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing_main_window)
        
        # Inicializar componentes
        self.ui_components = None
        self.event_handlers = None
        self.video_processor = None
        self.treeview_manager = None
        self.navigation_manager = None
        
        # Variables de estado - INICIALIZAR TODAS AQUÍ
        self.tree = None
        self.interactive_canvas = None
        self.current_combobox = None
        self.etiquetas_originales = {}
        self.current_defects_data = []  
        self.video_path = ""
        self.context_menu_helper = None
        self.fecha_seleccionada = None
        self.secciones_correa = None
        self.largo_total_correa = None
        self.pixeles_por_metro = 1000
        self.loading_window = None
        self.maquina_seleccionada = None
        self.imagenes_completas = []  # listado de imagenes cargadas
        
        # INICIALIZAR LOS LABELS QUE ESTÁN FALTANDO
        self.fecha_label = None
        self.maquina_label = None
        self.status_label = None
        self.btn_informe = None
        self.metadata_video = None
        
        # Inicializar servicio de máquinas
        self.db_session = controller.db_session
        self.maquina_service = MaquinaService(self.db_session)

        # Configurar UI
        self.setup_ui()
        
    def setup_ui(self):
        # Importaciones diferidas para evitar circularidad
        from modules.ui_components import UIComponents
        from modules.event_handlers import EventHandlers
        from modules.video_processor import VideoProcessor
        from modules.treeview_manager import TreeViewManager
        from modules.navigation_manager import NavigationManager
        
        # Inicializar componentes
        self.ui_components = UIComponents(self)
        self.event_handlers = EventHandlers(self)
        self.video_processor = VideoProcessor(self)
        self.treeview_manager = TreeViewManager(self)
        self.navigation_manager = NavigationManager(self)
        
        # Configurar UI
        self.ui_components.setup_main_frame()
        self.ui_components.setup_button_frame()
        self.ui_components.setup_content_frame()
        self.ui_components.setup_menu_bar()
        
    def on_closing_main_window(self):
        # Usar el manejador de eventos
        if hasattr(self, 'event_handlers') and self.event_handlers:
            self.event_handlers.on_closing_main_window()
        else:
            # Fallback si event_handlers no está disponible
            from tkinter import messagebox
            if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
                # Cerrar la sesión de base de datos
                if hasattr(self, 'db_session'):
                    try:
                        self.db_session.close()
                    except:
                        pass
                self.destroy()
                self.master.destroy()
    
    def show_loading(self, message="Procesando..."):
        """Muestra la ventana de carga"""
        if self.loading_window and hasattr(self.loading_window, 'window_exists') and self.loading_window.window_exists():
            self.loading_window.hide()
            
        from helpers.loading_indicator import LoadingWindow
        self.loading_window = LoadingWindow(self, message)
        self.loading_window.show()

    def hide_loading(self):
        """Oculta la ventana de carga"""
        if self.loading_window:
            self.loading_window.hide()
            self.loading_window = None

    def update_loading_message(self, message):
        """Actualiza el mensaje de la ventana de carga"""
        if self.loading_window and hasattr(self.loading_window, 'update_message'):
            self.loading_window.update_message(message)

    def actualizar_accuracy_display(self):
        """Actualiza el display de accuracy en la UI"""
        if hasattr(self, 'ui_components') and self.ui_components:
            self.ui_components.actualizar_accuracy_label()            