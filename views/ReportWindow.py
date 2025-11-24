# views/ReportWindow.py
import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from utils.database_connection import engine  
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from sqlalchemy.orm import Session
from services.historial_repository import HistorialRepository

class ReportWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Análisis de Defectos por Correa")
        self.geometry("1100x700")
        self.figures = []
        self._setup_ui()
        self._load_models()
        self._generate_report()

    def _setup_ui(self):
        """Configura la interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controles en la parte superior
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selector de modelo
        ttk.Label(control_frame, text="Modelo de Correa:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.cmb_model = ttk.Combobox(control_frame, state="readonly", width=25)
        self.cmb_model.grid(row=0, column=1, padx=5)
        self.cmb_model.bind("<<ComboboxSelected>>", lambda e: self._generate_report())
        
        # Selector de tramo
        ttk.Label(control_frame, text="Tramo:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.cmb_tramo = ttk.Combobox(control_frame, state="readonly", width=12)
        self.cmb_tramo.grid(row=0, column=3, padx=5)
        self.cmb_tramo.bind("<<ComboboxSelected>>", lambda e: self._generate_report())

        # Selector de fecha de video
        ttk.Label(control_frame, text="Fecha Video:").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.cmb_fecha = ttk.Combobox(control_frame, state="readonly", width=12)
        self.cmb_fecha.grid(row=0, column=5, padx=5)
        self.cmb_fecha.bind("<<ComboboxSelected>>", lambda e: self._generate_report())        
        
        # Botón para PDF
        btn_pdf = ttk.Button(control_frame, text="Exportar a PDF", command=self._export_pdf)
        btn_pdf.grid(row=0, column=4, padx=5)
        
        # Configurar pesos de columnas para centrar los elementos
        control_frame.columnconfigure(0, weight=0)
        control_frame.columnconfigure(1, weight=0)
        control_frame.columnconfigure(2, weight=0)
        control_frame.columnconfigure(3, weight=0)
        control_frame.columnconfigure(4, weight=1)
        
        # Frame para el área de gráficos con scroll
        graph_container = ttk.Frame(main_frame)
        graph_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        self.canvas = tk.Canvas(graph_container)
        scrollbar = ttk.Scrollbar(graph_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Área de gráficos
        self.graph_frame = ttk.Frame(self.scrollable_frame)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    # Obtiene los modelos de correa y los carga en combobox
    def _load_models(self):
        """Carga los modelos de correa disponibles"""
        try:
            # Obtener sesión de base de datos
            db_session = Session(engine)
            historial_repo = HistorialRepository(db_session)
            
            # Obtener modelos únicos
            modelos = historial_repo.obtener_modelos_unicos()
            
            self.cmb_model['values'] = modelos
            if modelos:
                self.cmb_model.current(0)
                self._load_tramos()
                self._load_fechas() 
                
            db_session.close()
        except Exception as e:
            print(f"Error cargando modelos: {e}")

    # Carga los tramos disponibles para el modelo seleccionado
    def _load_tramos(self):
        model = self.cmb_model.get()
        if not model:
            return
            
        try:
            # Obtener sesión de base de datos
            db_session = Session(engine)
            historial_repo = HistorialRepository(db_session)
            
            # Obtener tramos únicos para el modelo
            tramos = historial_repo.obtener_tramos_por_modelo(model)
            
            tramos = sorted([int(t) for t in tramos if t is not None])
            tramos = [f"Tramo {t}" for t in tramos]
            
            self.cmb_tramo['values'] = ['Todos'] + tramos
            self.cmb_tramo.current(0)
            
            db_session.close()
        except Exception as e:
            print(f"Error cargando tramos: {e}")

    def _generate_report(self):
        """Genera los gráficos basados en la selección actual"""
        model = self.cmb_model.get()
        tramo_seleccionado = self.cmb_tramo.get()
        fecha_seleccionada = self.cmb_fecha.get()
        
        if not model or not fecha_seleccionada:
            print("⚠️ Faltan modelo o fecha seleccionada")
            return
            
        try:
            # Obtener fecha anterior
            fecha_anterior = self._obtener_fecha_anterior(model, tramo_seleccionado, fecha_seleccionada)
            
            print(f"📊 Generando reporte para: Modelo={model}, Tramo={tramo_seleccionado}")
            print(f"📅 Fechas: Seleccionada={fecha_seleccionada}, Anterior={fecha_anterior}")
            
            # Limpiar gráficos anteriores
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
                
            self.figures = []

            # 1️⃣ Gráfico del día seleccionado
            print("📈 Generando gráfico del día...")
            fig1 = self._grafico_dia(model, fecha_seleccionada, tramo_seleccionado)
            if fig1:
                self.figures.append(fig1)
                print("✅ Gráfico del día generado")

            # 2️⃣ Gráfico comparativo
            if fecha_anterior:
                print("📈 Generando gráfico comparativo...")
                fig2 = self._grafico_comparativo_dos_dias(model, fecha_anterior, fecha_seleccionada, tramo_seleccionado)
                if fig2:
                    self.figures.append(fig2)
                    print("✅ Gráfico comparativo generado")
                else:
                    # Mostrar mensaje informativo en la interfaz
                    info_label = ttk.Label(self.graph_frame, 
                                        text=f"⚠️ No hay datos suficientes para comparar {fecha_anterior} vs {fecha_seleccionada}",
                                        foreground="orange",
                                        font=("Arial", 10))
                    info_label.pack(pady=10)
                    print("⚠️ No se pudo generar gráfico comparativo - datos insuficientes")
                print("📈 Generando gráfico Reparaciones vs Desgaste...")
                fig3 = self._grafico_reparaciones_vs_desgaste_por_tramos(model, fecha_anterior, fecha_seleccionada)
                if fig3:
                    self.figures.append(fig3)
                    print("✅ Gráfico Reparaciones vs Desgaste generado")
                else:
                    print("⚠️ No se pudo generar gráfico Reparaciones vs Desgaste")                    
                # # 4️⃣ Gráfico de distancias de fallas por tramo (SIEMPRE para TODOS los tramos)
                # fig4 = self._grafico_distancias_fallas_por_tramo(model, fecha_anterior, fecha_seleccionada)
                # if fig4:
                #     self.figures.append(fig4)   

                # 5️⃣ NUEVO: Gráfico de breaker expuesto por tramos (basado en tu imagen)
                # fig5 = self._grafico_distancias_breaker_por_tramos(model, fecha_anterior, fecha_seleccionada)
                # if fig5:
                #     self.figures.append(fig5)                
            else:
                print("⚠️ No hay fecha anterior para comparar")
        
        except Exception as e:
            print(f"❌ Error generando gráficos: {e}")
            import traceback
            print(f"❌ Traceback completo: {traceback.format_exc()}")

    def _grafico_dia(self, model, fecha, tramo_seleccionado):
        """Genera gráfico de barras simple con los defectos del último día con tabla"""
        try:
            # Obtener sesión de base de datos
            db_session = Session(engine)
            historial_repo = HistorialRepository(db_session)
            
            num_tramo = None
            if tramo_seleccionado != "Todos":
                num_tramo = int(tramo_seleccionado.split()[-1])
                
            # Obtener datos de defectos por predicción
            df = historial_repo.obtener_defectos_por_prediccion(model, fecha, num_tramo)
            
            if df.empty:
                return None

            # Crear figura con dos subplots: gráfico arriba, tabla abajo
            fig = Figure(figsize=(12, 8), dpi=100)
            gs = fig.add_gridspec(2, 1, height_ratios=[2, 1])  # 2/3 para gráfico, 1/3 para tabla
            
            # Subplot para el gráfico
            ax1 = fig.add_subplot(gs[0])

            x_pos = np.arange(len(df['prediccion']))
            bars = ax1.bar(x_pos, df['cantidad'], color='skyblue')
            
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                        f'{int(height)}', ha='center', va='bottom')

            ax1.set_title(f"DEFECTOS - {fecha}", fontsize=14, pad=15)
            ax1.set_xlabel("Tipo de Defecto")
            ax1.set_ylabel("Cantidad")
            ax1.set_ylim(0, max(df['cantidad']) + 5)
            ax1.grid(axis='y', linestyle='--', alpha=0.6)
            
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(df['prediccion'], rotation=45, ha='right')
            
            # Subplot para la tabla
            ax2 = fig.add_subplot(gs[1])
            ax2.axis('off')  # Ocultar ejes
            
            # Preparar datos para la tabla
            tabla_datos = []
            total_defectos = 0
            
            for _, row in df.iterrows():
                fila = [row['prediccion'], row['cantidad']]
                tabla_datos.append(fila)
                total_defectos += row['cantidad']
            
            # Agregar fila de total
            tabla_datos.append(['TOTAL', total_defectos])
            
            # Crear la tabla
            column_labels = ['Tipo de Defecto', 'Cantidad']
            
            table = ax2.table(cellText=tabla_datos,
                            colLabels=column_labels,
                            cellLoc='center',
                            loc='center',
                            bbox=[0, 0, 1, 1])
            
            # Formatear la tabla
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)
            
            # Estilo para la tabla
            for i, key in enumerate(table.get_celld().keys()):
                cell = table.get_celld()[key]
                if key[0] == 0:  # Encabezados
                    cell.set_facecolor('#4CAF50')
                    cell.set_text_props(weight='bold', color='white')
                elif key[0] == len(tabla_datos):  # Fila de total
                    cell.set_facecolor('#FF9800')
                    cell.set_text_props(weight='bold', color='white')
            
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

            db_session.close()
            return fig
            
        except Exception as e:
            print(f"Error en gráfico del día: {e}")
            return None

    def _grafico_comparativo_dos_dias(self, model, fecha_anterior, fecha_seleccionada, tramo_seleccionado):
        """Genera gráfico comparativo entre fecha anterior y fecha seleccionada con tabla"""
        try:
            print(f"🔍 Iniciando gráfico comparativo: {fecha_anterior} vs {fecha_seleccionada}")
            
            # Obtener sesión de base de datos
            db_session = Session(engine)
            historial_repo = HistorialRepository(db_session)
            
            num_tramo = None
            if tramo_seleccionado != "Todos":
                num_tramo = int(tramo_seleccionado.split()[-1])
                
            # Obtener datos para CADA FECHA por SEPARADO
            df_anterior = historial_repo.obtener_defectos_por_prediccion(model, fecha_anterior, num_tramo)
            df_seleccionada = historial_repo.obtener_defectos_por_prediccion(model, fecha_seleccionada, num_tramo)
            
            print(f"🔍 Datos anterior: {len(df_anterior)}")
            print(f"🔍 Datos seleccionada: {len(df_seleccionada)}")
            
            # Lista completa de defectos
            todos_defectos = ["CORTES", "CRISTALIZADO", "DESGARROS", "DESGASTE", 
                            "DESPRENDIMIENTO", "EMPALME", "REPARACIONES"]
            
            # Preparar datos para el gráfico y la tabla
            datos_anterior = []
            datos_seleccionada = []
            datos_tabla = []  # Para almacenar los datos de la tabla
            
            for defecto in todos_defectos:
                # Buscar en datos anteriores
                fila_anterior = df_anterior[df_anterior['prediccion'] == defecto]
                cantidad_anterior = fila_anterior['cantidad'].values[0] if not fila_anterior.empty else 0
                
                # Buscar en datos seleccionados
                fila_seleccionada = df_seleccionada[df_seleccionada['prediccion'] == defecto]
                cantidad_seleccionada = fila_seleccionada['cantidad'].values[0] if not fila_seleccionada.empty else 0
                
                datos_anterior.append(cantidad_anterior)
                datos_seleccionada.append(cantidad_seleccionada)
                
                # Calcular diferencia
                diferencia = cantidad_seleccionada - cantidad_anterior
                tendencia = "↑" if diferencia > 0 else "↓" if diferencia < 0 else "="
                
                # Agregar datos para la tabla
                datos_tabla.append([
                    defecto,
                    cantidad_anterior,
                    cantidad_seleccionada,
                    diferencia,
                    tendencia
                ])
            
            # Crear figura con dos subplots: gráfico arriba, tabla abajo
            fig = Figure(figsize=(14, 10), dpi=100)
            gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])  # 3/4 para gráfico, 1/4 para tabla
            
            # Subplot para el gráfico
            ax1 = fig.add_subplot(gs[0])
            
            bar_width = 0.35
            indices = np.arange(len(todos_defectos))
            
            # Crear barras
            bars_anterior = ax1.bar(indices - bar_width/2, datos_anterior, bar_width, 
                                label=f'Anterior: {fecha_anterior}', color='#FF9999', alpha=0.8)
            
            bars_seleccionada = ax1.bar(indices + bar_width/2, datos_seleccionada, bar_width, 
                                    label=f'Seleccionada: {fecha_seleccionada}', color='#66B2FF', alpha=0.8)
            
            # Añadir valores en las barras
            for bars in [bars_anterior, bars_seleccionada]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax1.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            ax1.set_title(f"COMPARATIVA: {fecha_anterior} vs {fecha_seleccionada}\nModelo: {model} - Tramo: {tramo_seleccionado}", 
                        fontsize=14, pad=15, fontweight='bold')
            ax1.set_xlabel("Tipo de Defecto", fontweight='bold')
            ax1.set_ylabel("Cantidad de Defectos", fontweight='bold')
            ax1.set_xticks(indices)
            ax1.set_xticklabels(todos_defectos, rotation=45, ha='right')
            ax1.legend()
            ax1.grid(axis='y', linestyle='--', alpha=0.6)
            
            # Ajustar límites del eje Y
            max_value = max(max(datos_anterior), max(datos_seleccionada))
            ax1.set_ylim(0, max_value + 2)
            
            # Subplot para la tabla
            ax2 = fig.add_subplot(gs[1])
            ax2.axis('off')  # Ocultar ejes
            
            # Crear tabla
            column_labels = ['Defecto', f'{fecha_anterior}', f'{fecha_seleccionada}', 'Diferencia', 'Tendencia']
            
            # Crear la tabla
            table = ax2.table(cellText=datos_tabla,
                            colLabels=column_labels,
                            cellLoc='center',
                            loc='center',
                            bbox=[0, 0, 1, 1])  # bbox: [left, bottom, width, height]
            
            # Formatear la tabla
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)
            
            # Estilo para la tabla
            for i, key in enumerate(table.get_celld().keys()):
                cell = table.get_celld()[key]
                if key[0] == 0:  # Encabezados
                    cell.set_facecolor('#4CAF50')
                    cell.set_text_props(weight='bold', color='white')
                elif key[1] == 4:  # Columna de tendencia
                    valor = cell.get_text().get_text()
                    if valor == "↑":
                        cell.set_facecolor('#FFCDD2')  # Rojo claro para aumento
                    elif valor == "↓":
                        cell.set_facecolor('#C8E6C9')  # Verde claro para disminución
                    else:
                        cell.set_facecolor('#F5F5F5')  # Gris para igual
                elif key[1] == 3:  # Columna de diferencia
                    valor = int(cell.get_text().get_text())
                    if valor > 0:
                        cell.set_facecolor('#FFCDD2')  # Rojo claro para aumento
                    elif valor < 0:
                        cell.set_facecolor('#C8E6C9')  # Verde claro para disminución
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
            
            db_session.close()
            print(f"✅ Gráfico comparativo con tabla creado exitosamente")
            return fig
            
        except Exception as e:
            print(f"❌ Error en gráfico comparativo: {e}")
            import traceback
            print(f"❌ Traceback completo: {traceback.format_exc()}")
            return None
            
    def _grafico_reparaciones_vs_desgaste_por_tramos(self, model, fecha_anterior, fecha_seleccionada):
        """Genera gráfico con 2 barras por tramo, cada una con 2 segmentos (4 colores)"""
        try:
            print(f"🔍 GRÁFICO 3 - INICIANDO")
            print(f"🔍 Fechas: {fecha_anterior} vs {fecha_seleccionada}")
            
            # Obtener sesión de base de datos
            db_session = Session(engine)
            historial_repo = HistorialRepository(db_session)
            
            # Obtener datos COMPLETOS
            df = historial_repo.obtener_reparaciones_vs_desgaste(model, [fecha_anterior, fecha_seleccionada])
            
            if df.empty:
                print("❌ NO HAY DATOS")
                db_session.close()
                return None
            
            # Obtener todos los tramos únicos
            tramos = sorted(df['Tramo'].unique())
            
            # NORMALIZAR FECHAS
            if isinstance(fecha_anterior, str):
                fecha_anterior = pd.to_datetime(fecha_anterior).date()
            if isinstance(fecha_seleccionada, str):
                fecha_seleccionada = pd.to_datetime(fecha_seleccionada).date()
            
            # Preparar datos estructurados
            datos_por_tramo = {}
            
            for tramo in tramos:
                datos_por_tramo[tramo] = {
                    'Desgaste_anterior': 0,
                    'Desgaste_seleccionada': 0,
                    'Reparaciones_anterior': 0,
                    'Reparaciones_seleccionada': 0
                }
            
            # LLENAR CON DATOS REALES
            for _, row in df.iterrows():
                tramo = row['Tramo']
                fecha_df = row['fecha']
                
                # Convertir fecha del DataFrame
                if isinstance(fecha_df, str):
                    fecha_df = pd.to_datetime(fecha_df).date()
                elif hasattr(fecha_df, 'date'):
                    fecha_df = fecha_df.date()
                
                prediccion = row['prediccion']
                cantidad = int(row['cantidad'])
                
                if tramo in datos_por_tramo:
                    if fecha_df == fecha_anterior:
                        if prediccion == 'DESGASTE':
                            datos_por_tramo[tramo]['Desgaste_anterior'] = cantidad
                        elif prediccion == 'REPARACIONES':
                            datos_por_tramo[tramo]['Reparaciones_anterior'] = cantidad
                    elif fecha_df == fecha_seleccionada:
                        if prediccion == 'DESGASTE':
                            datos_por_tramo[tramo]['Desgaste_seleccionada'] = cantidad
                        elif prediccion == 'REPARACIONES':
                            datos_por_tramo[tramo]['Reparaciones_seleccionada'] = cantidad
            
            # Preparar datos para el gráfico
            desgaste_ant = [datos_por_tramo[t]['Desgaste_anterior'] for t in tramos]
            desgaste_sel = [datos_por_tramo[t]['Desgaste_seleccionada'] for t in tramos]
            reparaciones_ant = [datos_por_tramo[t]['Reparaciones_anterior'] for t in tramos]
            reparaciones_sel = [datos_por_tramo[t]['Reparaciones_seleccionada'] for t in tramos]
            
            # Crear figura con dos subplots: gráfico arriba, tabla abajo
            fig = Figure(figsize=(14, 10), dpi=100)
            gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])  # 3/4 para gráfico, 1/4 para tabla
            
            # Subplot para el gráfico
            ax1 = fig.add_subplot(gs[0])
            
            # Configurar posiciones - 2 BARRAS POR TRAMO
            x = np.arange(len(tramos))
            width = 0.35
            
            # ✅ COLORES COMO EL GRÁFICO 2 - NARANJAS Y AZULES
            # BARRAS DE DESGASTE (NARANJAS)
            bars_desgaste_ant = ax1.bar(x - width/2, desgaste_ant, width, 
                                    color='#FF9999', alpha=0.8)  # Naranja claro
            
            bars_desgaste_sel = ax1.bar(x - width/2, desgaste_sel, width, bottom=desgaste_ant,
                                    color='#FF6600', alpha=0.8)  # Naranja oscuro
            
            # BARRAS DE REPARACIONES (AZULES)
            bars_reparaciones_ant = ax1.bar(x + width/2, reparaciones_ant, width,
                                        color='#66B2FF', alpha=0.8)  # Azul claro
            
            bars_reparaciones_sel = ax1.bar(x + width/2, reparaciones_sel, width, bottom=reparaciones_ant,
                                        color='#0066CC', alpha=0.8)  # Azul oscuro
            
            # Añadir etiquetas de valores en CADA SEGMENTO
            def agregar_etiquetas_segmento(bars, bottoms=None):
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    bottom = bottoms[i] if bottoms is not None else 0
                    
                    if height > 0:  # Solo mostrar etiqueta si hay valor
                        y_position = bottom + height/2
                        ax1.text(bar.get_x() + bar.get_width()/2, 
                            y_position,
                            f'{int(height)}', 
                            ha='center', va='center', 
                            fontsize=8, fontweight='bold',
                            color='white' if height > 3 else 'black')
            
            # Etiquetas para cada segmento
            agregar_etiquetas_segmento(bars_desgaste_ant)
            agregar_etiquetas_segmento(bars_desgaste_sel, desgaste_ant)
            agregar_etiquetas_segmento(bars_reparaciones_ant)
            agregar_etiquetas_segmento(bars_reparaciones_sel, reparaciones_ant)
            
            # ✅ TÍTULO COMO EL GRÁFICO 2
            ax1.set_title(f"DEFECTOS POR TRAMO DESGASTE VS REPARACIONES- \n{fecha_anterior} vs {fecha_seleccionada}\nModelo: {model}", 
                        fontsize=14, fontweight='bold', pad=15)
            
            ax1.set_xlabel("Tramo", fontweight='bold')
            ax1.set_ylabel("Cantidad de Defectos", fontweight='bold')
            ax1.set_xticks(x)
            ax1.set_xticklabels([f'Tramo {t}' for t in tramos], rotation=45, ha='right')
            
            # ✅ LEYENDA COMO EL GRÁFICO 2
            ax1.legend([bars_desgaste_ant, bars_desgaste_sel, bars_reparaciones_ant, bars_reparaciones_sel],
                    [f'Desgaste {fecha_anterior}', f'Desgaste {fecha_seleccionada}',
                    f'Reparaciones {fecha_anterior}', f'Reparaciones {fecha_seleccionada}'],
                    bbox_to_anchor=(1.05, 1), loc='upper left')
            
            ax1.grid(axis='y', linestyle='--', alpha=0.6)
            
            # Ajustar límites del eje Y
            total_desgaste = [a+b for a,b in zip(desgaste_ant, desgaste_sel)]
            total_reparaciones = [a+b for a,b in zip(reparaciones_ant, reparaciones_sel)]
            max_val = max(max(total_desgaste), max(total_reparaciones)) if total_desgaste or total_reparaciones else 10
            
            ax1.set_ylim(0, max_val * 1.15)
            
            # ✅ TABLA DE DATOS COMO EL GRÁFICO 2
            ax2 = fig.add_subplot(gs[1])
            ax2.axis('off')  # Ocultar ejes
            
            # Preparar datos para la tabla
            tabla_datos = []
            for i, tramo in enumerate(tramos):
                fila = [
                    f'Tramo {tramo}',
                    desgaste_ant[i],
                    desgaste_sel[i],
                    reparaciones_ant[i],
                    reparaciones_sel[i],
                    total_desgaste[i],
                    total_reparaciones[i]
                ]
                tabla_datos.append(fila)
            
            # Crear la tabla
            column_labels = ['Tramo', f'Desgaste\n{fecha_anterior}', f'Desgaste\n{fecha_seleccionada}',
                            f'Reparaciones\n{fecha_anterior}', f'Reparaciones\n{fecha_seleccionada}',
                            'Total Desgaste', 'Total Reparaciones']
            
            table = ax2.table(cellText=tabla_datos,
                            colLabels=column_labels,
                            cellLoc='center',
                            loc='center',
                            bbox=[0, 0, 1, 1])
            
            # Formatear la tabla como el gráfico 2
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)
            
            # Estilo para la tabla
            for i, key in enumerate(table.get_celld().keys()):
                cell = table.get_celld()[key]
                if key[0] == 0:  # Encabezados
                    cell.set_facecolor('#4CAF50')
                    cell.set_text_props(weight='bold', color='white')
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
            
            db_session.close()
            print("✅ GRÁFICO 3 CREADO")
            return fig
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _export_pdf(self):
        """Exporta todos los gráficos actuales a un único PDF"""
        if not hasattr(self, 'figures') or not self.figures:
            print("⚠️ No hay gráficos para exportar.")
            return

        try:
            model = self.cmb_model.get() or "reporte"
            filename = f"Defectos_{model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            with PdfPages(filename) as pdf:
                for fig in self.figures:
                    pdf.savefig(fig, bbox_inches='tight')

            print(f"✅ Gráficos exportados correctamente a {filename}")

        except Exception as e:
            print(f"❌ Error al exportar PDF: {e}")

    def _grafico_distancias_fallas_por_tramo(self, model, fecha1, fecha2):
        """Genera gráfico de distancias de fallas por tramo con tabla - SIEMPRE para TODOS los tramos"""
        try:
            # Obtener sesión de base de datos
            db_session = Session(engine)
            historial_repo = HistorialRepository(db_session)
            
            # Obtener datos de distancias de fallas
            df = historial_repo.obtener_distancias_fallas(model, [fecha1, fecha2])
            
            if df.empty:
                return None
                
            # Obtener lista de tramos únicos ordenados por cantidad total de fallas
            tramos_totales = df.groupby('Tramo')['cantidad_fallas'].sum().sort_values(ascending=False)
            tramos_ordenados = tramos_totales.index.tolist()
            
            # Preparar datos para el gráfico
            datos = {}
            for tramo in tramos_ordenados:
                datos[tramo] = {
                    fecha1: {'Reparaciones': 0, 'Desgaste': 0},
                    fecha2: {'Reparaciones': 0, 'Desgaste': 0}
                }
                
            # Llenar los datos con las distancias
            for _, row in df.iterrows():
                tramo = row['Tramo']
                fecha = row['fecha']
                prediccion = row['prediccion']
                distancia = row['distancia_total']
                
                if tramo in datos and fecha in datos[tramo] and prediccion in datos[tramo][fecha]:
                    datos[tramo][fecha][prediccion] = distancia
            
            # Crear gráfico
            fig = Figure(figsize=(14, 8), dpi=100)
            ax = fig.add_subplot(111)
            
            # Configurar posiciones de las barras
            x = np.arange(len(tramos_ordenados))
            width = 0.35
            
            # Valores para cada fecha y tipo de defecto
            reparaciones_f1 = [datos[t][fecha1]['Reparaciones'] for t in tramos_ordenados]
            desgaste_f1 = [datos[t][fecha1]['Desgaste'] for t in tramos_ordenados]
            reparaciones_f2 = [datos[t][fecha2]['Reparaciones'] for t in tramos_ordenados]
            desgaste_f2 = [datos[t][fecha2]['Desgaste'] for t in tramos_ordenados]
            
            # Barras para la fecha 1 - Usando colores similares al gráfico original (verdes)
            bars1_rep = ax.bar(x - width/2, reparaciones_f1, width, 
                              label=f'{fecha1} - Reparaciones', color='lightgreen', alpha=0.8)
            bars1_des = ax.bar(x - width/2, desgaste_f1, width, bottom=reparaciones_f1,
                              label=f'{fecha1} - Desgaste', color='darkgreen', alpha=0.8)
            
            # Barras para la fecha 2 - Usando colores similares al gráfico original (verdes)
            bars2_rep = ax.bar(x + width/2, reparaciones_f2, width,
                              label=f'{fecha2} - Reparaciones', color='lightblue', alpha=0.8)
            bars2_des = ax.bar(x + width/2, desgaste_f2, width, bottom=reparaciones_f2,
                              label=f'{fecha2} - Desgaste', color='darkblue', alpha=0.8)
            
            # Configurar el gráfico
            ax.set_xlabel('Tramo (Ordenado por cantidad de fallas)')
            ax.set_ylabel('Distancia Total de Fallas [m]')
            ax.set_title(f'DISTANCIAS DE FALLAS POR TRAMO - {model}\n(Siempre muestra TODOS los tramos)')
            ax.set_xticks(x)
            ax.set_xticklabels([f'Tramo {t}' for t in tramos_ordenados], rotation=45, ha='right')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Añadir valores en las barras (solo si son significativos)
            def add_value_labels(bars, threshold=0.1):
                for bar in bars:
                    height = bar.get_height()
                    if height > threshold:
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + height/2,
                                f'{height:.1f}m', ha='center', va='center', fontsize=8,
                                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7))
            
            add_value_labels(bars1_rep)
            add_value_labels(bars1_des)
            add_value_labels(bars2_rep)
            add_value_labels(bars2_des)
            
            # Crear tabla con los datos
            tabla_datos = []
            for tramo in tramos_ordenados:
                fila = [
                    tramo,
                    f"{datos[tramo][fecha1]['Reparaciones']:.1f}",
                    f"{datos[tramo][fecha1]['Desgaste']:.1f}",
                    f"{datos[tramo][fecha2]['Reparaciones']:.1f}",
                    f"{datos[tramo][fecha2]['Desgaste']:.1f}"
                ]
                tabla_datos.append(fila)
            
            # Crear tabla debajo del gráfico
            column_labels = ['Tramo', f'Rep {fecha1}', f'Desg {fecha1}', f'Rep {fecha2}', f'Desg {fecha2}']
            
            table = ax.table(cellText=tabla_datos,
                            colLabels=column_labels,
                            cellLoc='center',
                            loc='bottom',
                            bbox=[0, -0.5, 1, 0.3])
            
            # Ajustar estilo de la tabla
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.2)
            
            # Ajustar el diseño para hacer espacio para la tabla
            fig.subplots_adjust(bottom=0.4)
            
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
            
            db_session.close()
            return fig
            
        except Exception as e:
            print(f"❌ Error generando gráfico de distancias por tramo: {e}")
            return None
        
    def _grafico_distancias_breaker_por_tramos(self, model, fecha1, fecha2):
        """Genera gráfico de distancias de breaker expuesto por tramos"""
        try:
            print(f"🔍 GRÁFICO 5 - INICIANDO (Distancias Breaker)")
            print(f"🔍 Fechas: {fecha1} vs {fecha2}")
            
            # Obtener sesión de base de datos
            db_session = Session(engine)
            historial_repo = HistorialRepository(db_session)
            
            # NORMALIZAR FECHAS primero
            if isinstance(fecha1, str):
                fecha1_normalizada = pd.to_datetime(fecha1).date()
            else:
                fecha1_normalizada = fecha1
                
            if isinstance(fecha2, str):
                fecha2_normalizada = pd.to_datetime(fecha2).date()
            else:
                fecha2_normalizada = fecha2
            
            # Obtener datos de breaker expuesto CON FECHAS NORMALIZADAS
            df = historial_repo.obtener_distancias_fallas(model, [fecha1_normalizada, fecha2_normalizada])
            
            if df.empty:
                print("❌ NO HAY DATOS para gráfico de breaker")
                db_session.close()
                return None
                
            print(f"📊 DATOS BREAKER OBTENIDOS: {len(df)} registros")
            
            # Obtener lista de tramos únicos ordenados
            tramos = sorted(df['Tramo'].unique())
            print(f"📈 TRAMOS ENCONTRADOS: {tramos}")
            
            # Preparar datos para el gráfico
            datos_distancia = {}
            datos_cantidad = {}
            
            for tramo in tramos:
                datos_distancia[tramo] = {
                    fecha1_normalizada: {'Reparaciones': 0, 'Desgaste': 0},
                    fecha2_normalizada: {'Reparaciones': 0, 'Desgaste': 0}
                }
                datos_cantidad[tramo] = {
                    fecha1_normalizada: {'Reparaciones': 0, 'Desgaste': 0},
                    fecha2_normalizada: {'Reparaciones': 0, 'Desgaste': 0}
                }
            
            # Llenar los datos
            for _, row in df.iterrows():
                tramo = row['Tramo']
                fecha_df = row['fecha']
                prediccion = row['prediccion']
                distancia = row['distancia_total']
                cantidad = row['cantidad_fallas']
                
                # Normalizar fecha del DataFrame
                if isinstance(fecha_df, str):
                    fecha_df = pd.to_datetime(fecha_df).date()
                
                if tramo in datos_distancia:
                    if fecha_df == fecha1_normalizada:
                        datos_distancia[tramo][fecha1_normalizada][prediccion] = distancia
                        datos_cantidad[tramo][fecha1_normalizada][prediccion] = cantidad
                    elif fecha_df == fecha2_normalizada:
                        datos_distancia[tramo][fecha2_normalizada][prediccion] = distancia
                        datos_cantidad[tramo][fecha2_normalizada][prediccion] = cantidad
            
            # Crear gráfico
            fig = Figure(figsize=(14, 8), dpi=100)
            ax = fig.add_subplot(111)
            
            # Configurar posiciones de las barras
            x = np.arange(len(tramos))
            width = 0.35
            
            # Valores para cada fecha y tipo de defecto (DISTANCIAS para altura de barras)
            reparaciones_f1_dist = [datos_distancia[t][fecha1_normalizada]['Reparaciones'] for t in tramos]
            desgaste_f1_dist = [datos_distancia[t][fecha1_normalizada]['Desgaste'] for t in tramos]
            reparaciones_f2_dist = [datos_distancia[t][fecha2_normalizada]['Reparaciones'] for t in tramos]
            desgaste_f2_dist = [datos_distancia[t][fecha2_normalizada]['Desgaste'] for t in tramos]
            
            # Valores para etiquetas (CANTIDAD de fallas)
            reparaciones_f1_cant = [datos_cantidad[t][fecha1_normalizada]['Reparaciones'] for t in tramos]
            desgaste_f1_cant = [datos_cantidad[t][fecha1_normalizada]['Desgaste'] for t in tramos]
            reparaciones_f2_cant = [datos_cantidad[t][fecha2_normalizada]['Reparaciones'] for t in tramos]
            desgaste_f2_cant = [datos_cantidad[t][fecha2_normalizada]['Desgaste'] for t in tramos]
            
            # Barras apiladas para cada fecha (ALTURA = distancias)
            bars1 = ax.bar(x - width/2, reparaciones_f1_dist, width, 
                        label=f'{fecha1_normalizada} - Reparaciones', 
                        color='gold', alpha=0.8)
            bars1_bottom = ax.bar(x - width/2, desgaste_f1_dist, width, 
                                bottom=reparaciones_f1_dist, 
                                label=f'{fecha1_normalizada} - Desgaste', 
                                color='orange', alpha=0.8)
            
            bars2 = ax.bar(x + width/2, reparaciones_f2_dist, width, 
                        label=f'{fecha2_normalizada} - Reparaciones', 
                        color='lightblue', alpha=0.8)
            bars2_bottom = ax.bar(x + width/2, desgaste_f2_dist, width, 
                                bottom=reparaciones_f2_dist, 
                                label=f'{fecha2_normalizada} - Desgaste', 
                                color='blue', alpha=0.8)
            
            # Configurar el gráfico
            ax.set_xlabel('Tramo', fontweight='bold', fontsize=12)
            ax.set_ylabel('BREAKER EXPUESTO EN [m]', fontweight='bold', fontsize=12)
            ax.set_title(f'BREAKER EXPUESTO POR TRAMOS - {model}\n{fecha1_normalizada} vs {fecha2_normalizada}', 
                        fontsize=14, fontweight='bold', pad=20)
            
            ax.set_xticks(x)
            ax.set_xticklabels([f'Tramo {t}' for t in tramos], rotation=45, ha='right')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(axis='y', linestyle='--', alpha=0.6)
            
            # Añadir etiquetas con CANTIDAD de fallas
            def add_quantity_labels(bars, quantities):
                for bar, quantity in zip(bars, quantities):
                    height = bar.get_height()
                    if height > 0 and quantity > 0:
                        ax.text(bar.get_x() + bar.get_width()/2, 
                            bar.get_y() + height/2,
                            f'{int(quantity)}', 
                            ha='center', va='center', fontsize=8,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7))
            
            add_quantity_labels(bars1, reparaciones_f1_cant)
            add_quantity_labels(bars1_bottom, desgaste_f1_cant)
            add_quantity_labels(bars2, reparaciones_f2_cant)
            add_quantity_labels(bars2_bottom, desgaste_f2_cant)
            
            # Crear tabla con CANTIDAD de fallas
            tabla_datos = []
            for tramo in tramos:
                total_f1 = (datos_cantidad[tramo][fecha1_normalizada]['Reparaciones'] + 
                        datos_cantidad[tramo][fecha1_normalizada]['Desgaste'])
                total_f2 = (datos_cantidad[tramo][fecha2_normalizada]['Reparaciones'] + 
                        datos_cantidad[tramo][fecha2_normalizada]['Desgaste'])
                
                fila = [tramo, f'{total_f1}', f'{total_f2}']
                tabla_datos.append(fila)
            
            # Crear tabla debajo del gráfico
            column_labels = ['Tramo', str(fecha1_normalizada), str(fecha2_normalizada)]
            
            table = ax.table(cellText=tabla_datos,
                            colLabels=column_labels,
                            cellLoc='center',
                            loc='bottom',
                            bbox=[0, -0.3, 1, 0.2])
            
            # Ajustar estilo de la tabla
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.2)
            
            # Ajustar el diseño para hacer espacio para la tabla
            fig.subplots_adjust(bottom=0.25)
            
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
            
            db_session.close()
            print("✅ GRÁFICO 5 CREADO (Distancias Breaker)")
            return fig
            
        except Exception as e:
            print(f"❌ Error generando gráfico de breaker expuesto por tramos: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def _load_fechas(self):
        """Carga las fechas de video disponibles para el modelo seleccionado"""
        model = self.cmb_model.get()
        if not model:
            return
            
        try:
            # Obtener sesión de base de datos
            db_session = Session(engine)
            historial_repo = HistorialRepository(db_session)
            
            # Obtener fechas únicas de video para el modelo
            fechas = historial_repo.obtener_fechas_video_por_modelo(model)
            
            # Ordenar fechas de más reciente a más antigua
            fechas.sort(reverse=True)
            
            self.cmb_fecha['values'] = fechas
            if fechas:
                self.cmb_fecha.current(0)
                
            db_session.close()
        except Exception as e:
            print(f"Error cargando fechas: {e}")      

    def _obtener_fecha_anterior(self, model, tramo_seleccionado, fecha_actual):
        """Obtiene la fecha anterior más cercana a la fecha seleccionada"""
        try:
            # Obtener sesión de base de datos
            db_session = Session(engine)
            historial_repo = HistorialRepository(db_session)
            
            num_tramo = None
            if tramo_seleccionado != "Todos":
                num_tramo = int(tramo_seleccionado.split()[-1])
                
            # Obtener fecha anterior
            fecha_anterior = historial_repo.obtener_fecha_anterior(model, fecha_actual, num_tramo)
            
            db_session.close()
            return fecha_anterior
            
        except Exception as e:
            print(f"Error obteniendo fecha anterior: {e}")
            return None              

