Version Python 3.12.11

Hasta aquí se ha realizado lo siguiente:
- Se ha guardado datos en tabla history
- Se ha realizado simulación de predicción
- Se ha guardado la simulación en tabla history
- Indicarle que la predicción se realice con los datos de refuerzo 
- Crear botón de reforzing
- Crear la simulación nuevamente al presionar reforzing extrayendo los datos modificados del visor.
- reubicación de imagen y sacar ruta de imagen
- Se ha Cargado Modelo PKL de Cristian y probado el video con las imágenes de defectos
	NOTA: el programa arroja error porque ahora ya no existe el train en este programa por lo que debe
	ser reemplazado por el código de Cristian
- Se agrega manejador de imagen para zoom y realización de rectángulos (no completo)
- Se agrega botón para reproducir video con:
	scroll para avanzar y retroceder video
	controles para avanzar y retroceder frame
	dibujar rectángulo con botón derecho
	guardar imágenes en carpeta
-*1ro Lo primero es que al seleccionar el rectángulo con el botón sobre el video, debería capturar el frame completo y el 	rectángulo dibujado con verde y esa imagen guardarla, lo que hace ahora es que guarda la imagen dibujada con el 	rectángulo.
-*2do. Esto entrega una pantalla con los defectos como se realizó en el helper de imagen, y con un botón que diga guardar 	o cancelar luego de elegir el defecto.
-*3ro El rectangulo dibujado en el video es agregado en el treeview 
-*4to. esa información debería ser agregada a treeview del main_windows.py, pero ojo, creo que debería llegar toda la 	información necesaria del video, esto es, 
		+nombre de la imagen, 
		+posiciones del rectangulo x1,y1,x2,y2, 
		+el tiempo al cual la imagen pertenece dentro del video, 
		+el tipo de defecto que eligió el usuario 
		+numero de frame que corresponde dentro del video, por ejemplo si el 		 video va dentro se pausó en en el minuto 2 para dibujar el rectangulo y los frame son de 5 segundos, 			 indicar que el frame es el numero 25 dentro del video. 
		+tambien devolver el tiempo total que dura el video analizado.
- Se redibujará defecto al seleccionar el treeview
- Se agregan menú contextuales al treeview pero sin lógica de negocio
- Se agregan menú cotextuales solo a los agregados por el usuario (esto según el nombre name)
- Cambiar none por "Confirmar"
- Colocar en rectangulo el nombre
- Agregar pantalla para ingresar nombre de usuario y nombre de la correa, junto con un calendario
- Agregar settings de numero de frame, password y usuarios, otros....
- Zoom para seleccionar rectangulo en la imagen y seleccion de rectangulo no corrido
2.8
    - Se agrega dibujo para correa transportadora sin funcionalidad aún
2.9
    - Se crea tabla maquina 
    - Popup lee de tabla maquina
    - Dibujo de correa se ajusta a la cantidad de tramos indicada por la tabla
    - Se ubican botones arriba de treeview
3.0
    - Se agrega Reproductor de Imágenes como formato video
3.1
    - Se saca boton de reproductor de video antiguo, o mejor dicho se comentará en el main_windows, se mantiene helpers de video
    - Se Configura para que cargue las fotos solo cuando carga el video
    - Se Realiza Correa interactiva que Carga fotos por Tramo

3.2
    - Se Agrega Boton Rojo para que se pueda reproducir todas las fotos

3.3 
    - Se agregan los parámetros validados:
        + Tramo inicial
        + Distancia al inicio del siguiente tramo
    - Se realiza cambio de nombre a campo en BD de secciones a numero_tramos
    - Se realizó cambio de nombre de Maquina a Correa
    
3.4 
    - Se modifica tabla Máquina y se elimina numero_tramos como columna por problemas de actualización
    - Se agrega tabla tramos
    - Se modifica main_windows y date_popup
    - se agrega modificacion de tramos en settings

3.5
    - Se agrega visor de metros de la correa por tramo

3.6
    - Se agrega Entry para dirigirme directamente a la imagen seleccionada

3.7 - Se realiza interaccion entre treeview y el marcador de distancias

3.8 - Se actualiza el gráfico del treeview de forma que se seleccione la imagen en color verde.
    - Treeview con los encabezados correctos (Largo-Ancho-Distancia Correa)

3.9- Se arealiza nuevo dibujo de la Correa

4.1- Se agrega el largo al treeview

4.2.2 - - Se modificó color azul de correa.
    - Se modifico que que diga Correa y no Maquina en popup_date
    - Se modificó encabezado treeview [alto, largo, distancia]
    - Se modifico entry para ir a foto segun distancia para que pueda llegar a ella por esta via

4.3 - Se agrega el valor de tramos a la bd tabla historial
    - Se realizan ajustes para recibir el tramo en la BD

4.4 - Funcion Detectar adaptada
    - se limpia el codigo con respecto a funciones no cecesarias de entrenar (se elimina un archivo)
    - Se agrega el nombre real y la prediccion real a la bd

4.5 - Se realizan Arreglos a funcion Detectar.
    - data_load_factory es modificado.
    - Se genera el flujo de crear y borrar imagenes dentro de las carpetas "Imagenes", "trained_models\images" y 
        "trained_models\labels"
    - Se comienza adaptacion de Re-Entrenar

4.6 - Se integra Re-Entrenar.
        
4.7 - Cambiar las etiquetas en treeview (OK)
        Falta integrar las etiquetas de treeview a los txt 
        ventana de imagen tiene mal los botones de etiquetado
        CRUD de correas
        config de sentido correas (ok)
            - se agrega columna a tabla y se agrega combobox a ventana config(ok)
            - Se realiza el dibujo ok
            - Flecha sentido movimiento en el dibujo (ok)
        Barra o circulo que indique procesando
        EN Informe  
            - TABLA RESUMEN DE defectos
            - En grafico, sumatoria metros totales y lo mismo por tramo

4.8 -   EN Informe  
            - TABLA RESUMEN DE defectos (ok), ver que se puede mejorar
            - En grafico, sumatoria metros totales y lo mismo por tramo 


4.9.1_: - Se arregla gráfico
        - Se agrega eliminacion de carpetas
        - Se refactoriza código del main_windows (importante)
        - Se agrega barra de estado con hilos        

4.9.2: - Se genera Barra de estado con hilos en Re-cargar  

4.9.3: - Se genera los CRUD de  maquina y correa

4.9.4: - Se cambia todo a mysql

4.9.5: - Tramos corriendo segun distancia de tramos ok

4.9.6: - Insertando en tabla historial
       - Se agrega label con el acurrancy

4.9.7  - Se agrega comparacion de acurrancy en label 
       - Se inserta mejor acurrancy en tabla model

4.9.8 - Arreglado tema ejetutable cv2

4.9.9   - guardar foto con distancia de la seleccion del usuario
        - Fotos repetidas y arreglo del nombre en treeview
        - Poner etiqueta reentrenamiento, esto es, 
            * Se modifica archivo txt y bd en caso de existir un cambio de etiqueta
            * Se agrega al archivo txt y bd en caso de un defecto nuevo en una imagen con defecto.
        ??? * Para una imagen que no tiene defectos crea el txt e inserta en la tabla
        .... pero no tien el tramo, habria que calcularlo solamente
        .... Algo pasó con los tramos y su calculo

5.0.1   -Informe
        - Sacar dibujo que crea problemas
        - Pone variable de entorno services\boundingbox_service.py

------------


/factories                       # Fábricas de objetos y estrategias
    data_load_factory.py         # Retorna la estrategia de carga según tipo (exe, excel, txt, db)
    defect_factory.py            # Crea objetos Defect desde filas de base de datos

/models
    defect.py                    # Modelo de datos Defect con sus atributos

/controllers                     # Controladores que gestionan lógica entre vistas, servicios y modelos
    defect_controller.py         # Controla flujo de defectos entre UI y servicios (cargar, guardar, etiquetar, etc.)

/services                       # Servicios de acceso a base de datos y entrenamiento
    database_service.py          # Consultas e inserciones en defectos y historial
    training_service.py          # Simula entrenamiento de modelo (solo logs y espera)

/strategies                     # Estrategias de carga de datos, todas implementan DataLoaderStrategy
    data_loader_strategy.py      # Clase abstracta base para estrategias de carga
    db_data_loader_strategy.py   # Carga datos desde defectos en base de datos y crea Defects
    excel_data_loader_strategy.py# Carga desde Excel y guarda en defectos
    exe_data_loader_strategy.py  # Ejecuta un EXE y luego carga defectos desde base
    txt_data_loader_strategy.py  # Lee desde .txt y guarda en defectos

/utils
    image_loader.py              # Utilidad para cargar imágenes desde carpeta images

/images                         # Imágenes de ejemplo o prueba para visualización

/defectos.db                    # Base de datos SQLite con tablas: defects, historial

main.py                         # App principal con interfaz Tkinter para visualizar, etiquetar y entrenar
