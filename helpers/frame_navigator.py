import tkinter as tk

class FrameNavigator:
    def __init__(self, canvas_widget, root, delay=1000):
        self.canvas_widget = canvas_widget  # instancia de InteractiveImageCanvas
        self.root = root
        self.delay = delay  # milisegundos
        self.playing = False

    def play(self):
        if not self.playing:
            self.playing = True
            self._loop()

    def pause(self):
        self.playing = False

    def _loop(self):
        if self.playing:
            self.next()  # Esto llama a next_image() en InteractiveImageCanvas
            self.root.after(self.delay, self._loop)

    def next(self):
        if self.canvas_widget.next_image():  # Solo si hubo un cambio real
            # Actualizar kilómetros usando navigation_manager si existe
            if hasattr(self.root, 'navigation_manager'):
                self.root.navigation_manager.actualizar_kilometro()
            elif hasattr(self.root, 'actualizar_kilometro'):
                # Mantener compatibilidad con versiones anteriores
                self.root.actualizar_kilometro()

    def previous(self):
        if self.canvas_widget.prev_image():  # Solo si hubo un cambio real
            # Actualizar kilómetros usando navigation_manager si existe
            if hasattr(self.root, 'navigation_manager'):
                self.root.navigation_manager.actualizar_kilometro()
            elif hasattr(self.root, 'actualizar_kilometro'):
                # Mantener compatibilidad con versiones anteriores
                self.root.actualizar_kilometro()

    def reset(self, nuevas_imagenes):
        self.image_paths = nuevas_imagenes
        self.current_index = 0
        self.canvas_widget.set_image_list(nuevas_imagenes)