import serial
import threading
import time
import json
import os
from Config import Configuracion
import socket 



# Esta clase gestiona la conexión TCP con la Raspberry Pi Pico W
class PicoTCPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.is_connected = False
        print(f"Cliente TCP inicializado para {self.host}:{self.port}")

    def connect(self):
        if self.is_connected and self.sock:
            # print("Ya conectado al Pico W.") # Puedes descomentar para depurar
            return True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5) # Establece un timeout de 5 segundos para la conexión y lectura
            self.sock.connect((self.host, self.port))
            self.is_connected = True
            print(f"Conectado exitosamente a {self.host}:{self.port}")
            return True
        


#########Errores#####
        except socket.timeout:
            print("Error: Tiempo de espera agotado al intentar conectar TCP.")
            self.is_connected = False
            self.sock = None
            return False
        except ConnectionRefusedError:
            print("Error: Conexión TCP rechazada. Asegúrate de que la Pico W esté encendida y el script TCP esté corriendo.")
            self.is_connected = False
            self.sock = None
            return False
        except Exception as e:
            print(f"Error general al conectar TCP con el Pico W: {e}")
            self.is_connected = False
            self.sock = None
            return False

    def send_command(self, command):
        if not self.is_connected or not self.sock:
            print("No conectado al Pico W para enviar comando TCP. Intentando reconectar...")
            if not self.connect():
                return None 

        try:
            # Los comandos deben terminar con '\n' y ser bytes
            self.sock.sendall(f"{command}\n".encode('utf-8'))
            print("Enviado")
        


        #####Errores#####
        except socket.timeout:
            print("Error: Tiempo de espera agotado al enviar/recibir comando TCP. Conexión perdida.")
            self.is_connected = False # Considerar la conexión perdida
            if self.sock: self.sock.close()
            self.sock = None
            return None
        except Exception as e:
            print(f"Error al enviar comando o recibir respuesta TCP: {e}. Conexión perdida.")
            self.is_connected = False # Considerar la conexión perdida
            if self.sock:
                self.sock.close()
            self.sock = None
            return None
        


    def send_command_interval(self, intervalo, objeto):

        def ciclo_objeto():
            comando_on = f"{objeto.upper()}_ON"
            comando_off = f"{objeto.upper()}_OFF"

            while True:
                resp_on = PicoTCPClient.send_command(comando_on)
                print(f"{objeto} ON → {resp_on}")
                time.sleep(intervalo)

                resp_off = PicoTCPClient.send_command(comando_off)
                print(f"{objeto} OFF → {resp_off}")
                time.sleep(intervalo)

        hilo = threading.Thread(target=ciclo_objeto)
        hilo.start()


###Cierre de conexion
    def disconnect(self):
        if self.sock and self.is_connected:
            try:
                self.sock.close()
                self.is_connected = False
                print("Desconectado del Pico W (TCP).")
            except Exception as e:
                print(f"Error al desconectar TCP: {e}")







class Control:
    def __init__(self, puerto, baud=115200):  #------> Aca el puerto es el que les digo que no borren de la interfaz, ya que el unico programa que se ejecutrara es la interfaz esto se ejecuta en un thread
        self.ser = serial.Serial(puerto, baud, timeout=1)
        self.running = True

        # Archivos JSON
        self.LOG_DIR = "datos_sensores_json_separados"
        self.DHT_TEMP_JSON_FILE = os.path.join(self.LOG_DIR, "temperatura_dht.json")
        self.SOIL_MOISTURE_JSON_FILE = os.path.join(self.LOG_DIR, "humedad_suelo.json")
        self.WATER_LEVEL_JSON_FILE = os.path.join(self.LOG_DIR, "nivel_agua.json")
        self.FOTOCELDA_FILE = os.path.join(self.LOG_DIR, "fotocelda.json")
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
                 ##----> Aqui es donde se define el intervalo, en la interfaz se debe hacer un boton que escriba en el JSON (config.json) 
                
                while self.ser.in_waiting > 0:
                    config = Configuracion()
                    intervalo = config.obtener_intervalo_medicion()
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
            ####Fotocelda
                                    elif data_type == "Fotocelda_Sensor":

                                        data_dict = {
                                            "type": data_type,
                                            "timestamp": parts[1],
                                            "iluminacion": parts[3].split(":")[1]
                                        }
                                        self.write_to_json_line(data_dict, self.FOTOCELDA_FILE)
                                    
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


   

#def que cierra el puerto
    def cerrar(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()











