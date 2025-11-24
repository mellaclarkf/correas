import tkinter as tk
from tkinter import messagebox

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root  # Esta es la ventana tk.Tk() principal pasada desde main.py
        self.root.title("Inicio de Sesión")
        # Asegurarse de que la ventana de login se muestre si estaba oculta por root.withdraw()
        self.root.deiconify() 
        # Asegurarse de que el mainloop no cierre la ventana raíz directamente
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing_login)

        self.on_login_success = on_login_success

        # Creamos los widgets de login directamente en la ventana raíz (self.root)
        tk.Label(self.root, text="Usuario:").grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Contraseña:").grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Iniciar sesión", command=self.verificar_credenciales).grid(row=2, column=0, columnspan=2, pady=20)

    def verificar_credenciales(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" and password == "":
            self.root.withdraw()  # <-- Oculta la ventana de login (la raíz principal)
            self.on_login_success(self.root) # <-- PASAMOS la ventana raíz al callback
        else:
            messagebox.showerror("Error de inicio de sesión", "Usuario o contraseña incorrectos.")

    def on_closing_login(self):
        # Cuando se intenta cerrar la ventana de login, pregunta si realmente quiere salir de la aplicación.
        if messagebox.askokcancel("Salir", "¿Realmente quieres salir de la aplicación?"):
            self.root.destroy() # Destruye la ventana raíz, terminando la aplicación.