import cv2
import os
import tkinter as tk
from tkinter import Toplevel, Canvas, Label, filedialog
from PIL import Image, ImageTk

class VideoPlayerWindow:
    def __init__(self, main_window, video_path=None):
        self.main_window = main_window
        self.video_path = video_path
        self.cap = None
        self.paused = True
        self.frame_step = 5
        self.marked_zones = []
        self.start_point = None
        self.end_point = None

        if not os.path.exists("capturas"):
            os.makedirs("capturas")

        self.window = Toplevel(main_window)
        self.window.title("Reproductor de Video")

        # Controles arriba
        self.frame_controles = tk.Frame(self.window)
        self.frame_controles.pack(pady=5)

        self.btn_cargar = tk.Button(self.frame_controles, text="Cargar Video", command=self.cargar_video)
        self.btn_cargar.pack(side="left", padx=5)

        self.btn_play = tk.Button(self.frame_controles, text="Play/Pause", command=self.toggle_play, state="disabled")
        self.btn_play.pack(side="left", padx=5)

        self.btn_atras = tk.Button(self.frame_controles, text="<<", command=self.retroceder, state="disabled")
        self.btn_atras.pack(side="left", padx=5)

        self.btn_adelante = tk.Button(self.frame_controles, text=">>", command=self.avanzar, state="disabled")
        self.btn_adelante.pack(side="left", padx=5)

        self.spinbox_frames = tk.Spinbox(self.frame_controles, from_=1, to=50, width=5)
        self.spinbox_frames.pack(side="left", padx=5)
        self.spinbox_frames.delete(0, "end")
        self.spinbox_frames.insert(0, str(self.frame_step))

        self.time_label = Label(self.frame_controles, text="0.00 s")
        self.time_label.pack(side="left", padx=5)

        self.canvas = Canvas(self.window, width=800, height=450, bg="black")
        self.canvas.pack()

        # Barra de progreso interactiva
        self.progress_canvas = Canvas(self.window, width=800, height=20, bg="lightgray")
        self.progress_canvas.pack()
        self.progress_canvas.bind("<Button-1>", self.ir_a_posicion)
        self.progress_canvas.bind("<B1-Motion>", self.ir_a_posicion)

        self.canvas.bind("<Button-1>", self.iniciar_recorte)
        self.canvas.bind("<B1-Motion>", self.actualizar_recorte)
        self.canvas.bind("<ButtonRelease-1>", self.finalizar_recorte)

        if self.video_path:
            self.cargar_video(ruta=self.video_path)

    def cargar_video(self, ruta=None):
        if not ruta:
            ruta = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.avi")])
        if ruta:
            self.video_path = ruta
            self.cap = cv2.VideoCapture(self.video_path)
            self.paused = True
            self.btn_play.config(state="normal")
            self.btn_atras.config(state="normal")
            self.btn_adelante.config(state="normal")
            self.mostrar_siguiente_frame()

    def reproducir_video(self):
        if self.cap and not self.paused:
            ret, frame = self.cap.read()
            if ret:
                self._mostrar_frame(frame)
                self.window.after(30, self.reproducir_video)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.reproducir_video()

    def toggle_play(self):
        if self.cap:
            self.paused = not self.paused
            if not self.paused:
                self.reproducir_video()

    def avanzar(self):
        if self.cap:
            pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            frames_a_mover = int(self.spinbox_frames.get())
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, pos + frames_a_mover)
            ret, frame = self.cap.read()
            if ret:
                self._mostrar_frame(frame)

    def retroceder(self):
        if self.cap:
            pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            frames_a_mover = int(self.spinbox_frames.get())
            nueva_pos = max(pos - frames_a_mover, 0)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, nueva_pos)
            ret, frame = self.cap.read()
            if ret:
                self._mostrar_frame(frame)

    def _mostrar_frame(self, frame):
        frame_resized = cv2.resize(frame, (800, 450))
        self.current_frame = frame_resized
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.imgtk = imgtk
        self.canvas.create_image(0, 0, anchor="nw", image=imgtk)

        self.actualizar_barra_progreso()

    def mostrar_siguiente_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self._mostrar_frame(frame)

    def actualizar_barra_progreso(self):
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

        self.progress_canvas.delete("all")
        if total_frames > 0:
            progress_width = int((frame_pos / total_frames) * 800)
            self.progress_canvas.create_rectangle(0, 0, progress_width, 20, fill="green")

        tiempo_actual = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        self.time_label.config(text=f"{tiempo_actual:.2f} s")

    def ir_a_posicion(self, event):
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        click_x = event.x
        pos_frame = int((click_x / 800) * total_frames)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame)
        ret, frame = self.cap.read()
        if ret:
            self._mostrar_frame(frame)

    def iniciar_recorte(self, event):
        if self.paused and hasattr(self, 'current_frame'):
            self.start_point = (event.x, event.y)

    def actualizar_recorte(self, event):
        if self.paused and self.start_point:
            self.end_point = (event.x, event.y)
            self._mostrar_frame(self.current_frame.copy())
            self.canvas.create_rectangle(self.start_point[0], self.start_point[1],
                                         self.end_point[0], self.end_point[1],
                                         outline='green', width=2)

    def finalizar_recorte(self, event):
        if self.paused and self.start_point and self.end_point:
            x0, y0 = self.start_point
            x1, y1 = self.end_point
            x_min, y_min = min(x0, x1), min(y0, y1)
            width = abs(x1 - x0)
            height = abs(y1 - y0)

            if width > 0 and height > 0:
                tiempo_actual = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                frame_actual = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

                # Guardar los datos temporales de este recorte
                self.recorte_pendiente = {
                    'x': x_min,
                    'y': y_min,
                    'width': width,
                    'height': height,
                    'time': tiempo_actual,
                    'frame_number': frame_actual,
                    'total_frames': total_frames
                }

                # Abrir ventana para seleccionar defecto
                self.mostrar_selector_defecto()

            self.start_point = None
            self.end_point = None

    def mostrar_selector_defecto(self):
        ventana = tk.Toplevel(self.window)
        ventana.title("Seleccionar Defecto")
        ventana.grab_set()  # Modal

        tk.Label(ventana, text="Selecciona tipo de defecto:").pack(pady=5)

        defecto_var = tk.StringVar(value="Desgaste")
        opciones = ["Desgaste", "Desprendimiento", "Rasgado", "Otro"]
        for opcion in opciones:
            tk.Radiobutton(ventana, text=opcion, variable=defecto_var, value=opcion).pack(anchor="w")

        def confirmar_guardado():
            self.guardar_recorte_confirmado(defecto_var.get())
            ventana.destroy()

        def cancelar():
            ventana.destroy()

        frame_botones = tk.Frame(ventana)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Guardar", command=confirmar_guardado).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Cancelar", command=cancelar).pack(side="left", padx=5)
            

    def guardar_recorte_confirmado(self, tipo_defecto):
        rec = self.recorte_pendiente

        # Dibujar rectángulo sobre frame completo
        frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        cv2.rectangle(frame_rgb, (rec['x'], rec['y']), (rec['x']+rec['width'], rec['y']+rec['height']), (0, 255, 0), 2)

        # Guardar imagen
        img_frame = Image.fromarray(frame_rgb)
        image_filename = f'capturas/captura_Manual_{len(self.marked_zones)+1}.png'
        img_frame.save(image_filename)

        # Guardar en lista interna
        registro = {
            'image_path': image_filename,
            'x': rec['x'],
            'y': rec['y'],
            'x2': rec['x']+rec['width'],
            'y2': rec['y']+rec['height'],
            'time': rec['time'],
            'frame_number': rec['frame_number'],
            'total_frames': rec['total_frames'],
            'defecto': tipo_defecto
        }
        self.marked_zones.append(registro)

        print(f"Guardado: {registro}")

        # Agregar al TreeView del MainWindow en vivo
        self.main_window.agregar_defecto_a_treeview(registro)



