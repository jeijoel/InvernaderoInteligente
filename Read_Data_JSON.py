### La idea de este es para las lecturas de los datos de los sensores para posteriormente mostrarlos en los graficos y demas 
import json
import os

class SensorData:
    def __init__(self, folder, nombre_del_archivo):
        self.file_path = os.path.join(folder, nombre_del_archivo)

    def read_line(self):
        with open(self.file_path, "r", encoding="utf-8") as archivo:
            linea = archivo.readline().strip()
            data = json.loads(linea)

            if data['type'] == "DHT_DATA":
                return data['timestamp'], data['temperatura_c']
            elif data['type'] == "SOIL_MOISTURE_DATA":
                return data['timestamp'], data['estado_suelo']
            elif data['type'] == "WATER_LEVEL_DATA":
                return data['timestamp'], data['nivel_agua']
            elif data['type'] == "Fotocelda_Sensor":
                return data['timestamp'], data['iluminacion']


# instancias
# sensor = SensorData("datos_sensores_json_separados", "nivel_agua.json")
sensor2 = SensorData("datos_sensores_json_separados", "humedad_suelo.json")
sensor3 = SensorData("datos_sensores_json_separados", "temperatura_dht.json")
datodelsensor = sensor3.read_line()
print(datodelsensor)



