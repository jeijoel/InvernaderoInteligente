import tkinter as tk
from Controler import Control  

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Venntana")
        self.geometry("300x150")

        # Crear instancia de SerialControl con el puerto
        self.serial_control = Control('COM5')  #--------------------> OJO! Esto es necesario para enviar el objeto con el puerto para que lo abra, si no no hace lecturas, tienen que dejarlo






        # Botones
        self.btn_cmd1 = tk.Button(self, text="ON", command=self.enviar_comando_1)
        self.btn_cmd1.pack(pady=10)

        self.btn_cmd2 = tk.Button(self, text="OFF", command=self.enviar_comando_2)
        self.btn_cmd2.pack(pady=10)



    def enviar_comando_1(self):
        self.serial_control.enviar_comando("LED_ON")

    def enviar_comando_2(self):
        self.serial_control.enviar_comando("LED_OFF")

    def on_closing(self):
      


        self.serial_control.cerrar() #------> Igual no borrar ya que si no se cierrra queda inhabilitado.
        self.destroy()





if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
