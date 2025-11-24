import os
from tkinter import filedialog, messagebox
from views.date_popup import DatePopup
from services.maquina_service import MaquinaService
from utils.database_connection import get_db
import threading
from utils.tramo_utils import calcular_desplazamiento_inicial

class VideoProcessor:
    def __init__(self, main_window):
        self.main_window = main_window
        self.processing_thread = None
        # Obtener sesión de base de datos
        self.db_session = next(get_db())
        self.maquina_service = MaquinaService(self.db_session)
        
    def cargar_video(self):
        date_popup = DatePopup(self.main_window)
        fecha, maquina, tramo_inicial, distancia_siguiente = date_popup.show()
        
        if not self._validar_seleccion(fecha, maquina, tramo_inicial, distancia_siguiente):
            return
            
        # VERIFICAR QUE LOS LABELS EXISTEN ANTES DE USARLOS
        if hasattr(self.main_window, 'fecha_label') and self.main_window.fecha_label:
            self.main_window.fecha_label.config(text=f"Fecha: {fecha}")
        
        if hasattr(self.main_window, 'maquina_label') and self.main_window.maquina_label:
            self.main_window.maquina_label.config(text=f"Máquina: {maquina}")
        
        if not self._configurar_maquina(maquina):
            return
            
        self.main_window.maquina_seleccionada = maquina

        video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
        if not video_path:
            return
            
        self.main_window.video_path = video_path
        self.main_window.controller.boundingbox_service.set_modelo_correa(maquina)
        
        # Guardar metadata para posible uso posterior
        self.main_window.metadata_video = {
            'fecha': fecha,
            'maquina': maquina, 
            'tramo_inicial': tramo_inicial,  
            'distancia_siguiente': distancia_siguiente, 
            'video_path': video_path
        }

        # Mostrar loading
        self.main_window.show_loading("Iniciando procesamiento de video...")
        
        # Iniciar procesamiento en un hilo separado
        self.processing_thread = threading.Thread(
            target=self._procesar_video_en_hilo, 
            args=(video_path, tramo_inicial, distancia_siguiente),
            daemon=True
        )
        self.processing_thread.start()
        
    def _procesar_video_en_hilo(self, video_path, tramo_inicial, distancia_siguiente):
        """Procesa el video considerando el desplazamiento inicial"""
        try:
            print("DEBUG: Procesando video con desplazamiento inicial")
            print(f"DEBUG: tramo_inicial={tramo_inicial}, distancia_siguiente={distancia_siguiente}")
            # Calcular desplazamiento inicial
            tramos_info = getattr(self.main_window.treeview_manager, 'tramos_info', [])
            print(f"DEBUG: tramos_info={tramos_info}")
            desplazamiento = calcular_desplazamiento_inicial(
                tramo_inicial, 
                distancia_siguiente, 
                tramos_info  
            )
            
            self.main_window.desplazamiento_inicial = desplazamiento
            
            # Procesar video normalmente
            resultado_df = self.main_window.controller.cargar_datos_desde_fuente(
                "video", video_path, insertar_en_bd=False
            )
            
            print(f"DEBUG: Procesamiento completado. Resultados: {len(resultado_df) if resultado_df is not None else 0} defectos")
            
            # Pasar los resultados al hilo principal CON DESPLAZAMIENTO
            self.main_window.after(0, self._mostrar_resultados, resultado_df, video_path, desplazamiento)
            
        except Exception as e:
            print(f"DEBUG: Error en hilo: {e}")
            self.main_window.after(0, self._mostrar_error, str(e))
            
    # video_processor.py 
    def _mostrar_resultados(self, resultado_df, video_path, desplazamiento_inicial=0):
        """Muestra los resultados considerando el desplazamiento inicial"""
        try:
            if resultado_df is not None and not resultado_df.empty:
                # Añadir metadatos al DataFrame
                if hasattr(self.main_window, 'metadata_video'):
                    metadata = self.main_window.metadata_video
                    resultado_df['fecha_video'] = metadata['fecha']
                    #resultado_df['maquina'] = metadata['maquina']
                    #resultado_df['video_path'] = metadata['video_path']
                    # NO agregar tramo aquí, se calculará individualmente
                
                # Actualizar UI con los resultados
                self.main_window.navigation_manager.configurar_navegacion_video()
                self.main_window.treeview_manager.actualizar_treeview_con_defectos(resultado_df)
                # INSERTAR EN BASE DE DATOS CON CÁLCULO DE TRAMO
                try:
                    ids_insertados = self.main_window.controller.guardar_resultados_en_bd(
                        resultado_df,
                        imagenes_completas=getattr(self.main_window, 'imagenes_completas', None),
                        largo_total_correa=getattr(self.main_window, 'largo_total_correa', None),
                        tramos_info=getattr(self.main_window.treeview_manager, 'tramos_info', None),
                        secciones_correa=getattr(self.main_window, 'secciones_correa', 5),
                        desplazamiento_inicial=desplazamiento_inicial
                    )
                    
                    if ids_insertados:
                        print(f"✅ {len(ids_insertados)} registros insertados con tramos calculados")
                        resultado_df['id'] = ids_insertados
                    else:
                        print("❌ Error al insertar registros en la base de datos")
                        resultado_df['id'] = range(1, len(resultado_df) + 1)
                        
                except Exception as db_error:
                    print(f"❌ Error en inserción a BD: {db_error}")
                    resultado_df['id'] = range(1, len(resultado_df) + 1)
                
                messagebox.showinfo("Video procesado", 
                                f"Se detectaron {len(resultado_df)} defectos en {video_path}.\n\n"
                                f"Los datos han sido guardados automáticamente en la base de datos.")
            else:
                if resultado_df is None:
                    error_msg = "El procesamiento retornó None - posible error interno"
                    messagebox.showerror("Error", error_msg)
                elif resultado_df.empty:
                    info_msg = "No se detectaron defectos en el video"
                    messagebox.showinfo("Video procesado", info_msg)
                    
        except Exception as e:
            self._mostrar_error(str(e))
        finally:
            self.main_window.hide_loading()
            
    def _mostrar_error(self, error_msg):
        """Muestra error en UI"""
        try:
            self.main_window.hide_loading()
        except:
            pass
            
        messagebox.showerror("Error", f"Error procesando video: {error_msg}")
        import traceback
        print(f"Error completo: {traceback.format_exc()}")
    
    def _validar_seleccion(self, fecha, maquina, tramo_inicial, distancia_siguiente):
        """Valida la selección incluyendo los nuevos parámetros"""
        if not fecha:
            messagebox.showwarning("Selección Incompleta", "Debe seleccionar una fecha para cargar el video.")
            return False
        if not maquina:
            messagebox.showwarning("Selección Incompleta", "Debe seleccionar una máquina para cargar el video.")
            return False
        if tramo_inicial is None:
            messagebox.showwarning("Selección Incompleta", "Debe ingresar un tramo inicial válido.")
            return False
        if distancia_siguiente is None:
            messagebox.showwarning("Selección Incompleta", "Debe ingresar una distancia al siguiente tramo válida.")
            return False
        return True
        
    def _configurar_maquina(self, maquina):
        # Usar el nuevo servicio en lugar de DBOperations
        id_maquina = self.maquina_service.obtener_id_maquina_por_nombre(maquina)
        if id_maquina is None:
            messagebox.showerror("Error", f"No se encontró la máquina '{maquina}' en la base de datos.")
            return False
            
        direccion_maquina = self.maquina_service.obtener_direccion_maquina(id_maquina)
        if direccion_maquina is None:
            direccion_maquina = True
        self.main_window.correa_helper.actualizar_direccion(direccion_maquina)
        
        # Obtener largo total usando el servicio
        self.main_window.largo_total_correa = self.maquina_service.obtener_largo_total_por_tramos(id_maquina)
        if self.main_window.largo_total_correa <= 0:
            messagebox.showerror("Error", "La correa no tiene tramos definidos o su largo total es 0.")
            return False
            
        # Obtener número de tramos usando el servicio
        self.main_window.secciones_correa = self.maquina_service.contar_tramos_de_maquina(id_maquina)
        self.main_window.correa_helper.actualizar_tramos(self.main_window.secciones_correa)
        
        # OBTENER INFORMACIÓN DE TRAMOS Y GUARDARLA 
        try:
            # Obtener información detallada de los tramos
            tramos = self.maquina_service.obtener_tramos_por_maquina(id_maquina)
            tramos_info = [
                {'numero': tramo.numero_tramo, 'largo': tramo.largo_tramo or 0}
                for tramo in tramos
            ]
            # Guardar en el treeview manager
            self.main_window.treeview_manager.tramos_info = tramos_info
        except Exception as e:
            print(f"Error obteniendo información de tramos: {e}")
            self.main_window.treeview_manager.tramos_info = []
        
        return True