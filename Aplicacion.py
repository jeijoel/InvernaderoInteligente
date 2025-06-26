import tkinter as tk
from tkinter import messagebox, Frame, Label, Button, Scale, Canvas
import threading
import time
import os
# Estas son importaciones de tus propios módulos, asegúrate de que estén disponibles
from Read_Data_JSON import SensorData
from interfaz_graficos import InterfazGraficas
from Controler import PicoTCPClient
import Config
from CamaraWeb import abrir_camara
from Interfaz_Ticket_Conectado import ventana_tickets

def ventana_principal():
    # --- Colores y Fuentes ---
    COLOR_FONDO = "#F7F7F7"
    COLOR_MARCO = "#FFFFFF"
    COLOR_PRINCIPAL = "#096B35"
    COLOR_SECUNDARIO = "#7AC35D"
    COLOR_TEXTO = "#000000"
    COLOR_TEXTO_INVERSO = "#FFFFFF"

    FONT_TITULO = ("Arial", 16, "bold")
    FONT_NORMAL = ("Arial", 12)
    FONT_BOTON = ("Arial", 10, "bold")

    # --- Estado de la Aplicación (Variables) ---
    ultimo_ts_temp = None
    ultimo_ts_hum = None
    ultimo_ts_agua = None
    ultimo_ts_luz = None

    # Inicialización de sensores (simulado si los archivos no existen)
    try:
        sensor_temp = SensorData("datos_sensores_json_separados", "temperatura_dht.json")
        sensor_hum = SensorData("datos_sensores_json_separados", "humedad_suelo.json")
        sensor_agua = SensorData("datos_sensores_json_separados", "nivel_agua.json")
        sensor_luz = SensorData("datos_sensores_json_separados", "fotocelda.json")
    except Exception as e:
        print(f"Error inicializando sensores: {e}. Se usarán valores por defecto.")
        # Mock objects para que la UI no falle
        class MockSensor:
            def read_line(self): return (None, "--")
        sensor_temp = sensor_hum = sensor_agua = sensor_luz = MockSensor()

<<<<<<< HEAD

    # Conexión con el controlador
    pico_host = '192.168.100.104'
=======
    serial_control = Control('COM3')
    pico_host = '172.20.10.2'
>>>>>>> 0dc9b44e19621928faa8b93da611ecb9587ebe49
    pico_port = 1234
    pico_client = PicoTCPClient(pico_host, pico_port)

    # Estado inicial de los actuadores
    estado_techo_abierto = False
    estado_luz_encendida = False
    estado_ventilador_encendido = False
    ejecucion_activa_luz = False
    ejecucion_activa_ventilador = False

    # Intervalos por defecto
    intervalo_datos = 5
    intervalo_luz = 15
    intervalo_ventilador = 15

    # --- Configuración de la Ventana Principal ---
    ventana = tk.Tk()
    ventana.title('Panel de Control del Invernadero')
    ventana.config(bg=COLOR_FONDO)
    ventana.iconbitmap('./Imagenes/Interfaz.ico')

    # Centrar la ventana en la pantalla
    ancho_ventana = 900
    alto_ventana = 750
    x_pos = (ventana.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y_pos = (ventana.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana.geometry(f'{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}')
    ventana.resizable(False, False)

    # --- Funciones Lógicas (sin cambios en su interior) ---
    def mostrar_ventana_graficos():
        carpeta = "datos_sensores_json_separados"
        InterfazGraficas(ventana, carpeta)

    def actualizar_intervalo(valor):
        nonlocal intervalo_datos
        intervalo_datos = int(valor)
<<<<<<< HEAD
        print(f"Intervalo de toma de datos: {intervalo_datos}s")
        # config = Config.Configuracion(intervalo=0)
        # config.escribir_config(intervalo_datos)
=======
        print(f"Intervalo de toma de datos: {intervalo_datos}s, se guardara en el config.json")
        config = Configuracion()
        config.escribir_config(intervalo_datos)
>>>>>>> 0dc9b44e19621928faa8b93da611ecb9587ebe49

    def actualizar_intervalo_luz(valor):
        nonlocal intervalo_luz
        intervalo_luz = int(valor)
        print(f"Intervalo de luz: {intervalo_luz}s")

    def actualizar_intervalo_ventilador(valor):
        nonlocal intervalo_ventilador
        intervalo_ventilador = int(valor)
        print(f"Intervalo de ventilador: {intervalo_ventilador}s")

    def alternar_techo():
        nonlocal estado_techo_abierto
        if estado_techo_abierto:
            pico_client.send_command("M2_OFF")
            etiqueta_estado_techo.config(text="Cerrado")
            boton_abrir_cerrar_techo.config(text="Abrir Techo")
        else:
            pico_client.send_command("M2_ON")
            etiqueta_estado_techo.config(text="Abierto")
            boton_abrir_cerrar_techo.config(text="Cerrar Techo")
        estado_techo_abierto = not estado_techo_abierto

    def alternar_luz():
        nonlocal estado_luz_encendida
        if estado_luz_encendida:
            pico_client.send_command("LED_OFF")
            etiqueta_estado_luz.config(text="Apagada")
            boton_encendido_apagado_manual_luz.config(text="Encender Luz")
        else:
            pico_client.send_command("LED_ON")
            etiqueta_estado_luz.config(text="Encendida")
            boton_encendido_apagado_manual_luz.config(text="Apagar Luz")
        estado_luz_encendida = not estado_luz_encendida

    def alternar_ventilador():
        nonlocal estado_ventilador_encendido
        if estado_ventilador_encendido:
            pico_client.send_command("M1_OFF")
            etiqueta_estado_ventilador.config(text="Apagado")
            boton_encendido_apagado_manual_ventilador.config(text="Encender")
        else:
            pico_client.send_command("M1_ON")
            etiqueta_estado_ventilador.config(text="Encendido")
            boton_encendido_apagado_manual_ventilador.config(text="Apagar")
        estado_ventilador_encendido = not estado_ventilador_encendido

    def ciclo_luz():
        nonlocal ejecucion_activa_luz
        ejecucion_activa_luz = True
        while ejecucion_activa_luz:
            print("Ciclo Luz: ON")
            pico_client.send_command("LED_ON")
            time.sleep(intervalo_luz)
            if not ejecucion_activa_luz: break
            print("Ciclo Luz: OFF")
            pico_client.send_command("LED_OFF")
            time.sleep(intervalo_luz)

    def ciclo_ventilador():
        nonlocal ejecucion_activa_ventilador
        ejecucion_activa_ventilador = True
        while ejecucion_activa_ventilador:
            print("Ciclo Ventilador: ON")
            pico_client.send_command("M1_ON")
            time.sleep(intervalo_ventilador)
            if not ejecucion_activa_ventilador: break
            print("Ciclo Ventilador: OFF")
            pico_client.send_command("M1_OFF")
            time.sleep(intervalo_ventilador)

    def iniciar_ciclos():
        detener_ciclos()
        print("Iniciando ciclos...")
        threading.Thread(target=ciclo_luz, daemon=True).start()
        threading.Thread(target=ciclo_ventilador, daemon=True).start()

    def detener_ciclos():
        nonlocal ejecucion_activa_luz, ejecucion_activa_ventilador
        print("Deteniendo ciclos...")
        ejecucion_activa_luz = False
        ejecucion_activa_ventilador = False

    def on_closing():
<<<<<<< HEAD
        detener_ciclos()
        pico_client.close()
        ventana.destroy()
=======
        serial_control.cerrar()
        detener_ciclo()
        ventana_principal.destroy()
>>>>>>> 0dc9b44e19621928faa8b93da611ecb9587ebe49

    def verificar_y_notificar_datos():
        nonlocal ultimo_ts_temp, ultimo_ts_hum, ultimo_ts_agua, ultimo_ts_luz
        # (Lógica de notificación sin cambios)
        try:
            ts_temp, valor_temp = sensor_temp.read_line()
            temp_c = float(valor_temp)
            if ts_temp != ultimo_ts_temp:
                if temp_c < 15: messagebox.showwarning("Temperatura baja", f"La temperatura es muy baja: {temp_c} °C")
                elif temp_c > 35: messagebox.showwarning("Temperatura alta", f"La temperatura es muy alta: {temp_c} °C")
                ultimo_ts_temp = ts_temp
        except (ValueError, TypeError): pass
        except Exception as e: print(f"Error notificando temperatura: {e}")

    def actualizar_datos_display():
        try:
            _, temp = sensor_temp.read_line()
            etiqueta_valor_temperatura.config(text=f"{temp}°C")
        except: etiqueta_valor_temperatura.config(text="-- °C")
        try:
            _, humedad = sensor_hum.read_line()
            etiqueta_valor_humedad.config(text=f"{humedad}")
        except: etiqueta_valor_humedad.config(text="-- %")
        try:
            _, nivel_agua = sensor_agua.read_line()
            etiqueta_valor_agua.config(text=f"{nivel_agua}")
        except: etiqueta_valor_agua.config(text="--")
        try:
            _, iluminacion = sensor_luz.read_line()
            etiqueta_valor_luz.config(text=f"{iluminacion}")
        except: etiqueta_valor_luz.config(text="--")
        ventana.after(5000, actualizar_datos_display) # Auto-actualiza cada 5s

    def guardar_intervalos():
        print("Guardando intervalos en el dispositivo...")
        pico_client.send_command(f"SET_INTERVAL_DATA:{intervalo_datos}")
        pico_client.send_command(f"SET_INTERVAL_LIGHT:{intervalo_luz}")
        pico_client.send_command(f"SET_INTERVAL_FAN:{intervalo_ventilador}")
        messagebox.showinfo("Guardado", "Los intervalos han sido enviados al dispositivo.")
        verificar_y_notificar_datos()

    # --- Construcción de la Interfaz Gráfica ---
    
    # Marco principal que contiene todo
    main_frame = Frame(ventana, bg=COLOR_FONDO, padx=20, pady=20)
    main_frame.pack(expand=True, fill="both")

    # --- Sección de Sensores ---
    sensores_frame = Frame(main_frame, bg=COLOR_MARCO, bd=2, relief="groove")
    sensores_frame.pack(fill="x", pady=(0, 10))
    Label(sensores_frame, text="Estado de Sensores", font=FONT_TITULO, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO).pack(fill="x", ipady=5)

    grid_sensores = Frame(sensores_frame, bg=COLOR_MARCO, padx=10, pady=10)
    grid_sensores.pack(fill="x")
    grid_sensores.columnconfigure((0, 1, 2, 3), weight=1)

    # Widgets de sensores
    labels_sensores = ["Temperatura:", "Humedad Suelo:", "Nivel Agua:", "Iluminación:"]
    valores_sensores = []
    for i, txt in enumerate(labels_sensores):
        Label(grid_sensores, text=txt, font=FONT_NORMAL, bg=COLOR_MARCO, fg=COLOR_TEXTO).grid(row=i, column=0, sticky="w", pady=5)
        valor_label = Label(grid_sensores, text="--", font=FONT_NORMAL, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL)
        valor_label.grid(row=i, column=1, sticky="w", pady=5)
        valores_sensores.append(valor_label)

    etiqueta_valor_temperatura, etiqueta_valor_humedad, etiqueta_valor_agua, etiqueta_valor_luz = valores_sensores
    Button(grid_sensores, text="Ver Gráficas", command=mostrar_ventana_graficos, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=2, rowspan=4, sticky="ns", padx=10)

    # --- Sección de Actuadores ---
    actuadores_frame = Frame(main_frame, bg=COLOR_MARCO, bd=2, relief="groove")
    actuadores_frame.pack(fill="x", pady=10)
    Label(actuadores_frame, text="Control Manual de Actuadores", font=FONT_TITULO, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO).pack(fill="x", ipady=5)

    grid_actuadores = Frame(actuadores_frame, bg=COLOR_MARCO, padx=10, pady=10)
    grid_actuadores.pack(fill="x")
    grid_actuadores.columnconfigure((0, 1, 2), weight=1)

    # Techo
    Label(grid_actuadores, text="Techo:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=0, column=0, sticky="w", pady=5)
    etiqueta_estado_techo = Label(grid_actuadores, text="Cerrado", font=FONT_NORMAL, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL)
    etiqueta_estado_techo.grid(row=0, column=1)
    boton_abrir_cerrar_techo = Button(grid_actuadores, text="Abrir Techo", command=alternar_techo, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON)
    boton_abrir_cerrar_techo.grid(row=0, column=2, sticky="ew", padx=10)

    # Luz
    Label(grid_actuadores, text="Luz:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=1, column=0, sticky="w", pady=5)
    etiqueta_estado_luz = Label(grid_actuadores, text="Apagada", font=FONT_NORMAL, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL)
    etiqueta_estado_luz.grid(row=1, column=1)
    boton_encendido_apagado_manual_luz = Button(grid_actuadores, text="Encender Luz", command=alternar_luz, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON)
    boton_encendido_apagado_manual_luz.grid(row=1, column=2, sticky="ew", padx=10)

    # Ventilador
    Label(grid_actuadores, text="Ventilador:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=2, column=0, sticky="w", pady=5)
    etiqueta_estado_ventilador = Label(grid_actuadores, text="Apagado", font=FONT_NORMAL, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL)
    etiqueta_estado_ventilador.grid(row=2, column=1)
    boton_encendido_apagado_manual_ventilador = Button(grid_actuadores, text="Encender", command=alternar_ventilador, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON)
    boton_encendido_apagado_manual_ventilador.grid(row=2, column=2, sticky="ew", padx=10)

    # --- Sección de Configuración de Intervalos ---
    intervalos_frame = Frame(main_frame, bg=COLOR_MARCO, bd=2, relief="groove")
    intervalos_frame.pack(fill="x", pady=10)
    Label(intervalos_frame, text="Configuración de Ciclos (segundos)", font=FONT_TITULO, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO).pack(fill="x", ipady=5)
    
    grid_intervalos = Frame(intervalos_frame, bg=COLOR_MARCO, padx=10, pady=10)
    grid_intervalos.pack(fill="x")
    grid_intervalos.columnconfigure(1, weight=1)

    # Escalas de Intervalos
    Label(grid_intervalos, text="Intervalo Datos:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=0, column=0, sticky="w", pady=5)
    escala_intervalo = Scale(grid_intervalos, from_=5, to=60, orient="horizontal", command=actualizar_intervalo, resolution=5, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL, troughcolor=COLOR_SECUNDARIO, highlightthickness=0)
    escala_intervalo.set(intervalo_datos)
    escala_intervalo.grid(row=0, column=1, sticky="ew")

    Label(grid_intervalos, text="Intervalo Luz:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=1, column=0, sticky="w", pady=5)
    escala_intervalo_luz = Scale(grid_intervalos, from_=15, to=120, orient="horizontal", command=actualizar_intervalo_luz, resolution=15, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL, troughcolor=COLOR_SECUNDARIO, highlightthickness=0)
    escala_intervalo_luz.set(intervalo_luz)
    escala_intervalo_luz.grid(row=1, column=1, sticky="ew")

    Label(grid_intervalos, text="Intervalo Ventilador:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=2, column=0, sticky="w", pady=5)
    escala_intervalo_ventilador = Scale(grid_intervalos, from_=15, to=120, orient="horizontal", command=actualizar_intervalo_ventilador, resolution=15, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL, troughcolor=COLOR_SECUNDARIO, highlightthickness=0)
    escala_intervalo_ventilador.set(intervalo_ventilador)
    escala_intervalo_ventilador.grid(row=2, column=1, sticky="ew")

    # --- Sección de Controles Principales ---
    controles_frame = Frame(main_frame, bg=COLOR_FONDO)
    controles_frame.pack(fill="x", pady=20)
    controles_frame.columnconfigure((0, 1, 2, 3), weight=1)

    # Botones de control
    Button(controles_frame, text="Iniciar Ciclos", command=iniciar_ciclos, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=0, sticky="ew", padx=5)
    Button(controles_frame, text="Detener Ciclos", command=detener_ciclos, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=1, sticky="ew", padx=5)
    Button(controles_frame, text="Guardar Intervalos", command=guardar_intervalos, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=2, sticky="ew", padx=5)
    
    # --- Botones Adicionales y de Salida ---
    bottom_frame = Frame(main_frame, bg=COLOR_FONDO)
    bottom_frame.pack(fill="x", side="bottom")
    bottom_frame.columnconfigure((0, 1, 2), weight=1)
    
    Button(bottom_frame, text="Ver Cámara", command=abrir_camara, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=0, sticky="ew", padx=5)
    Button(bottom_frame, text="Tickets Soporte", command=ventana_tickets, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=1, sticky="ew", padx=5)
    Button(bottom_frame, text='Cerrar Aplicación', command=on_closing, bg="#C0392B", fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=2, sticky="ew", padx=5)


    # --- Inicio de la Aplicación ---
    ventana.protocol("WM_DELETE_WINDOW", on_closing)
    actualizar_datos_display() # Inicia el primer ciclo de actualización de datos
    ventana.mainloop()

if __name__ == "__main__":
    ventana_principal()
