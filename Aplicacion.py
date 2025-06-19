from tkinter import *
from tkinter import messagebox
from interfaz_graficos import *
import os
from Controler import *
import threading
import time
from interfaz_graficos import InterfazGraficas
import tkinter as tk

def ventana_principal():
    #####Inicializar el controler$########
    serial_control = Control('COM3')  # No borrar
    pico_host = '192.168.100.104'
    pico_port = 1234
    pico_client = PicoTCPClient(pico_host, pico_port)
    ejecucion_activa = False
    
    ventana_principal = Tk()
    ventana_principal.title('Interfaz Gráfica')
    # Obtener el tamaño real de la pantalla
    ancho_pantalla = ventana_principal.winfo_screenwidth()
    alto_pantalla = ventana_principal.winfo_screenheight()

    # Configurar el tamaño máximo
    ventana_principal.config(width=ancho_pantalla, height=alto_pantalla)

    # Usar geometry para asegurarse de que la ventana se muestra correctamente
    ventana_principal.geometry(f"{ancho_pantalla}x{alto_pantalla}")

    ventana_principal.resizable(width=NO, height=NO)
    ventana_principal.iconbitmap('./Imagenes/Interfaz.ico')

    # Cálculos del canvas
    ancho_lienzo_principal = 486
    largo_lienzo_principal = 920


    # Coordenadas para centrar el canvas
    canvas_x = (ancho_pantalla - ancho_lienzo_principal) // 2
    canvas_y = (alto_pantalla - largo_lienzo_principal) // 2

    lienzo_principal = Canvas(ventana_principal, width=ancho_lienzo_principal, height=largo_lienzo_principal, bg="cornflower blue", cursor="dotbox")
    lienzo_principal.place(x=canvas_x, y=canvas_y)

    def Ruta_Audio(nombre):
        return os.path.join('Audios', nombre)

    def cargarImagen(nombre):
        ruta = os.path.join('Imagenes',nombre)
        imagen = PhotoImage(file=ruta)
        return imagen

    def desabilitado():
        messagebox.showinfo(title="Mensaje de la aplicación", message="Cierra la aplicación desde la pantalla principal dando click en 'Cerrar'")
        pass
    def Destruir_ventana_principal():
        ventana_principal.destroy()

    def lienzo_grafica_temperatura():
        mostrar_ventana_graficos()

    def lienzo_grafica_humedad():

        mostrar_ventana_graficos()

    def estado_techo():
        return "Estado del Techo"

    def intervalo_toma_de_datos():
        return None

    def intervalo_encendido_apagado_luz():
        return None

    def intervalo_encendido_apagado_ventilador():
        return None

    def estado_luz():
        return "Estado de Luz"

    def estado_ventilador():
        return "Estado de Ventilador"

    def mostrar_ventana_graficos():
        ventana_graficos = InterfazGraficas(ventana_principal, "datos_sensores_json_separados")
        
    def abrir_graficas():
        carpeta = "datos_sensores_json_separados"
        InterfazGraficas(ventana_principal, carpeta)
    etiqueta_temperatura = Label(lienzo_principal, text="Temperatura", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_temperatura.place(x=10, y=125)

    etiqueta_valor_temperatura = Label(lienzo_principal, text="Valor de Temperatura", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_valor_temperatura.place(x=150, y=125)

    
    boton_grafica_temperatura = Button(lienzo_principal, text="Grafica Temperatura", command=abrir_graficas, bg="white", fg="black", font="Arial 8")
    boton_grafica_temperatura.place(x=375, y=125)


    etiqueta_humedad = Label(lienzo_principal, text="Humedad", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_humedad.place(x=10, y=150)

    etiqueta_valor_humedad = Label(lienzo_principal, text="Valor de Humedad", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_valor_humedad.place(x=150, y=150)

    boton_grafica_humedad = Button(lienzo_principal, text="Grafica Humedad", command=lienzo_grafica_humedad, bg="white", fg="black", font="Arial 8")
    boton_grafica_humedad.place(x=375, y=150)

    etiqueta_techo = Label(lienzo_principal, text="Techo", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_techo.place(x=10, y=175)

    etiqueta_estado_techo = Label(lienzo_principal, text="Estado del Techo", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_estado_techo.place(x=150, y=175)

    boton_abrir_cerrar_techo = Button(lienzo_principal, text=estado_techo(), bg="white", fg="black", font="Arial 8")
    boton_abrir_cerrar_techo.place(x=375, y=175)

    etiqueta_intervalo = Label(lienzo_principal, text="Intervalo", bg="cornflower blue", fg="white", font="Arial 20 bold")
    etiqueta_intervalo.place(x=165, y=200)

    escala_intervalo = Scale(lienzo_principal, from_=5, to=30, orient=HORIZONTAL, command=intervalo_toma_de_datos(), length=275, resolution=5)
    escala_intervalo.place(x=20, y=232.5)

    boton_guardar_intervalo = Button(lienzo_principal, text="Guardar", bg="white", fg="black", font="Arial 10")
    boton_guardar_intervalo.place(x=350, y=240)

    etiqueta_luz = Label(lienzo_principal, text="Luz", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_luz.place(x=10, y=275)

    etiqueta_nivel_luz = Label(lienzo_principal, text="Nivel de Luz", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_nivel_luz.place(x=150, y=275)

    boton_encendido_apagado_manual_luz = Button(lienzo_principal, text=estado_luz(), bg="white", fg="black", font="Arial 10")
    boton_encendido_apagado_manual_luz.place(x=325, y=275)

    etiqueta_ventilador = Label(lienzo_principal, text="Ventilador", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_ventilador.place(x=10, y=300)

    etiqueta_estado_ventilador = Label(lienzo_principal, text="Estado Ventilador", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_estado_ventilador.place(x=150, y=300)

    boton_encendido_apagado_manual_ventilador = Button(lienzo_principal, text=estado_ventilador(), bg="white", fg="black", font="Arial 10")
    boton_encendido_apagado_manual_ventilador.place(x=325, y=300)

    etiqueta_intervalo_encendido_apagado = Label(lienzo_principal, text="Intervalo Encendido Apagado", bg="cornflower blue", fg="white", font="Arial 20 bold")
    etiqueta_intervalo_encendido_apagado.place(x=30, y=325)

    boton_ayuda_intervalo_encendido_apagado = Button(lienzo_principal, text="Ayuda", bg="white", fg="black", font="Arial 10")
    boton_ayuda_intervalo_encendido_apagado.place(x=425, y=330)

    etiqueta_intervalo_luz = Label(lienzo_principal, text="Luz", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_intervalo_luz.place(x=10, y=360)

    escala_intervalo_luz = Scale(lienzo_principal, from_=15, to=120, orient=HORIZONTAL, command=intervalo_encendido_apagado_luz(), length=275, resolution=15)
    escala_intervalo_luz.place(x=115, y=355)

    boton_guardar_intervalo_encendido_apagado_luz = Button(lienzo_principal, text="Guardar", bg="white", fg="black", font="Arial 10")
    boton_guardar_intervalo_encendido_apagado_luz.place(x=415, y=360)

    etiqueta_intervalo_ventilador = Label(lienzo_principal, text="Ventilador", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_intervalo_ventilador.place(x=10, y=400)

    escala_intervalo_ventilador = Scale(lienzo_principal, from_=15, to=120, orient=HORIZONTAL, command=intervalo_encendido_apagado_ventilador(), length=275, resolution=15)
    escala_intervalo_ventilador.place(x=115, y=400)

    boton_guardar_intervalo_encendido_apagado_ventilador = Button(lienzo_principal, text="Guardar", bg="white", fg="black", font="Arial 10")
    boton_guardar_intervalo_encendido_apagado_ventilador.place(x=415, y=400)

    boton_ayuda = Button(lienzo_principal, text="Ayuda", bg="white", fg="black", font="Arial 10")
    boton_ayuda.place(x=15, y=880)

    boton_soporte = Button(lienzo_principal, text="Soporte", bg="white", fg="black")
    boton_soporte.place(x=415, y=880)

    boton_salir = Button(lienzo_principal, text='Cerrar', activebackground="#FFFFFF", activeforeground="#000000",fg="#FFFFFF", bg="#000000", cursor="ur_angle", relief=FLAT, overrelief=RAISED,command=Destruir_ventana_principal)
    boton_salir.place(x=203, y=715)

        # Comandos individuales
    def enviar_comando_1():
        pico_client.send_command("LED_ON")

    def enviar_comando_2():
        pico_client.send_command("LED_OFF")

    def enviar_comando_3():
        pico_client.send_command("M1_ON")

    def enviar_comando_4():
        pico_client.send_command("M1_OFF")

    def enviar_comando_5():
        pico_client.send_command("M2_ON")

    def enviar_comando_6():
        pico_client.send_command("M2_OFF")

    # Ciclo con hilo para ventilador##########################3
    def iniciar_ventilador_ciclo():
        try:
            intervalo = 0 #---------- Aqui no se como retorna el valor la escala pero la definis aqui
            threading.Thread(target=enviar_comando_7, args=(intervalo, "M1")).start()
        except ValueError:
            print("Intervalo inválido para ventilador.")

    def enviar_comando_7(intervalo, objeto):
        ejecucion_activa = True
        while ejecucion_activa:
            pico_client.send_command(f"{objeto}_ON")
            time.sleep(intervalo)
            pico_client.send_command(f"{objeto}_OFF")
            time.sleep(intervalo)

    # Ciclo con hilo para luces##############################
    def iniciar_luces_ciclo():
        try:
            intervalo =  0 #---------- Aqui igual
            threading.Thread(target=enviar_comando_8, args=(intervalo, "LED")).start()
        except ValueError:
            print("Intervalo inválido para luces.")

    def enviar_comando_8( intervalo, objeto):
        ejecucion_activa = True
        while ejecucion_activa:
            pico_client.send_command(f"{objeto}_ON")
            time.sleep(intervalo)
            pico_client.send_command(f"{objeto}_OFF")
            time.sleep(intervalo)

    # Método para detener el ciclo de los ontervalos de las luces y el ventilador, podes crear un boton para este
    def detener_ciclo():
        ejecucion_activa = False

    def on_closing():
        serial_control.cerrar()
        detener_ciclo()

    


    ventana_principal.protocol("WM_DELETE_WINDOW", on_closing)

    ventana_principal.mainloop()

if __name__ == "__main__":
    ventana_principal()
