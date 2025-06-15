import tkinter as tk
import threading
from Controler import Control
from Controler import PicoTCPClient
import time

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ventana")
        self.geometry("350x400")

        self.serial_control = Control('COM3')  # No borrar
        self.pico_host = '192.168.100.104'
        self.pico_port = 1234
        self.pico_client = PicoTCPClient(self.pico_host, self.pico_port)

        self.ejecucion_activa = False  # Control del bucle ON/OFF

        # Botones simples
        self.btn_cmd1 = tk.Button(self, text="LED ON", command=self.enviar_comando_1)
        self.btn_cmd1.pack(pady=5)

        self.btn_cmd2 = tk.Button(self, text="LED OFF", command=self.enviar_comando_2)
        self.btn_cmd2.pack(pady=5)

        self.btn_cmd3 = tk.Button(self, text="M1 ON", command=self.enviar_comando_3)
        self.btn_cmd3.pack(pady=5)

        self.btn_cmd4 = tk.Button(self, text="M1 OFF", command=self.enviar_comando_4)
        self.btn_cmd4.pack(pady=5)

        self.btn_cmd5 = tk.Button(self, text="M2 ON", command=self.enviar_comando_5)
        self.btn_cmd5.pack(pady=5)

        self.btn_cmd6 = tk.Button(self, text="M2 OFF", command=self.enviar_comando_6)
        self.btn_cmd6.pack(pady=5)

        # --- Control de Ventilador con intervalo ---
        self.label_vent = tk.Label(self, text="Intervalo Ventilador (s):")
        self.label_vent.pack()
        self.entry_vent = tk.Entry(self)
        self.entry_vent.pack()

        self.btn_cmd7 = tk.Button(self, text="INICIAR VENTILADOR CICLO", command=self.iniciar_ventilador_ciclo)
        self.btn_cmd7.pack(pady=5)

        self.label_luz = tk.Label(self, text="Intervalo Luces (s):")
        self.label_luz.pack()
        self.entry_luz = tk.Entry(self)
        self.entry_luz.pack()

        self.btn_cmd8 = tk.Button(self, text="INICIAR LUCES CICLO", command=self.iniciar_luces_ciclo)
        self.btn_cmd8.pack(pady=5)

        self.btn_detener = tk.Button(self, text="DETENER CICLO", command=self.detener_ciclo)
        self.btn_detener.pack(pady=10)

    # Comandos individuales
    def enviar_comando_1(self):
        self.pico_client.send_command("LED_ON")

    def enviar_comando_2(self):
        self.pico_client.send_command("LED_OFF")

    def enviar_comando_3(self):
        self.pico_client.send_command("M1_ON")

    def enviar_comando_4(self):
        self.pico_client.send_command("M1_OFF")

    def enviar_comando_5(self):
        self.pico_client.send_command("M2_ON")

    def enviar_comando_6(self):
        self.pico_client.send_command("M2_OFF")

    # Ciclo con hilo para ventilador##########################3
    def iniciar_ventilador_ciclo(self):
        try:
            intervalo = float(self.entry_vent.get())
            threading.Thread(target=self.enviar_comando_7, args=(intervalo, "M1")).start()
        except ValueError:
            print("Intervalo inválido para ventilador.")

    def enviar_comando_7(self, intervalo, objeto):
        self.ejecucion_activa = True
        while self.ejecucion_activa:
            self.pico_client.send_command(f"{objeto}_ON")
            time.sleep(intervalo)
            self.pico_client.send_command(f"{objeto}_OFF")
            time.sleep(intervalo)

    # Ciclo con hilo para luces##############################
    def iniciar_luces_ciclo(self):
        try:
            intervalo = float(self.entry_luz.get())
            threading.Thread(target=self.enviar_comando_8, args=(intervalo, "LED")).start()
        except ValueError:
            print("Intervalo inválido para luces.")

    def enviar_comando_8(self, intervalo, objeto):
        self.ejecucion_activa = True
        while self.ejecucion_activa:
            self.pico_client.send_command(f"{objeto}_ON")
            time.sleep(intervalo)
            self.pico_client.send_command(f"{objeto}_OFF")
            time.sleep(intervalo)

    # Método para detener el ciclo de los ontervalos de las luces y el ventilador
    def detener_ciclo(self):
        self.ejecucion_activa = False





    def on_closing(self):
        self.serial_control.cerrar()
        self.detener_ciclo()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
