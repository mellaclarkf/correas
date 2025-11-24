import tkinter as tk
from tkinter import messagebox

class ContextMenuHelper:
    def __init__(self, master, treeview, get_columns_callback, eliminar_callback):
        self.master = master
        self.treeview = treeview
        self.get_columns = get_columns_callback
        self.eliminar_callback = eliminar_callback

        self.popup_menu = tk.Menu(self.master, tearoff=0)
        self.popup_menu.add_command(label="Ver detalles", command=self.ver_detalles)
        self.popup_menu.add_command(label="Eliminar fila", command=self.eliminar_fila)
        self.popup_menu.add_command(label="Guardar fila")

        self.treeview.bind("<Button-3>", self.mostrar_menu_contextual)

    def mostrar_menu_contextual(self, event):
        item_id = self.treeview.identify_row(event.y)
        if item_id:
            valores = self.treeview.item(item_id, "values")
            if len(valores) >= 2:
                nombre = valores[1].lower()  # convertir a minúsculas para comparación
                if any(palabra in nombre for palabra in ["manual", "video"]):
                    self.treeview.selection_set(item_id)
                    self.popup_menu.post(event.x_root, event.y_root)
                    return
        self.treeview.selection_remove(self.treeview.selection())


    def ver_detalles(self):
        selected_item = self.treeview.selection()
        if selected_item:
            valores = self.treeview.item(selected_item[0], "values")
            detalles = "\n".join(f"{col}: {valores[i]}" for i, col in enumerate(self.get_columns()))
            messagebox.showinfo("Detalles de la fila", detalles)

    def eliminar_fila(self):
        selected_item = self.treeview.selection()
        if selected_item:
            confirm = messagebox.askyesno("Eliminar fila", "¿Está seguro de eliminar la fila seleccionada?")
            if confirm:
                self.eliminar_callback(selected_item[0])
