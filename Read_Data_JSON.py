### La idea de este es para las lecturas de los datos de los sensores para posteriormente mostrarlos en los graficos y demas 
import json
import os

class SensorData:
    def __init__(self, folder, nombre_del_archivo):
        self.file_path = os.path.join(folder, nombre_del_archivo)

    def read_line(self):
        with open(self.file_path, "r", encoding="utf-8") as archivo:
            linea = archivo.readline().strip() # espacios 
            data = json.loads(linea)
            
            if data['type'] == "DHT_DATA":
                return data['timestamp'], data['temperatura_c'] #------> aca yo solo le puse que me diera la fecha y el dato del sensor poero se puede retornar otro valor de alguna clave del json
            elif data['type'] == "SOIL_MOISTURE_DATA":
                return data['timestamp'], data['estado_suelo']
            elif data['type'] == "WATER_LEVEL_DATA":
                return data['timestamp'], data['nivel_agua']
            



# instancias
# sensor = SensorData("datos_sensores_json_separados", "nivel_agua.json")
# sensor2 = SensorData("datos_sensores_json_separados", "humedad_suelo.json")
# sensor3 = SensorData("datos_sensores_json_separados", "temperatura_dht.json")
# datodelsensor = sensor2.read_line()
# print(datodelsensor)



