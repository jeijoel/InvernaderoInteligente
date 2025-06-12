import tkinter as tk
from tkinter import ttk
from Read_Data_JSON import SensorData
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import matplotlib.dates as mdates

class InterfazGraficas:
    def __init__(self, maestro, ruta_carpeta):
        self.ventana = tk.Toplevel(maestro)
        self.ventana.title("Gráficos de Sensores")
        self.ventana.geometry("640x360")  # Horizontal
        self.ventana.configure(bg='white')

        self.carpeta = ruta_carpeta
        self.sensor_seleccionado = tk.StringVar(value="Temperatura")
        self.rango_seleccionado = tk.StringVar(value="Últimos 5 minutos")

        self.sensor_seleccionado.trace_add("write", self.actualizar_grafica)
        self.rango_seleccionado.trace_add("write", self.actualizar_grafica)

        self.construir_interfaz()
        self.crear_grafica()

    def construir_interfaz(self):
        marco_superior = tk.Frame(self.ventana, bg='white')
        marco_superior.pack(fill=tk.X, pady=5)

        sensores = ["Temperatura", "Humedad Suelo", "Nivel Agua"]
        rangos = ["Últimos 5 minutos", "Última hora", "Último día"]

        ttk.Combobox(marco_superior, values=sensores, textvariable=self.sensor_seleccionado, state="readonly", width=18).pack(side="left", padx=5)
        ttk.Combobox(marco_superior, values=rangos, textvariable=self.rango_seleccionado, state="readonly", width=18).pack(side="left", padx=5)

        self.marco_grafica = tk.Frame(self.ventana, bg='white')
        self.marco_grafica.pack(fill=tk.BOTH, expand=True)

    def actualizar_grafica(self, *args):
        self.crear_grafica()

    def leer_datos_archivo(self, archivo):
        """Lee todos los datos del archivo JSON y los devuelve ordenados por marca de tiempo"""
        marcas_tiempo = []
        valores = []
        sensor = self.sensor_seleccionado.get()

        try:
            with open(f"{self.carpeta}/{archivo}", "r", encoding="utf-8") as f:
                lineas = f.readlines()
                
                for linea in lineas:
                    if not linea.strip():
                        continue
                    try:
                        datos = json.loads(linea.strip())
                        marca_tiempo = datetime.fromisoformat(datos["timestamp"])

                        if sensor == "Temperatura" and datos["type"] == "DHT_DATA":
                            valor = float(datos["temperatura_c"])
                        elif sensor == "Humedad Suelo" and datos["type"] == "SOIL_MOISTURE_DATA":
                            estado = datos["estado_suelo"].lower()
                            if "seco" in estado:
                                valor = 0
                            elif "húmedo" in estado:
                                valor = 1
                            elif "mojado" in estado:
                                valor = 2
                            else:
                                continue
                        elif sensor == "Nivel Agua" and datos["type"] == "WATER_LEVEL_DATA":
                            nivel = datos["nivel_agua"].lower()
                            if "vacío" in nivel:
                                valor = 0
                            elif "bajo" in nivel:
                                valor = 1
                            elif "medio" in nivel:
                                valor = 2
                            elif "lleno" in nivel:
                                valor = 3
                            else:
                                continue
                        else:
                            continue

                        marcas_tiempo.append(marca_tiempo)
                        valores.append(valor)
                        
                    except Exception as e:
                        print(f"Error parseando línea: {e}")
                        continue
                        
        except FileNotFoundError:
            print("Archivo no encontrado:", archivo)
            return [], []

        if marcas_tiempo and valores:
            datos_ordenados = sorted(zip(marcas_tiempo, valores), key=lambda x: x[0])
            marcas_tiempo, valores = zip(*datos_ordenados)
            marcas_tiempo = list(marcas_tiempo)
            valores = list(valores)

        return marcas_tiempo, valores

    def crear_grafica(self):
        for widget in self.marco_grafica.winfo_children():
            widget.destroy()

        configuracion_sensor = {
            "Temperatura": ("temperatura_dht.json", "Temperatura (°C)", "red"),
            "Humedad Suelo": ("humedad_suelo.json", "Estado del Suelo", "blue"),
            "Nivel Agua": ("nivel_agua.json", "Nivel de Agua", "green"),
        }

        sensor = self.sensor_seleccionado.get()
        archivo, etiqueta, color = configuracion_sensor[sensor]

        marcas_tiempo, valores = self.leer_datos_archivo(archivo)

        if not marcas_tiempo:
            tk.Label(self.marco_grafica, text="No hay datos disponibles.", bg="white").pack(pady=20)
            return

        ultimo_dato = max(marcas_tiempo)
        primer_dato = min(marcas_tiempo)

        rango = self.rango_seleccionado.get()
        if rango == "Últimos 5 minutos":
            desde = ultimo_dato - timedelta(minutes=5)
        elif rango == "Última hora":
            desde = ultimo_dato - timedelta(hours=1)
        elif rango == "Último día":
            desde = ultimo_dato - timedelta(days=1)
        else:
            desde = primer_dato

        desde = max(desde, primer_dato)

        tiempos_filtrados = []
        valores_filtrados = []
        for t, v in zip(marcas_tiempo, valores):
            if t >= desde:
                tiempos_filtrados.append(t)
                valores_filtrados.append(v)

        if not tiempos_filtrados:
            mensaje = f"No hay datos en el rango '{rango}'.\n"
            mensaje += f"Último dato disponible: {ultimo_dato.strftime('%d/%m/%Y %H:%M:%S')}\n"
            mensaje += f"Total de datos en archivo: {len(marcas_tiempo)}"
            tk.Label(self.marco_grafica, text=mensaje, bg="white", justify="center").pack(pady=20)
            return

        fig, ax = plt.subplots(figsize=(6, 2.2))

        ax.plot(tiempos_filtrados, valores_filtrados, marker='o', linestyle='-', color=color, markersize=4)
        ax.set_title(f"{etiqueta} - {rango}")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)

        if rango == "Últimos 5 minutos":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        elif rango == "Última hora":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))

        if sensor == "Nivel Agua":
            ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5, label="Lleno")
            ax.axhline(y=2, color='orange', linestyle='--', alpha=0.5, label="Medio")
            ax.axhline(y=1, color='red', linestyle='--', alpha=0.5, label="Bajo")
            ax.set_yticks([0, 1, 2, 3])
            ax.set_yticklabels(["Vacío", "Bajo", "Medio", "Lleno"])
            ax.legend(loc='upper right', fontsize=8)
        elif sensor == "Humedad Suelo":
            ax.set_yticks([0, 1, 2])
            ax.set_yticklabels(["Seco", "Húmedo", "Mojado"])

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.marco_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        total_datos = len(marcas_tiempo)
        datos_mostrados = len(tiempos_filtrados)
        
        if tiempos_filtrados:
            desde_str = min(tiempos_filtrados).strftime('%d/%m/%Y %H:%M:%S')
            hasta_str = max(tiempos_filtrados).strftime('%d/%m/%Y %H:%M:%S')
            info = f"Mostrando {datos_mostrados} de {total_datos} datos totales"
            info += f"\nRango: {desde_str} → {hasta_str}"
            info += f"\nÚltimo dato disponible: {ultimo_dato.strftime('%d/%m/%Y %H:%M:%S')}"
        else:
            info = f"No hay datos en este rango. Total disponibles: {total_datos}"

        etiqueta_info = tk.Label(self.marco_grafica, text=info, bg="white", font=("Arial", 8), justify="left")
        etiqueta_info.pack(pady=2)



