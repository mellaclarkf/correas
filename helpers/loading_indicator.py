import tkinter as tk
from tkinter import ttk
import threading
import time

class LoadingWindow:
    def __init__(self, parent, message="Procesando..."):
        self.parent = parent
        self.message = message
        self.window = None
        self.progress_bar = None
        self.label = None
        self.is_visible = False
        self.stop_animation = False
        
    def show(self):
        """Muestra la ventana de carga con barra de progreso"""
        if self.is_visible and self.window:
            return
            
        self.stop_animation = False
        self.window = tk.Toplevel(self.parent)
        self.window.title("Procesando")
        self.window.geometry("300x100")
        self.window.resizable(False, False)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Centrar la ventana
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 300) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 100) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Label con el mensaje
        self.label = tk.Label(self.window, text=self.message, pady=10)
        self.label.pack()
        
        # Barra de progreso indeterminada
        self.progress_bar = ttk.Progressbar(
            self.window, 
            mode='indeterminate', 
            length=280
        )
        self.progress_bar.pack(pady=10, padx=10)
        self.progress_bar.start(10)
        
        self.is_visible = True
        
        # Iniciar animación de mensajes en un hilo
        self.animation_thread = threading.Thread(target=self._animate_messages, daemon=True)
        self.animation_thread.start()
        
    def _animate_messages(self):
        """Animación de mensajes en un hilo separado"""
        messages = [
            "Extrayendo frames del video...",
            "Procesando con modelo de IA...",
            "Analizando posibles defectos...",
            "Finalizando procesamiento..."
        ]
        
        current_index = 0
        while self.is_visible and not self.stop_animation:
            # Actualizar mensaje en el hilo principal de Tkinter
            if self.window and self.is_visible:
                self.parent.after(0, self._update_message, messages[current_index])
            
            current_index = (current_index + 1) % len(messages)
            time.sleep(2)  # Cambiar mensaje cada 2 segundos
    
    def _update_message(self, message):
        """Actualizar mensaje de forma segura desde el hilo principal"""
        if self.label and self.is_visible and self.window:
            self.label.config(text=message)
            
    def update_message(self, new_message):
        """Actualiza el mensaje de la barra de progreso"""
        if self.is_visible and self.label and self.window:
            self.label.config(text=new_message)
            
    def hide(self):
        """Oculta y destruye la ventana de carga"""
        self.stop_animation = True
        self.is_visible = False
        
        if self.window:
            try:
                if self.progress_bar:
                    self.progress_bar.stop()
                self.window.grab_release()
                self.window.destroy()
            except:
                pass
            finally:
                self.window = None
                self.progress_bar = None
                self.label = None
        
    def set_progress(self, value, maximum=100):
        """Establece el progreso específico"""
        if self.is_visible and self.progress_bar and self.window:
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate', maximum=maximum, value=value)
            
    def set_indeterminate(self):
        """Vuelve al modo indeterminado"""
        if self.is_visible and self.progress_bar and self.window:
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start(10)
            
    def window_exists(self):
        """Verifica si la ventana todavía existe"""
        return self.is_visible and self.window is not None