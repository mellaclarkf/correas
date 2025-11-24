import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox, ttk
from services.maquina_service import MaquinaService
from utils.database_connection import get_db

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        
        # Obtener sesión de base de datos y crear servicio
        self.db_session = next(get_db())
        self.maquina_service = MaquinaService(self.db_session)

        self.maquina_seleccionada = None

        self.title("Configuración de la Aplicación")
        self.geometry("810x600")

        # Layout general: panel izquierdo (botones) y derecho (contenido)
        self.left_frame = tk.Frame(self, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.setup_buttons()

    def setup_buttons(self):
        tk.Label(self.left_frame, text="Opciones de Configuración", font=("Arial", 12, "bold")).pack(pady=10)

        # Botón para Cambiar Contraseña
        btn_change_password = tk.Button(self.left_frame, text="Cambiar Contraseña", command=self.show_change_password)
        btn_change_password.pack(pady=5, fill=tk.X)

        # Botón para Agregar Usuario
        btn_add_user = tk.Button(self.left_frame, text="Agregar Usuario", command=self.show_add_user)
        btn_add_user.pack(pady=5, fill=tk.X)

        # Botón para Gestión de Máquinas
        btn_manage_machines = tk.Button(self.left_frame, text="Gestión de Máquinas", command=self.show_machine_management)
        btn_manage_machines.pack(pady=5, fill=tk.X)

        # Botón para CRUD Tramos
        btn_edit_tramos = tk.Button(self.left_frame, text="Editar Tramos", command=self.show_tramo_crud)
        btn_edit_tramos.pack(pady=5, fill=tk.X)

        # Cerrar
        btn_close = tk.Button(self.left_frame, text="Cerrar", command=self.destroy)
        btn_close.pack(pady=20, fill=tk.X)

    def clear_right_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def show_change_password(self):
        self.clear_right_frame()
        tk.Label(self.right_frame, text="Cambiar Contraseña (demo)", font=("Arial", 12)).pack(pady=10)
        # Aquí puedes agregar campos y lógica real...

    def show_add_user(self):
        self.clear_right_frame()
        tk.Label(self.right_frame, text="Agregar Usuario (demo)", font=("Arial", 12)).pack(pady=10)
        # Aquí puedes agregar campos y lógica real...

    def show_tramo_crud(self):
        self.clear_right_frame()
        tk.Label(self.right_frame, text="Editar Tramos de Máquina", font=("Arial", 12, "bold")).pack(pady=10)

        # === Selección de máquina ===
        top_frame = tk.Frame(self.right_frame)
        top_frame.pack(fill=tk.X, pady=5)

        tk.Label(top_frame, text="Seleccionar Correa:").pack(anchor=tk.W)
        machine_names = self.maquina_service.obtener_nombres_maquinas()
        self.maquina_cb = ttk.Combobox(top_frame, values=machine_names, state="readonly", width=30)
        self.maquina_cb.pack(pady=5, anchor=tk.W)
        self.maquina_cb.bind("<<ComboboxSelected>>", self.load_tramos)

        # === Formulario inline para AGREGAR tramo ===
        form_frame = tk.LabelFrame(self.right_frame, text="Agregar Tramo", padx=10, pady=10)
        form_frame.pack(fill=tk.X, pady=5)

        tk.Label(form_frame, text="N° Tramo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.add_numero_entry = tk.Entry(form_frame, width=10)
        self.add_numero_entry.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(form_frame, text="Largo (m):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        self.add_largo_entry = tk.Entry(form_frame, width=10)
        self.add_largo_entry.grid(row=0, column=3, padx=5, pady=3)

        tk.Label(form_frame, text="Nota:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=3)
        self.add_nota_entry = tk.Entry(form_frame, width=30)
        self.add_nota_entry.grid(row=0, column=5, padx=5, pady=3)

        tk.Button(form_frame, text="Agregar", command=self.ui_agregar_tramo).grid(row=0, column=6, padx=10)

        # === Treeview de TRAMOS ===
        self.tramos_tree = ttk.Treeview(self.right_frame, columns=("numero", "largo", "nota"), show="headings")
        self.tramos_tree.heading("numero", text="N° Tramo")
        self.tramos_tree.heading("largo", text="Largo (m)")
        self.tramos_tree.heading("nota", text="Nota")
        self.tramos_tree.pack(expand=True, fill=tk.BOTH, pady=10)

        # Botones de acciones sobre tramos
        acciones_frame = tk.Frame(self.right_frame)
        acciones_frame.pack(fill=tk.X)

        tk.Button(acciones_frame, text="Guardar Cambios", command=self.guardar_tramos).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(acciones_frame, text="Eliminar Tramo Seleccionado", command=self.eliminar_tramo).pack(side=tk.LEFT, padx=5, pady=5)

        # Editar celdas con doble clic
        self.tramos_tree.bind('<Double-1>', self.on_treeview_double_click)

        # Estado interno
        self.id_maquina_actual = None

    def load_tramos(self, event=None):
        maquina_nombre = self.maquina_cb.get()
        id_maquina = self.maquina_service.obtener_id_maquina_por_nombre(maquina_nombre)
        
        if id_maquina is None:
            messagebox.showerror("Error", "No se encontró la máquina.")
            return
        
        self.id_maquina_actual = id_maquina

        # Cargar tramos en el tree
        for row in self.tramos_tree.get_children():
            self.tramos_tree.delete(row)
        
        tramos = self.maquina_service.obtener_tramos_por_maquina(id_maquina)
        for tramo in tramos:
            self.tramos_tree.insert("", tk.END, values=(tramo.numero_tramo, tramo.largo_tramo, tramo.nota))
        
        self.ajustar_columnas(self.tramos_tree)

    def guardar_tramos(self):
        if self.id_maquina_actual is None:
            messagebox.showerror("Error", "Seleccione una máquina primero.")
            return

        for item in self.tramos_tree.get_children():
            numero_tramo, largo_str, nota = self.tramos_tree.item(item)["values"]
            try:
                largo_tramo = float(largo_str) if str(largo_str).strip() != "" else None
            except ValueError:
                messagebox.showerror("Error", f"Largo inválido en tramo {numero_tramo}.")
                return
            
            # Actualizar el tramo
            self.maquina_service.actualizar_tramo(
                self.id_maquina_actual, 
                int(numero_tramo), 
                largo_tramo, 
                nota
            )

        messagebox.showinfo("Éxito", "Tramos guardados correctamente.")

    def on_treeview_double_click(self, event):
        selected_item = self.tramos_tree.identify_row(event.y)
        selected_column = self.tramos_tree.identify_column(event.x)

        if not selected_item or selected_column == '#0':
            return

        col_index = int(selected_column.replace('#', '')) - 1

        # Obtener coordenadas de la celda
        bbox = self.tramos_tree.bbox(selected_item, column=selected_column)
        if not bbox:
            return

        x, y, width, height = bbox
        value = self.tramos_tree.set(selected_item, column=selected_column)

        # Crear campo Entry sobre la celda
        entry = tk.Entry(self.tramos_tree)
        entry.insert(0, value)
        entry.select_range(0, tk.END)
        entry.focus()
        entry.place(x=x, y=y, width=width, height=height)

        def save_edit(event=None):
            new_value = entry.get()
            self.tramos_tree.set(selected_item, column=selected_column, value=new_value)
            entry.destroy()
            self.update_tramo_in_db(selected_item)

        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', lambda e: entry.destroy())

    def update_tramo_in_db(self, item_id):
        tramo_data = self.tramos_tree.item(item_id, 'values')
        try:
            numero_tramo = int(tramo_data[0])
            largo_tramo = float(tramo_data[1]) if tramo_data[1] else None
            nota = tramo_data[2]
        except Exception as e:
            print(f"Error al convertir datos: {e}")
            return

        # Actualizar usando el servicio
        self.maquina_service.actualizar_tramo(
            self.id_maquina_actual,
            numero_tramo,
            largo_tramo,
            nota
        )

    def ajustar_columnas(self, tree):
        font = tkFont.Font()
        for col in tree["columns"]:
            max_width = font.measure(col)
            for item in tree.get_children():
                valor = tree.set(item, col)
                width = font.measure(str(valor))
                if width > max_width:
                    max_width = width
            tree.column(col, width=max_width + 10)

    def show_machine_management(self):
        """Muestra la interfaz para gestionar máquinas"""
        self.clear_right_frame()
        
        tk.Label(self.right_frame, text="Gestión de Máquinas", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame para agregar nueva máquina
        add_frame = tk.LabelFrame(self.right_frame, text="Agregar Nueva Máquina", padx=10, pady=10)
        add_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Campos para nueva máquina
        tk.Label(add_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.new_machine_name = tk.Entry(add_frame, width=30)
        self.new_machine_name.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(add_frame, text="Dirección:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.new_machine_direction = ttk.Combobox(add_frame, values=["Derecha", "Izquierda"], state="readonly", width=15)
        self.new_machine_direction.set("Derecha")
        self.new_machine_direction.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        tk.Label(add_frame, text="Ubicación:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.new_machine_ubicacion = tk.Entry(add_frame, width=30)
        self.new_machine_ubicacion.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(add_frame, text="Largo (m):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.new_machine_largo = tk.Entry(add_frame, width=30)
        self.new_machine_largo.grid(row=3, column=1, pady=5, padx=5)

        btn_add = tk.Button(add_frame, text="Agregar Máquina", command=self.add_new_machine)
        btn_add.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Frame para lista de máquinas existentes
        list_frame = tk.LabelFrame(self.right_frame, text="Máquinas Existentes", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # Treeview para mostrar máquinas
        columns = ("id", "nombre", "ubicacion", "largo", "direccion")
        self.machines_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.machines_tree.heading("id", text="ID")
        self.machines_tree.heading("nombre", text="Nombre")
        self.machines_tree.heading("ubicacion", text="Ubicación")
        self.machines_tree.heading("largo", text="Largo (m)")
        self.machines_tree.heading("direccion", text="Dirección")

        self.machines_tree.column("id", width=50)
        self.machines_tree.column("nombre", width=150)
        self.machines_tree.column("ubicacion", width=150)
        self.machines_tree.column("largo", width=80)
        self.machines_tree.column("direccion", width=100)
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.machines_tree.yview)
        self.machines_tree.configure(yscrollcommand=scrollbar.set)
        
        self.machines_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón para eliminar máquina seleccionada
        btn_delete = tk.Button(list_frame, text="Eliminar Máquina Seleccionada", command=self.delete_selected_machine)
        btn_delete.pack(pady=10)

        # Botón para Editar máquina seleccionada
        btn_edit = tk.Button(list_frame, text="Editar Máquina Seleccionada", command=self.edit_selected_machine)
        btn_edit.pack(pady=5)
        
        # Cargar máquinas existentes
        self.load_machines_list()

    def add_new_machine(self):
        """Agrega una nueva máquina a la base de datos"""
        nombre = self.new_machine_name.get().strip()
        ubicacion = self.new_machine_ubicacion.get().strip()
        direccion = self.new_machine_direction.get()
        
        if not nombre:
            messagebox.showerror("Error", "Debe ingresar un nombre para la máquina.")
            return
            
        # Convertir dirección a booleano
        direccion_bool = (direccion == "Derecha")
        
        # Obtener largo si se proporcionó
        largo_text = self.new_machine_largo.get().strip()
        largo = float(largo_text) if largo_text else None
        
        # Insertar en la base de datos usando el servicio
        nuevo_id = self.maquina_service.insertar_maquina(nombre, ubicacion, largo, direccion_bool)
        
        if nuevo_id:
            messagebox.showinfo("Éxito", f"Máquina '{nombre}' agregada correctamente.")
            self.new_machine_name.delete(0, tk.END)
            self.new_machine_ubicacion.delete(0, tk.END)
            self.new_machine_largo.delete(0, tk.END)
            self.load_machines_list()
        else:
            messagebox.showerror("Error", "No se pudo agregar la máquina. Verifique que el nombre no exista ya.")

    def delete_selected_machine(self):
        """Elimina la máquina seleccionada de la base de datos"""
        selected_item = self.machines_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selección requerida", "Por favor seleccione una máquina para eliminar.")
            return
            
        item = selected_item[0]
        values = self.machines_tree.item(item, "values")
        machine_id, machine_name = int(values[0]), values[1]
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar eliminación", 
                            f"¿Está seguro de que desea eliminar la máquina '{machine_name}'?\n\n"
                            "Esta acción también eliminará todos los tramos asociados."):
            # Eliminar la máquina usando el servicio
            if self.maquina_service.eliminar_maquina(machine_id):
                messagebox.showinfo("Éxito", f"Máquina '{machine_name}' eliminada correctamente.")
                self.load_machines_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la máquina.")

    def load_machines_list(self):
        """Carga la lista de máquinas en el treeview"""
        # Limpiar treeview
        for item in self.machines_tree.get_children():
            self.machines_tree.delete(item)
            
        # Obtener máquinas de la base de datos usando el servicio
        maquinas = self.maquina_service.obtener_todas_maquinas()
        
        # Llenar treeview
        for maquina in maquinas:
            direccion_texto = "Derecha" if maquina.direccion else "Izquierda"
            self.machines_tree.insert("", tk.END, values=(
                maquina.id, 
                maquina.nombre, 
                maquina.ubicacion if maquina.ubicacion else "",
                maquina.largo if maquina.largo else "",
                direccion_texto
            ))

    def edit_selected_machine(self):
        """Permite editar la máquina seleccionada"""
        selected_item = self.machines_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selección requerida", "Por favor seleccione una máquina para editar.")
            return

        item = selected_item[0]
        values = self.machines_tree.item(item, "values")
        machine_id = int(values[0])

        # Ventana emergente para edición
        edit_win = tk.Toplevel(self)
        edit_win.title("Editar Máquina")

        tk.Label(edit_win, text="Nombre:").grid(row=0, column=0, pady=5, sticky=tk.W)
        nombre_entry = tk.Entry(edit_win, width=30)
        nombre_entry.insert(0, values[1])
        nombre_entry.grid(row=0, column=1, pady=5)

        tk.Label(edit_win, text="Ubicación:").grid(row=1, column=0, pady=5, sticky=tk.W)
        ubicacion_entry = tk.Entry(edit_win, width=30)
        ubicacion_entry.insert(0, values[2])
        ubicacion_entry.grid(row=1, column=1, pady=5)

        tk.Label(edit_win, text="Largo (m):").grid(row=2, column=0, pady=5, sticky=tk.W)
        largo_entry = tk.Entry(edit_win, width=30)
        largo_entry.insert(0, values[3])
        largo_entry.grid(row=2, column=1, pady=5)

        tk.Label(edit_win, text="Dirección:").grid(row=3, column=0, pady=5, sticky=tk.W)
        direccion_cb = ttk.Combobox(edit_win, values=["Derecha", "Izquierda"], state="readonly")
        direccion_cb.set(values[4])
        direccion_cb.grid(row=3, column=1, pady=5)

        def save_changes():
            nombre = nombre_entry.get().strip()
            ubicacion = ubicacion_entry.get().strip()
            try:
                largo = float(largo_entry.get().strip()) if largo_entry.get().strip() else None
            except ValueError:
                messagebox.showerror("Error", "Largo debe ser un número válido.")
                return
            direccion = (direccion_cb.get() == "Derecha")

            # Actualizar usando el servicio
            self.maquina_service.actualizar_maquina(machine_id, nombre, ubicacion, largo, direccion)
            self.load_machines_list()
            edit_win.destroy()

        btn_save = tk.Button(edit_win, text="Guardar Cambios", command=save_changes)
        btn_save.grid(row=4, column=0, columnspan=2, pady=10)

    def ui_agregar_tramo(self):
        if self.id_maquina_actual is None:
            messagebox.showerror("Error", "Seleccione una máquina primero.")
            return

        num_txt = self.add_numero_entry.get().strip()
        largo_txt = self.add_largo_entry.get().strip()
        nota_txt = self.add_nota_entry.get().strip()

        if not num_txt:
            messagebox.showerror("Error", "Debe indicar el número de tramo.")
            return

        try:
            numero_tramo = int(num_txt)
        except ValueError:
            messagebox.showerror("Error", "El número de tramo debe ser un entero.")
            return

        try:
            largo_tramo = float(largo_txt) if largo_txt else None
        except ValueError:
            messagebox.showerror("Error", "El largo del tramo debe ser numérico.")
            return

        # Evitar duplicados rápido en UI
        for item in self.tramos_tree.get_children():
            n, _, _ = self.tramos_tree.item(item)["values"]
            if int(n) == numero_tramo:
                messagebox.showwarning("Atención", f"El tramo N° {numero_tramo} ya existe.")
                return

        # Insertar usando el servicio
        nuevo_id = self.maquina_service.insertar_tramo(self.id_maquina_actual, numero_tramo, largo_tramo, nota_txt)
        if not nuevo_id:
            messagebox.showerror("Error", f"No se pudo insertar. Verifique que el tramo N° {numero_tramo} no exista ya.")
            return

        # Limpiar inputs y refrescar
        self.add_numero_entry.delete(0, tk.END)
        self.add_largo_entry.delete(0, tk.END)
        self.add_nota_entry.delete(0, tk.END)

        self.load_tramos()

    def eliminar_tramo(self):
        if self.id_maquina_actual is None:
            messagebox.showerror("Error", "Seleccione una máquina primero.")
            return

        sel = self.tramos_tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un tramo para eliminar.")
            return

        item = sel[0]
        numero_tramo, _, _ = self.tramos_tree.item(item)["values"]

        if not messagebox.askyesno("Confirmar", f"¿Eliminar el tramo N° {numero_tramo}?"):
            return

        # Eliminar usando el servicio
        ok = self.maquina_service.eliminar_tramo_por_numero(self.id_maquina_actual, int(numero_tramo))
        if not ok:
            messagebox.showerror("Error", "No se pudo eliminar el tramo.")
            return

        self.load_tramos()

    def show(self):
        self.grab_set()
        self.wait_window()