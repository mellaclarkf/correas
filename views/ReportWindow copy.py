# views/report_window.py
import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from utils.database_connection import DatabaseConnection
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

class ReportWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Análisis de Defectos por Correa")
        self.geometry("1100x700")  # Tamaño más adecuado
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
        
        # Botón para PDF
        btn_pdf = ttk.Button(control_frame, text="Exportar a PDF", command=self._export_pdf)
        btn_pdf.grid(row=0, column=4, padx=5)
        
        # Configurar pesos de columnas para centrar los elementos
        control_frame.columnconfigure(0, weight=0)
        control_frame.columnconfigure(1, weight=0)
        control_frame.columnconfigure(2, weight=0)
        control_frame.columnconfigure(3, weight=0)
        control_frame.columnconfigure(4, weight=1)  # Espacio flexible a la derecha
        
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

    def _load_models(self):
        """Carga los modelos de correa disponibles"""
        try:
            conn = DatabaseConnection().get_connection()
            models = pd.read_sql(
                "SELECT DISTINCT modelo_correa FROM historial WHERE modelo_correa IS NOT NULL ORDER BY modelo_correa", 
                conn
            )['modelo_correa'].tolist()
            
            self.cmb_model['values'] = models
            if models:
                self.cmb_model.current(0)
                self._load_tramos()
        except Exception as e:
            print(f"Error cargando modelos: {e}")

    def _load_tramos(self):
        """Carga los tramos disponibles para el modelo seleccionado"""
        model = self.cmb_model.get()
        if not model:
            return
            
        try:
            conn = DatabaseConnection().get_connection()
            tramos = pd.read_sql(
                "SELECT DISTINCT Tramo FROM historial WHERE modelo_correa = ? AND Tramo IS NOT NULL ORDER BY Tramo", 
                conn, params=(model,)
            )['Tramo'].tolist()
            
            tramos = sorted([int(t) for t in tramos if t is not None])
            tramos = [f"Tramo {t}" for t in tramos]
            
            self.cmb_tramo['values'] = ['Todos'] + tramos
            self.cmb_tramo.current(0)
        except Exception as e:
            print(f"Error cargando tramos: {e}")

    def _get_ultimas_fechas(self, conn, model, tramo_seleccionado):
        """Obtiene las dos últimas fechas con datos"""
        try:
            condicion_tramo = ""
            params = [model]
            
            if tramo_seleccionado != "Todos":
                num_tramo = int(tramo_seleccionado.split()[-1])
                condicion_tramo = "AND Tramo = ?"
                params.append(num_tramo)
            
            fechas_query = f"""
                SELECT DISTINCT DATE(fecha_registro) as fecha 
                FROM historial 
                WHERE modelo_correa = ? AND prediccion IS NOT NULL {condicion_tramo}
                ORDER BY fecha DESC 
                LIMIT 2
            """
            
            fechas_df = pd.read_sql(fechas_query, conn, params=params)
            fechas = fechas_df['fecha'].tolist()
            
            if not fechas:
                print("⚠️ No hay fechas disponibles para el modelo y tramo seleccionados.")
                return None, None
                
            ultima_fecha = fechas[0]
            penultima_fecha = fechas[1] if len(fechas) > 1 else None
            
            return ultima_fecha, penultima_fecha
            
        except Exception as e:
            print(f"Error obteniendo fechas: {e}")
            return None, None

    def _generate_report(self):
        """Genera los gráficos basados en la selección actual"""
        model = self.cmb_model.get()
        tramo_seleccionado = self.cmb_tramo.get()
        
        if not model:
            return
            
        if hasattr(self, 'last_model') and self.last_model != model:
            self._load_tramos()
        self.last_model = model

        try:
            conn = DatabaseConnection().get_connection()
            ultima_fecha, penultima_fecha = self._get_ultimas_fechas(conn, model, tramo_seleccionado)
            
            if not ultima_fecha:
                return

            # Limpiar gráficos anteriores
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
                
            self.figures = []

            # 1️⃣ Gráfico del último día
            fig1 = self._grafico_dia(model, ultima_fecha, conn, tramo_seleccionado)
            if fig1:
                self.figures.append(fig1)

            # 2️⃣ Gráfico comparativo de los dos últimos días
            if penultima_fecha:
                fig2 = self._grafico_comparativo_dos_dias(model, penultima_fecha, ultima_fecha, conn, tramo_seleccionado)
                if fig2:
                    self.figures.append(fig2)
                    
                # 3️⃣ Gráfico comparativo: Reparaciones vs Desgaste por tramos
                fig3 = self._grafico_reparaciones_vs_desgaste_por_tramos(model, penultima_fecha, ultima_fecha, conn)
                if fig3:
                    self.figures.append(fig3)

                # 4️⃣ Gráfico de distancias de fallas por tramo (SIEMPRE para TODOS los tramos)
                fig4 = self._grafico_distancias_fallas_por_tramo(model, penultima_fecha, ultima_fecha, conn)
                if fig4:
                    self.figures.append(fig4)    
           

        except Exception as e:
            print(f"❌ Error generando gráficos: {e}")

    def _grafico_dia(self, model, fecha, conn, tramo_seleccionado):
        """Genera gráfico de barras simple con los defectos del último día"""
        condicion_tramo = ""
        params = [model, fecha]
        
        if tramo_seleccionado != "Todos":
            num_tramo = int(tramo_seleccionado.split()[-1])
            condicion_tramo = "AND Tramo = ?"
            params.append(num_tramo)
            
        query = f"""
            SELECT prediccion, COUNT(*) as cantidad
            FROM historial
            WHERE modelo_correa = ? AND DATE(fecha_registro) = ? {condicion_tramo}
            GROUP BY prediccion
            ORDER BY cantidad DESC
        """
        
        df = pd.read_sql(query, conn, params=params)
        df = df[df['prediccion'].notna()]

        if df.empty:
            return None

        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)

        x_pos = np.arange(len(df['prediccion']))
        bars = ax.bar(x_pos, df['cantidad'], color='skyblue')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                    f'{int(height)}', ha='center', va='bottom')

        ax.set_title(f"DEFECTOS - {fecha}", fontsize=14, pad=15)
        ax.set_xlabel("Tipo de Defecto")
        ax.set_ylabel("Cantidad")
        ax.set_ylim(0, max(df['cantidad']) + 5)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(df['prediccion'], rotation=45, ha='right')
        
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

        return fig

    def _grafico_comparativo_dos_dias(self, model, fecha1, fecha2, conn, tramo_seleccionado):
        """Genera gráfico comparativo entre dos fechas"""
        condicion_tramo = ""
        params = [model, fecha1, fecha2]
        
        if tramo_seleccionado != "Todos":
            num_tramo = int(tramo_seleccionado.split()[-1])
            condicion_tramo = "AND Tramo = ?"
            params.append(num_tramo)
            
        query = f"""
            SELECT DATE(fecha_registro) as fecha, prediccion, COUNT(*) as cantidad
            FROM historial
            WHERE modelo_correa = ? AND DATE(fecha_registro) IN (?, ?) {condicion_tramo}
            GROUP BY fecha, prediccion
            ORDER BY fecha, prediccion
        """
        
        df = pd.read_sql(query, conn, params=params)
        
        if df.empty:
            return None
            
        pivot = df.pivot_table(index='prediccion', columns='fecha', values='cantidad', fill_value=0)
        
        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        bar_width = 0.35
        indices = np.arange(len(pivot.index))
        
        bars1 = ax.bar(indices - bar_width/2, pivot[fecha1], bar_width, 
                      label=str(fecha1), color='skyblue', alpha=0.7)
        
        bars2 = ax.bar(indices + bar_width/2, pivot[fecha2], bar_width, 
                      label=str(fecha2), color='lightcoral', alpha=0.7)
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                            f'{int(height)}', ha='center', va='bottom')
        
        ax.set_title(f"COMPARATIVA: {fecha1} vs {fecha2}", fontsize=14, pad=15)
        ax.set_xlabel("Tipo de Defecto")
        ax.set_ylabel("Cantidad")
        ax.set_xticks(indices)
        ax.set_xticklabels(pivot.index, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
        
        return fig

    def _grafico_reparaciones_vs_desgaste_por_tramos(self, model, fecha1, fecha2, conn):
        """Genera gráfico comparativo de Reparaciones vs Desgaste por tramos"""
        try:
            query = """
                SELECT Tramo, DATE(fecha_registro) as fecha, prediccion, COUNT(*) as cantidad
                FROM historial
                WHERE modelo_correa = ? AND DATE(fecha_registro) IN (?, ?)
                AND prediccion IN ('Reparaciones', 'Desgaste')
                GROUP BY Tramo, fecha, prediccion
                ORDER BY Tramo, fecha
            """
            
            df = pd.read_sql(query, conn, params=(model, fecha1, fecha2))
            
            if df.empty:
                return None
                
            tramos = sorted(df['Tramo'].unique())
            
            datos = {}
            for tramo in tramos:
                datos[tramo] = {
                    fecha1: {'Reparaciones': 0, 'Desgaste': 0},
                    fecha2: {'Reparaciones': 0, 'Desgaste': 0}
                }
                
            for _, row in df.iterrows():
                tramo = row['Tramo']
                fecha = row['fecha']
                prediccion = row['prediccion']
                cantidad = row['cantidad']
                
                if tramo in datos and fecha in datos[tramo] and prediccion in datos[tramo][fecha]:
                    datos[tramo][fecha][prediccion] = cantidad
            
            fig = Figure(figsize=(12, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            x = np.arange(len(tramos))
            width = 0.35
            
            reparaciones_f1 = [datos[t][fecha1]['Reparaciones'] for t in tramos]
            desgaste_f1 = [datos[t][fecha1]['Desgaste'] for t in tramos]
            reparaciones_f2 = [datos[t][fecha2]['Reparaciones'] for t in tramos]
            desgaste_f2 = [datos[t][fecha2]['Desgaste'] for t in tramos]
            
            bars1_rep = ax.bar(x - width/2, reparaciones_f1, width, label=f'{fecha1} - Reparaciones', color='gold')
            bars1_des = ax.bar(x - width/2, desgaste_f1, width, bottom=reparaciones_f1, 
                              label=f'{fecha1} - Desgaste', color='orange')
            
            bars2_rep = ax.bar(x + width/2, reparaciones_f2, width, label=f'{fecha2} - Reparaciones', color='lightgreen')
            bars2_des = ax.bar(x + width/2, desgaste_f2, width, bottom=reparaciones_f2, 
                              label=f'{fecha2} - Desgaste', color='darkgreen')
            
            ax.set_xlabel('Tramo')
            ax.set_ylabel('Cantidad de Defectos')
            ax.set_title('Reparaciones vs Desgaste por Tramos')
            ax.set_xticks(x)
            ax.set_xticklabels([f'Tramo {t}' for t in tramos], rotation=45, ha='right')
            ax.legend()
            
            def add_value_labels(bars):
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + height/2,
                                f'{int(height)}', ha='center', va='center', fontsize=8)
            
            add_value_labels(bars1_rep)
            add_value_labels(bars1_des)
            add_value_labels(bars2_rep)
            add_value_labels(bars2_des)
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
            
            return fig
            
        except Exception as e:
            print(f"❌ Error generando gráfico Reparaciones vs Desgaste: {e}")
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

    def _grafico_distancias_fallas_por_tramo(self, model, fecha1, fecha2, conn):
        """Genera gráfico de distancias de fallas por tramo con tabla - SIEMPRE para TODOS los tramos"""
        try:
            query = """
                SELECT 
                    Tramo, 
                    DATE(fecha_registro) as fecha, 
                    prediccion, 
                    SUM(ABS(eje_y2 - eje_y)) as distancia_total,
                    COUNT(*) as cantidad_fallas
                FROM historial
                WHERE modelo_correa = ? 
                AND DATE(fecha_registro) IN (?, ?)
                AND prediccion IN ('Reparaciones', 'Desgaste')
                AND eje_y IS NOT NULL 
                AND eje_y2 IS NOT NULL
                GROUP BY Tramo, fecha, prediccion
                ORDER BY cantidad_fallas DESC
            """
            
            df = pd.read_sql(query, conn, params=(model, fecha1, fecha2))
            
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
                    if height > threshold:  # Solo mostrar valores mayores al threshold
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
            
            return fig
            
        except Exception as e:
            print(f"❌ Error generando gráfico de distancias por tramo: {e}")
            return None
        
