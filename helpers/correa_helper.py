# correa_canvas_helper.py
import tkinter as tk

class CorreaCanvasHelper:
    """
    Dibuja una correa tipo óvalo con tramos (rodillos) en la parte superior e inferior.
    - direccion_derecha = True:
        Superior: 1 • 2 • 3 ...
        Inferior: ... N • ... (numeración inversa)
    - direccion_derecha = False (izquierda):
        Superior: N • ... • 3
        Inferior: 1 • 2 • ...
    """
    def __init__(self, parent, tramos=5, on_tramo_selected=None):
        self.tramos = tramos
        self.canvas = tk.Canvas(parent, width=600, height=100, bg="white",
                                highlightthickness=0, highlightbackground="black")
        self.on_tramo_selected = on_tramo_selected
        self.selected_tramo = None
        self.todos_seleccionado = False
        self.direccion_derecha = True  # por defecto
        self.radio_rodillo = 8

        self.rodillos_posiciones = []  # (tramo_id, cx, cy)

        self.canvas.bind("<Button-1>", self.handle_click)
        self.dibujar_correa()

    def dibujar_correa(self):
        self.canvas.delete("all")
        self.rodillos_posiciones = []

        ancho = int(self.canvas['width'])
        alto = int(self.canvas['height'])

        margen = 40
        separacion_vertical = 25

        # Estructura base (líneas y arcos)
        self.canvas.create_line(
            margen, 30,
            ancho - margen, 30,
            fill="gray", width=4
        )
        self.canvas.create_line(
            margen, alto - 30,
            ancho - margen, alto - 30,
            fill="gray", width=4
        )
        self.canvas.create_arc(
            margen - self.radio_rodillo - 8, 30,
            margen + self.radio_rodillo + 8, alto - 30,
            start=90, extent=180, style=tk.ARC, outline="gray", width=4
        )
        self.canvas.create_arc(
            ancho - margen - self.radio_rodillo - 8, 30,
            ancho - margen + self.radio_rodillo + 8, alto - 30,
            start=270, extent=180, style=tk.ARC, outline="gray", width=4
        )

        # Flecha dirección
        self.dibujar_flecha_direccion()

        # Cálculos de distribución
        tramos_superiores = (self.tramos + 1) // 2
        tramos_inferiores = self.tramos // 2

        # Evitar divisiones por cero
        divisor_sup = max(1, tramos_superiores - 1)
        step_sup = (ancho - 2 * margen) / divisor_sup

        # --- Tramos superiores ---
        for i in range(tramos_superiores):
            cx = margen + i * step_sup
            cy = alto // 2 - separacion_vertical

            if self.direccion_derecha:
                tramo_id = i
            else:
                tramo_id = self.tramos - i - 1  # invertido arriba

            color = "blue" if (self.todos_seleccionado or self.selected_tramo == tramo_id) else "black"

            self.canvas.create_oval(
                cx - self.radio_rodillo, cy - self.radio_rodillo,
                cx + self.radio_rodillo, cy + self.radio_rodillo,
                fill=color, outline="", tags=f"tramo_{tramo_id}"
            )
            self.canvas.create_text(
                cx, cy,
                text=str(tramo_id + 1),
                fill="white", font=("Arial", 8, "bold")
            )
            self.rodillos_posiciones.append((tramo_id, cx, cy))

        # --- Tramos inferiores ---
        if tramos_inferiores == tramos_superiores:
            # Caso par (p.ej., 6): distribuir uniformemente en todo el ancho (sin offset 0.5)
            divisor_inf = max(1, tramos_inferiores - 1)
            step_inf = (ancho - 2 * margen) / divisor_inf
            for j in range(tramos_inferiores):
                cx = margen + j * step_inf
                cy = alto // 2 + separacion_vertical

                if self.direccion_derecha:
                    tramo_id = self.tramos - j - 1
                else:
                    tramo_id = j

                color = "blue" if (self.todos_seleccionado or self.selected_tramo == tramo_id) else "black"

                self.canvas.create_oval(
                    cx - self.radio_rodillo, cy - self.radio_rodillo,
                    cx + self.radio_rodillo, cy + self.radio_rodillo,
                    fill=color, outline="", tags=f"tramo_{tramo_id}"
                )
                self.canvas.create_text(
                    cx, cy,
                    text=str(tramo_id + 1),
                    fill="white", font=("Arial", 8, "bold")
                )
                self.rodillos_posiciones.append((tramo_id, cx, cy))
        else:
            # Caso impar (p.ej., 5): centrados entre los superiores (offset 0.5 * step_sup)
            for j in range(tramos_inferiores):
                cx = margen + (j + 0.5) * step_sup
                cy = alto // 2 + separacion_vertical

                if self.direccion_derecha:
                    tramo_id = self.tramos - j - 1
                else:
                    tramo_id = j

                color = "blue" if (self.todos_seleccionado or self.selected_tramo == tramo_id) else "black"

                self.canvas.create_oval(
                    cx - self.radio_rodillo, cy - self.radio_rodillo,
                    cx + self.radio_rodillo, cy + self.radio_rodillo,
                    fill=color, outline="", tags=f"tramo_{tramo_id}"
                )
                self.canvas.create_text(
                    cx, cy,
                    text=str(tramo_id + 1),
                    fill="white", font=("Arial", 8, "bold")
                )
                self.rodillos_posiciones.append((tramo_id, cx, cy))

        # Botón "Ver Todos"
        self.canvas.create_oval(
            ancho - 25, 5,
            ancho - 5, 25,
            fill="blue", tags="ver_todos"
        )

        # Mostrar longitud en cada tramo si está disponible
        if hasattr(self, 'tramos_info') and self.tramos_info:
            for i, (tramo_id, cx, cy) in enumerate(self.rodillos_posiciones):
                if i < len(self.tramos_info):
                    longitud = self.tramos_info[i]['largo']
                    if longitud:
                        # Mostrar longitud debajo del rodillo
                        self.canvas.create_text(
                            cx, cy + 15,
                            text=f"{longitud}m",
                            fill="darkgreen",
                            font=("Arial", 7)
                        )

    def dibujar_flecha_direccion(self):
        """Dibuja una flecha pequeña en la esquina superior izquierda indicando la dirección."""
        x = 10
        y = 10
        tam = 25
        if self.direccion_derecha:
            # →
            self.canvas.create_line(x, y, x + tam, y, fill="blue", width=2, arrow=tk.LAST)
        else:
            # ←
            self.canvas.create_line(x + tam, y, x, y, fill="blue", width=2, arrow=tk.LAST)

    def actualizar_tramos(self, tramos):
        self.tramos = max(1, int(tramos))
        self.selected_tramo = None
        self.todos_seleccionado = False
        self.dibujar_correa()

    def actualizar_direccion(self, direccion_derecha):
        """Actualiza la dirección (True = derecha, False = izquierda) y redibuja."""
        self.direccion_derecha = bool(direccion_derecha)
        self.dibujar_correa()

    def handle_click(self, event):
        # ¿Click en "Ver Todos"?
        clicked_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in clicked_items:
            if "ver_todos" in self.canvas.gettags(item):
                self.todos_seleccionado = True
                self.selected_tramo = None
                self.dibujar_correa()
                if self.on_tramo_selected:
                    self.on_tramo_selected(None)
                return

        # ¿Click en un rodillo?
        for tramo_id, cx, cy in self.rodillos_posiciones:
            dist = ((event.x - cx) ** 2 + (event.y - cy) ** 2) ** 0.5
            if dist <= self.radio_rodillo:
                self.selected_tramo = tramo_id
                self.todos_seleccionado = False
                self.dibujar_correa()
                if self.on_tramo_selected:
                    self.on_tramo_selected(tramo_id)
                return
            
    
    def actualizar_tramos_con_longitudes(self, tramos_info):
        """
        Actualiza el canvas con las longitudes reales de los tramos.
        
        Args:
            tramos_info: Lista de diccionarios con {'numero': X, 'largo': Y}
        """
        self.tramos_info = tramos_info
        self.tramos = len(tramos_info)
        self.dibujar_correa()

    def get_canvas(self):
        return self.canvas
