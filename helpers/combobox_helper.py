import tkinter.ttk as ttk

def crear_combobox_etiquetas(parent, x, y, width, height, valor_inicial, callback):
    """
    Crea y posiciona un Combobox con las etiquetas de defectos.
    """
    opciones = [
        "CORTES",
        "DESGASTE", 
        "DESPRENDIMIENTO",
        "REPARACIONES",
        "DESGARROS",
        "EMPALME",
        "Confirmar"  # Mantener por compatibilidad
    ]
    combobox = ttk.Combobox(parent, values=opciones)
    combobox.place(x=x, y=y, width=width, height=height)
    combobox.set(valor_inicial)
    combobox.bind("<<ComboboxSelected>>", callback)
    return combobox
