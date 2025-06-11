import serial
import threading
import time
import json
import os
from Config import Configuracion




class Control:
    def __init__(self, puerto, baud=115200):  #------> Aca el puerto es el que les digo que no borren de la interfaz, ya que el unico programa que se ejecutrara es la interfaz esto se ejecuta en un thread
        self.ser = serial.Serial(puerto, baud, timeout=1)
        self.running = True

        # Archivos JSON
        self.LOG_DIR = "datos_sensores_json_separados"
        self.DHT_TEMP_JSON_FILE = os.path.join(self.LOG_DIR, "temperatura_dht.json")
        self.SOIL_MOISTURE_JSON_FILE = os.path.join(self.LOG_DIR, "humedad_suelo.json")
        self.WATER_LEVEL_JSON_FILE = os.path.join(self.LOG_DIR, "nivel_agua.json")
        self.ERROR_LOG_FILE = os.path.join(self.LOG_DIR, "errores_sistema.log")

        self.thread = threading.Thread(target=self.leer_datos, daemon=True)
        self.thread.start()

    #### Escribir en Json ################################################################################

    def write_to_json_line(self, data_dict, file_path):
        print(f"Escribiendo en {file_path}: {data_dict}")
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data_dict) + "\n")

    def limpiar_buffer(self):
        while self.ser.in_waiting > 0:
            self.ser.readline()

    ### lee los datos ######################################################################################

    def leer_datos(self):
        contadorbuffer = 0
        Datalist = []
        print(f"Iniciando comunicador conectando a {self.ser.port}...")
        try:
            while self.running:
                config = Configuracion()
                intervalo = config.obtener_intervalo_medicion() ##----> Aqui es donde se define el intervalo, en la interfaz se debe hacer un boton que escriba en el JSON (config.json) 
                
                while self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()

                    if line:
                        contadorbuffer += 1
                        Datalist.append(line)
                        print(f"Recibido: {line}")
                        if contadorbuffer == 4:
                            for linea in Datalist:
                                try:
                                    parts = linea.split(",")
                                    data_type = parts[0]

        ## DHT
                                    if data_type == "DHT_DATA":
                                        data_dict = {
                                            "type": data_type,
                                            "timestamp": parts[1],
                                            "sensor_name": parts[2],
                                            "temperatura_c": parts[3].split(":")[1]
                                            
                                        }
                                        
        ## Humedad
                                        self.write_to_json_line(data_dict, self.DHT_TEMP_JSON_FILE)

                                    elif data_type == "SOIL_MOISTURE_DATA":
                                        data_dict = {
                                            "type": data_type,
                                            "timestamp": parts[1],
                                            "sensor_name": parts[2],
                                            "estado_suelo": parts[3].split(":")[1]
                                        }
                                        self.write_to_json_line(data_dict, self.SOIL_MOISTURE_JSON_FILE)
        ## nivel de agua
                                    elif data_type == "WATER_LEVEL_DATA":
                                        distancia_cm = float(parts[3].split(":")[1])
                                        nivel_agua = parts[4].split(":")[1]

                                        data_dict = {
                                            "type": data_type,
                                            "timestamp": parts[1],
                                            "sensor_name": parts[2],
                                            "distancia_cm": distancia_cm,
                                            "nivel_agua": nivel_agua
                                        }
                                        self.write_to_json_line(data_dict, self.WATER_LEVEL_JSON_FILE)
                                    
                                        ###################### ERRORES #######################333

                                    elif data_type in ["ERROR", "PICO_ERROR"]:
                                        with open(self.ERROR_LOG_FILE, 'a', encoding='utf-8') as f_err:
                                            f_err.write(line + "\n")
                                    else:
                                        print(f"Tipo de dato desconocido: {data_type} en línea: {line}")

                            

                                except Exception as e:
                                    print(f"Error al procesar línea: {line} - Error: {e}")

                
                            print(contadorbuffer)
                            contadorbuffer = 0
                            Datalist.clear()
                            self.limpiar_buffer()
                            time.sleep(intervalo) #-------------> Ese es el intervalo

                
        except Exception as e:
            print(f"\nError en hilo de lectura: {e}")




            ####################################   Enviar datos    ######################3333

    def enviar_comando(self, comando):  #-----> desde la GUI se llama a la clase de arriba con este metodo y le deben dar el comando para que esta funcion se lo env'ie a la raspi
        if self.ser.is_open:
            try:
                self.ser.write(f"{comando}\n".encode('utf-8'))
                print(f"Comando enviado: {comando}")

                #Errores
            except Exception as e:
                print(f"Error al enviar comando: {e}")
        else:
            print("Puerto serial no disponible.")

#def que cierra el puerto
    def cerrar(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()











