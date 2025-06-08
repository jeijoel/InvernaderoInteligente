import json


## La clase simplemente lee el json y el metodo de obtener retorna el valor para usarlo en el time sleep del bucle del controler
class Configuracion:
    def __init__(self, file_path="config.json"):
        self.file_path = file_path
        self.data = self._leer_config()

    def _leer_config(self):
        with open(self.file_path, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    def obtener_intervalo_medicion(self):
        return self.data.get("intervalo_medicion", None)