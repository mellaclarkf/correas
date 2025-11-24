import tkinter as tk
from tkcalendar import Calendar
from tkinter import ttk, messagebox
from services.maquina_service import MaquinaService
from utils.database_connection import get_db

class DatePopup(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Seleccionar Fecha y Correa")
        self.grab_set()

        self.fecha_seleccionada = None
        self.maquina_seleccionada = None
        self.tramo_inicial = None
        self.distancia_siguiente_tramo = None

        # Obtener sesión de base de datos
        self.db = next(get_db())
        self.maquina_service = MaquinaService(self.db)

        # Calendario
        self.calendar = Calendar(self, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(padx=10, pady=10)

        # Correa
        tk.Label(self, text="Seleccionar Correa:").pack(pady=(10, 0))
        self.machine_options = self.maquina_service.obtener_nombres_maquinas()
        self.maquina_combobox = ttk.Combobox(self, values=self.machine_options, state="readonly")
        self.maquina_combobox.set("Seleccione Correa")
        self.maquina_combobox.pack(padx=10, pady=5)

        # Tramo inicial
        tk.Label(self, text="Tramo inicial (entero):").pack(pady=(10, 0))
        self.entry_tramo_inicial = tk.Entry(self)
        self.entry_tramo_inicial.pack(padx=10, pady=5)

        # Distancia al siguiente tramo
        tk.Label(self, text="Distancia al siguiente tramo (m):").pack(pady=(10, 0))
        self.entry_distancia_tramo = tk.Entry(self)
        self.entry_distancia_tramo.pack(padx=10, pady=5)

        # Confirmar
        btn_confirmar = tk.Button(self, text="Confirmar", command=self.confirmar_seleccion)
        btn_confirmar.pack(pady=10)

        # Validación de pulsaciones de teclado
        vcmd_int = (self.register(self.validate_integer_input), "%P")
        vcmd_float = (self.register(self.validate_float_input), "%P")

        self.entry_tramo_inicial.config(validate="key", validatecommand=vcmd_int)
        self.entry_distancia_tramo.config(validate="key", validatecommand=vcmd_float)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def confirmar_seleccion(self):
        self.fecha_seleccionada = self.calendar.get_date()
        self.maquina_seleccionada = self.maquina_combobox.get()
        
        if self.maquina_seleccionada == "Seleccione Correa":
            self.maquina_seleccionada = None
            messagebox.showerror("Error", "Debe seleccionar una correa.")
            return

        # Validar tramo inicial (entero)
        try:
            tramo = int(self.entry_tramo_inicial.get())
        except ValueError:
            messagebox.showerror("Error", "El tramo inicial debe ser un número entero.")
            return

        # Obtener el ID de la máquina seleccionada
        id_maquina = self.maquina_service.obtener_id_maquina_por_nombre(self.maquina_seleccionada)
        if id_maquina is None:
            messagebox.showerror("Error", "No se encontró el ID de Correa seleccionada.")
            return
        
        # Contar los tramos
        numero_tramos = self.maquina_service.contar_tramos_de_maquina(id_maquina)

        if tramo < 1 or tramo > numero_tramos:
            messagebox.showerror("Error", f"El tramo inicial debe estar entre 1 y {numero_tramos}.")
            return
        
        self.tramo_inicial = tramo

        # Validar distancia al siguiente tramo (decimal > 0)
        try:
            distancia = float(self.entry_distancia_tramo.get())
            if distancia <= 0:
                messagebox.showerror("Error", "La distancia al siguiente tramo debe ser mayor a 0.")
                return
            self.distancia_siguiente_tramo = distancia
        except ValueError:
            messagebox.showerror("Error", "La distancia al siguiente tramo debe ser un número decimal.")
            return

        self.destroy()

    def validate_integer_input(self, value):
        """Permite solo enteros positivos (sin signo)"""
        return value.isdigit() or value == ""

    def validate_float_input(self, value):
        """Permite solo números decimales positivos"""
        if value == "":
            return True
        try:
            float_value = float(value)
            return float_value >= 0 and not value.startswith("-")
        except ValueError:
            return False

    def on_close(self):
        self.fecha_seleccionada = None
        self.maquina_seleccionada = None
        self.tramo_inicial = None
        self.distancia_siguiente_tramo = None
        self.destroy()

    def show(self):
        self.wait_window()
        return (
            self.fecha_seleccionada,
            self.maquina_seleccionada,
            self.tramo_inicial,
            self.distancia_siguiente_tramo
        )