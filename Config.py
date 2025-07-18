import json


## La clase simplemente lee el json y el metodo de obtener retorna el valor para usarlo en el time sleep del bucle del controler
class Configuracion:
    def __init__(self, file_path="config.json"):
        self.file_path = file_path
        self.data = self._leer_config()
        

    def escribir_config(self, intervalo):
        with open(self.file_path, 'w', encoding='utf-8') as config:
            config.write(json.dumps(intervalo) + "\n")

    def _leer_config(self):
        with open(self.file_path, "r", encoding="utf-8") as config:
            return json.load(config)

    def obtener_intervalo_medicion(self):
        #print(f"{self.data}")
        return self.data
        
    
config = Configuracion()
config.obtener_intervalo_medicion()