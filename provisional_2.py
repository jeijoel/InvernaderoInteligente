import tkinter as tk
from tkinter import messagebox, Frame, Label, Button, Scale, Canvas, Scrollbar, HORIZONTAL, VERTICAL
import threading
import time
import os

from Read_Data_JSON import SensorData
from interfaz_graficos import InterfazGraficas
from Controler import PicoTCPClient, Control
import Config
from CamaraWeb import abrir_camara
from Interfaz_Ticket_Conectado import ventana_tickets

def ventana_principal():
    # --- Paleta de Colores y Fuentes ---
    COLOR_FONDO = "#F7F7F7"
    COLOR_MARCO = "#FFFFFF"
    COLOR_PRINCIPAL = "#096B35"
    COLOR_SECUNDARIO = "#7AC35D"
    COLOR_TEXTO = "#000000"
    COLOR_TEXTO_INVERSO = "#FFFFFF"
    COLOR_ALERTA = "#C0392B"

    FONT_TITULO = ("Arial", 14, "bold") # Reducido ligeramente para optimizar espacio
    FONT_NORMAL = ("Arial", 10) # Reducido ligeramente
    FONT_BOTON = ("Arial", 9, "bold") # Reducido ligeramente

    # --- Estado de la Aplicación (Variables) ---
    ultimo_ts_temp = None
    ultimo_ts_hum = None
    ultimo_ts_agua = None
    ultimo_ts_luz = None

    # Inicialización de sensores
    sensor_temp = SensorData("datos_sensores_json_separados", "temperatura_dht.json")
    sensor_hum = SensorData("datos_sensores_json_separados", "humedad_suelo.json")
    sensor_agua = SensorData("datos_sensores_json_separados", "nivel_agua.json")
    sensor_luz = SensorData("datos_sensores_json_separados", "fotocelda.json")

    # Conexión con Controladores
    #serial_control = Control('COM3')
    pico_host = '172.20.10.2'
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
    try:
        ventana.iconbitmap('./Imagenes/Interfaz.ico')
    except tk.TclError:
        print("Advertencia: No se encontró el archivo 'Interfaz.ico'.")

    # Centrar la ventana en la pantalla
    ancho_ventana = 420
    alto_ventana = 600 # Se mantiene el alto, pero con scrollbar se adapta
    x_pos = (ventana.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y_pos = (ventana.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana.geometry(f'{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}')

    # --- Funciones Lógicas (sin alterar su funcionamiento interno) ---
    def mostrar_ventana_graficos():
        carpeta = "datos_sensores_json_separados"
        InterfazGraficas(ventana, carpeta)

    def actualizar_intervalo(valor):
        nonlocal intervalo_datos
        intervalo_datos = int(valor)
        print(f"Intervalo de toma de datos: {intervalo_datos}s, se guardara en el config.json")
        config = Config.Configuracion()
        config.escribir_config(intervalo_datos)

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
        command, text_estado, text_boton = ("M2_OFF", "Cerrado", "Abrir Techo") if estado_techo_abierto else ("M2_ON", "Abierto", "Cerrar Techo")
        pico_client.send_command(command)
        etiqueta_estado_techo.config(text=text_estado)
        boton_abrir_cerrar_techo.config(text=text_boton)
        estado_techo_abierto = not estado_techo_abierto

    def alternar_luz():
        nonlocal estado_luz_encendida
        command, text_estado, text_boton = ("LED_OFF", "Apagada", "Encender Luz") if estado_luz_encendida else ("LED_ON", "Encendida", "Apagar Luz")
        pico_client.send_command(command)
        etiqueta_valor_luz.config(text=text_estado)
        boton_encendido_apagado_manual_luz.config(text=text_boton)
        estado_luz_encendida = not estado_luz_encendida

    def alternar_ventilador():
        nonlocal estado_ventilador_encendido
        command, text_estado, text_boton = ("M1_OFF", "Apagado", "Encender") if estado_ventilador_encendido else ("M1_ON", "Encendido", "Apagar")
        pico_client.send_command(command)
        etiqueta_estado_ventilador.config(text=text_estado)
        boton_encendido_apagado_manual_ventilador.config(text=text_boton)
        estado_ventilador_encendido = not estado_ventilador_encendido

    def ciclo_luz():
        nonlocal ejecucion_activa_luz
        ejecucion_activa_luz = True
        while ejecucion_activa_luz:
            pico_client.send_command("LED_ON")
            time.sleep(intervalo_luz)
            if not ejecucion_activa_luz: break
            pico_client.send_command("LED_OFF")
            time.sleep(intervalo_luz)

    def ciclo_ventilador():
        nonlocal ejecucion_activa_ventilador
        ejecucion_activa_ventilador = True
        while ejecucion_activa_ventilador:
            pico_client.send_command("M1_ON")
            time.sleep(intervalo_ventilador)
            if not ejecucion_activa_ventilador: break
            pico_client.send_command("M1_OFF")
            time.sleep(intervalo_ventilador)

    def iniciar_ciclos():
        detener_ciclos()
        threading.Thread(target=ciclo_luz, daemon=True).start()
        threading.Thread(target=ciclo_ventilador, daemon=True).start()

    def detener_ciclos():
        nonlocal ejecucion_activa_luz, ejecucion_activa_ventilador
        ejecucion_activa_luz = False
        ejecucion_activa_ventilador = False

    def on_closing():
        #serial_control.cerrar()
        detener_ciclos()
        ventana.destroy()

    def verificar_y_notificar_datos():
        nonlocal ultimo_ts_temp, ultimo_ts_hum, ultimo_ts_agua, ultimo_ts_luz
        try:
            ts_temp, valor_temp = sensor_temp.read_line()
            temp_c = float(valor_temp)
            if ts_temp != ultimo_ts_temp:
                if temp_c < 15: messagebox.showwarning("Temperatura baja", f"La temperatura es muy baja: {temp_c} °C")
                elif temp_c > 35: messagebox.showwarning("Temperatura alta", f"La temperatura es muy alta: {temp_c} °C")
                ultimo_ts_temp = ts_temp
        except Exception as e:
            print(f"Error leyendo temperatura: {e}")

        try:
            ts_hum, estado_suelo = sensor_hum.read_line()
            if ts_hum != ultimo_ts_hum:
                if "Seco" in estado_suelo: messagebox.showwarning("Humedad baja", "El suelo está seco. Requiere riego.")
                ultimo_ts_hum = ts_hum
        except Exception as e:
            print(f"Error leyendo humedad: {e}")

    def actualizar_datos():
        try:
            _, temp = sensor_temp.read_line()
            etiqueta_valor_temperatura.config(text=f"{temp}°C")
        except:
            etiqueta_valor_temperatura.config(text="-- °C")
        try:
            _, humedad = sensor_hum.read_line()
            etiqueta_valor_humedad.config(text=f"{humedad}")
        except:
            etiqueta_valor_humedad.config(text="--")
        try:
            _, nivel_agua = sensor_agua.read_line()
            etiqueta_valor_agua.config(text=f"{nivel_agua}")
        except:
            etiqueta_valor_agua.config(text="--")
        try:
            _, iluminacion = sensor_luz.read_line()
            etiqueta_valor_luz.config(text=f"{iluminacion}")
        except:
            etiqueta_valor_luz.config(text="--")
        # Reprogramar la actualización
        ventana.after(intervalo_datos * 1000, actualizar_datos) # Se asegura de que se actualice al intervalo configurado

    def guardar_intervalos():
        pico_client.send_command(f"SET_INTERVAL_DATA:{intervalo_datos}")
        pico_client.send_command(f"SET_INTERVAL_LIGHT:{intervalo_luz}")
        pico_client.send_command(f"SET_INTERVAL_FAN:{intervalo_ventilador}")
        messagebox.showinfo("Guardado", "Los intervalos han sido enviados al dispositivo.")
        verificar_y_notificar_datos() # Esto podría ejecutarse después de cada actualización de datos, no al guardar intervalos.

    # --- Construcción de la Interfaz Gráfica ---

    # Usamos un Canvas con Scrollbar para hacer la interfaz adaptable si no cabe todo.
    canvas = Canvas(ventana, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar = Scrollbar(ventana, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = Frame(canvas, bg=COLOR_FONDO)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- Sección de Sensores ---
    sensores_frame = Frame(scrollable_frame, bg=COLOR_MARCO, bd=2, relief="groove")
    sensores_frame.pack(fill="x", padx=10, pady=(10, 5))
    Label(sensores_frame, text="Estado de Sensores", font=FONT_TITULO, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO, pady=5).pack(fill="x", ipady=2)
    grid_sensores = Frame(sensores_frame, bg=COLOR_MARCO, padx=10, pady=5)
    grid_sensores.pack(fill="x")
    grid_sensores.columnconfigure((0, 1), weight=1) # Las columnas de labels y valores tienen el mismo peso
    grid_sensores.columnconfigure(2, weight=0) # El botón de gráficas no se expande

    labels_sensores = ["Temperatura:", "Humedad Suelo:", "Nivel Agua:", "Iluminación:"]
    valores_sensores = []
    for i, txt in enumerate(labels_sensores):
        Label(grid_sensores, text=txt, font=FONT_NORMAL, bg=COLOR_MARCO, fg=COLOR_TEXTO).grid(row=i, column=0, sticky="w", pady=2)
        valor_label = Label(grid_sensores, text="--", font=FONT_NORMAL, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL)
        valor_label.grid(row=i, column=1, sticky="w", padx=5, pady=2)
        valores_sensores.append(valor_label)
    etiqueta_valor_temperatura, etiqueta_valor_humedad, etiqueta_valor_agua, etiqueta_valor_luz = valores_sensores
    Button(grid_sensores, text="Ver Gráficas", command=mostrar_ventana_graficos, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=2, rowspan=4, sticky="nsew", padx=5, pady=2)

    # --- Sección de Actuadores ---
    actuadores_frame = Frame(scrollable_frame, bg=COLOR_MARCO, bd=2, relief="groove")
    actuadores_frame.pack(fill="x", padx=10, pady=5)
    Label(actuadores_frame, text="Control Manual de Actuadores", font=FONT_TITULO, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO, pady=5).pack(fill="x", ipady=2)
    grid_actuadores = Frame(actuadores_frame, bg=COLOR_MARCO, padx=10, pady=5)
    grid_actuadores.pack(fill="x")
    grid_actuadores.columnconfigure((0, 1, 2), weight=1) # Todas las columnas tienen peso para distribuir el espacio

    # Techo
    Label(grid_actuadores, text="Techo:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=0, column=0, sticky="w", pady=2)
    etiqueta_estado_techo = Label(grid_actuadores, text="Cerrado", font=FONT_NORMAL, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL) # Eliminado width para que se ajuste
    etiqueta_estado_techo.grid(row=0, column=1, sticky="ew", pady=2)
    boton_abrir_cerrar_techo = Button(grid_actuadores, text="Abrir Techo", command=alternar_techo, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON)
    boton_abrir_cerrar_techo.grid(row=0, column=2, sticky="ew", padx=5, pady=2)

    # Luz
    Label(grid_actuadores, text="Luz:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=1, column=0, sticky="w", pady=2)
    # Reutilizamos etiqueta_valor_luz para mostrar el estado actual de la luz (manual o automático)
    etiqueta_valor_luz.grid(row=1, column=1, sticky="ew", pady=2) # Reposicionamos esta etiqueta aquí
    boton_encendido_apagado_manual_luz = Button(grid_actuadores, text="Encender Luz", command=alternar_luz, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON)
    boton_encendido_apagado_manual_luz.grid(row=1, column=2, sticky="ew", padx=5, pady=2)

    # Ventilador
    Label(grid_actuadores, text="Ventilador:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=2, column=0, sticky="w", pady=2)
    etiqueta_estado_ventilador = Label(grid_actuadores, text="Apagado", font=FONT_NORMAL, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL) # Eliminado width
    etiqueta_estado_ventilador.grid(row=2, column=1, sticky="ew", pady=2)
    boton_encendido_apagado_manual_ventilador = Button(grid_actuadores, text="Encender", command=alternar_ventilador, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON)
    boton_encendido_apagado_manual_ventilador.grid(row=2, column=2, sticky="ew", padx=5, pady=2)

    # --- Botón de Actualización Manual ---
    update_frame = Frame(scrollable_frame, bg=COLOR_FONDO)
    update_frame.pack(fill="x", padx=10, pady=5)
    Button(update_frame, text="Actualizar Datos de Sensores", command=actualizar_datos, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).pack(ipady=2, fill="x") # Ligeramente más compacto

    # --- Sección de Configuración de Intervalos ---
    intervalos_frame = Frame(scrollable_frame, bg=COLOR_MARCO, bd=2, relief="groove")
    intervalos_frame.pack(fill="x", padx=10, pady=5)
    Label(intervalos_frame, text="Configuración de Ciclos (segundos)", font=FONT_TITULO, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO, pady=5).pack(fill="x", ipady=2)
    grid_intervalos = Frame(intervalos_frame, bg=COLOR_MARCO, padx=10, pady=5)
    grid_intervalos.pack(fill="x")
    grid_intervalos.columnconfigure(1, weight=1)

    # Escalas de Intervalos
    Label(grid_intervalos, text="Intervalo Datos:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=0, column=0, sticky="w", pady=2)
    escala_intervalo = Scale(grid_intervalos, from_=5, to=60, orient=HORIZONTAL, command=actualizar_intervalo, resolution=5, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL, troughcolor=COLOR_SECUNDARIO, highlightthickness=0, length=200) # Añadido length
    escala_intervalo.set(intervalo_datos)
    escala_intervalo.grid(row=0, column=1, sticky="ew", padx=(5,0), pady=2)

    Label(grid_intervalos, text="Intervalo Luz:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=1, column=0, sticky="w", pady=2)
    escala_intervalo_luz = Scale(grid_intervalos, from_=15, to=120, orient=HORIZONTAL, command=actualizar_intervalo_luz, resolution=15, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL, troughcolor=COLOR_SECUNDARIO, highlightthickness=0, length=200)
    escala_intervalo_luz.set(intervalo_luz)
    escala_intervalo_luz.grid(row=1, column=1, sticky="ew", padx=(5,0), pady=2)

    Label(grid_intervalos, text="Intervalo Ventilador:", font=FONT_NORMAL, bg=COLOR_MARCO).grid(row=2, column=0, sticky="w", pady=2)
    escala_intervalo_ventilador = Scale(grid_intervalos, from_=15, to=120, orient=HORIZONTAL, command=actualizar_intervalo_ventilador, resolution=15, bg=COLOR_MARCO, fg=COLOR_PRINCIPAL, troughcolor=COLOR_SECUNDARIO, highlightthickness=0, length=200)
    escala_intervalo_ventilador.set(intervalo_ventilador)
    escala_intervalo_ventilador.grid(row=2, column=1, sticky="ew", padx=(5,0), pady=2)

    # --- Sección de Controles Principales ---
    controles_frame = Frame(scrollable_frame, bg=COLOR_FONDO)
    controles_frame.pack(fill="x", padx=10, pady=5)
    controles_frame.columnconfigure((0, 1, 2), weight=1)

    Button(controles_frame, text="Iniciar Ciclos", command=iniciar_ciclos, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=0, sticky="ew", padx=2, ipady=2)
    Button(controles_frame, text="Detener Ciclos", command=detener_ciclos, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=1, sticky="ew", padx=2, ipady=2)
    Button(controles_frame, text="Guardar Intervalos", command=guardar_intervalos, bg=COLOR_PRINCIPAL, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=2, sticky="ew", padx=2, ipady=2)

    # --- Botones Adicionales y de Salida ---
    bottom_frame = Frame(scrollable_frame, bg=COLOR_FONDO)
    bottom_frame.pack(fill="x", padx=10, pady=(5, 10))
    bottom_frame.columnconfigure((0, 1, 2), weight=1)

    Button(bottom_frame, text="Ver Cámara", command=abrir_camara, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=0, sticky="ew", padx=2, ipady=2)
    Button(bottom_frame, text="Tickets Soporte", command=ventana_tickets, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=1, sticky="ew", padx=2, ipady=2)
    Button(bottom_frame, text='Cerrar Aplicación', command=on_closing, bg=COLOR_ALERTA, fg=COLOR_TEXTO_INVERSO, font=FONT_BOTON).grid(row=0, column=2, sticky="ew", padx=2, ipady=2)

    # --- Inicio de la Aplicación ---
    ventana.protocol("WM_DELETE_WINDOW", on_closing)
    actualizar_datos() # Llama una vez al inicio para poblar los campos
    ventana.mainloop()

if __name__ == "__main__":
    ventana_principal()