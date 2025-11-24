import sys, traceback
import tkinter as tk
from views.login_window import LoginWindow
from modules.main_window import MainWindow
from controllers.main_controller import MainController
from utils.folder_dataset import DatasetFolderManager
from utils.database_connection import get_db

# La función ahora recibe la instancia de la ventana raíz (tk.Tk())
def abrir_ventana_principal(main_root_instance):
    trained_models_path = DatasetFolderManager.obtener_ruta_trained_models()
    DatasetFolderManager.crear_estructura_base(trained_models_path)

    # Obtener sesión de base de datos
    db_session = next(get_db())
    controller = MainController(window=None, db_session=db_session) 

    # La MainWindow se crea como un Toplevel, siendo hija de la ventana raíz principal oculta.
    app = MainWindow(main_root_instance, controller) # PASAMOS main_root_instance

    controller.window = app

    # Importante: NO LLAMAMOS app.run() aquí.
    # El único mainloop es el de 'root_login' que se mantiene activo.
try:
    if __name__ == "__main__":
        # Creamos la ÚNICA ventana raíz de Tkinter que manejará toda la aplicación.
        root_login = tk.Tk()
        root_login.withdraw() # Inicia oculta para que no aparezca una ventana en blanco inicialmente.
                            # Será revelada o manejada por el LoginWindow/MainWindow.

        # Inicializamos la ventana de login, pasándole esta raíz y la función de callback.
        # El LoginWindow puede mostrar la raíz cuando la necesite.
        login_window = LoginWindow(root_login, on_login_success=abrir_ventana_principal)
        
        # Después de crear el LoginWindow, lo hacemos visible
        root_login.deiconify() # Muestra la ventana principal (que ahora tiene el login)

        # Mantenemos UN SOLO mainloop para toda la aplicación.
        root_login.mainloop()
except Exception:
    traceback.print_exc()  # imprime en consola
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)  # guarda en archivo     