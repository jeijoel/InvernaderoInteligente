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
    #serial_control = Control('COM3')  # No borrar
    pico_host = '192.168.100.104'
    pico_port = 1234
    pico_client = PicoTCPClient(pico_host, pico_port)

    estado_techo_abierto = False
    estado_luz_encendida = False
    estado_ventilador_encendido = False
    ejecucion_activa = False

    intervalo_datos = 5
    intervalo_luz = 15
    intervalo_ventilador = 15

    ventana_principal = Tk()
    ventana_principal.title('Interfaz Gráfica')
    ancho_pantalla = ventana_principal.winfo_screenwidth()
    alto_pantalla = ventana_principal.winfo_screenheight()
    ventana_principal.config(width=ancho_pantalla, height=alto_pantalla)
    ventana_principal.geometry(f"{ancho_pantalla}x{alto_pantalla}")
    ventana_principal.resizable(width=NO, height=NO)
    ventana_principal.iconbitmap('./Imagenes/Interfaz.ico')

    ancho_lienzo_principal = 486
    largo_lienzo_principal = 920
    canvas_x = (ancho_pantalla - ancho_lienzo_principal) // 2
    canvas_y = (alto_pantalla - largo_lienzo_principal) // 2

    lienzo_principal = Canvas(ventana_principal, width=ancho_lienzo_principal, height=largo_lienzo_principal, bg="cornflower blue", cursor="dotbox")
    lienzo_principal.place(x=canvas_x, y=canvas_y)

    def mostrar_ventana_graficos():
        carpeta = "datos_sensores_json_separados"
        InterfazGraficas(ventana_principal, carpeta)

    def actualizar_intervalo(valor):
        nonlocal intervalo_datos
        intervalo_datos = int(valor)
        print(f"Intervalo de toma de datos: {intervalo_datos}s")

    def actualizar_intervalo_luz(valor):
        nonlocal intervalo_luz
        intervalo_luz = int(valor)
        print(f"Intervalo de luz: {intervalo_luz}s")

    def actualizar_intervalo_ventilador(valor):
        nonlocal intervalo_ventilador
        intervalo_ventilador = int(valor)
        print(f"Intervalo de ventilador: {intervalo_ventilador}s")

    def guardar_intervalos():
        print(f"Enviando intervalos al microcontrolador...")
        pico_client.send_command(f"SET_INTERVAL_DATA:{intervalo_datos}")
        pico_client.send_command(f"SET_INTERVAL_LIGHT:{intervalo_luz}")
        pico_client.send_command(f"SET_INTERVAL_FAN:{intervalo_ventilador}")
        print("Intervalos enviados correctamente.")

    def alternar_techo():
        nonlocal estado_techo_abierto
        if estado_techo_abierto:
            pico_client.send_command("M2_OFF")
            etiqueta_estado_techo.config(text="Techo Cerrado")
            boton_abrir_cerrar_techo.config(text="Abrir Techo")
        else:
            pico_client.send_command("M2_ON")
            etiqueta_estado_techo.config(text="Techo Abierto")
            boton_abrir_cerrar_techo.config(text="Cerrar Techo")
        estado_techo_abierto = not estado_techo_abierto

    def alternar_luz():
        nonlocal estado_luz_encendida
        if estado_luz_encendida:
            pico_client.send_command("LED_OFF")
            etiqueta_nivel_luz.config(text="Luz Apagada")
            boton_encendido_apagado_manual_luz.config(text="Encender Luz")
        else:
            pico_client.send_command("LED_ON")
            etiqueta_nivel_luz.config(text="Luz Encendida")
            boton_encendido_apagado_manual_luz.config(text="Apagar Luz")
        estado_luz_encendida = not estado_luz_encendida

    def alternar_ventilador():
        nonlocal estado_ventilador_encendido
        if estado_ventilador_encendido:
            pico_client.send_command("M1_OFF")
            etiqueta_estado_ventilador.config(text="Ventilador Apagado")
            boton_encendido_apagado_manual_ventilador.config(text="Encender Ventilador")
        else:
            pico_client.send_command("M1_ON")
            etiqueta_estado_ventilador.config(text="Ventilador Encendido")
            boton_encendido_apagado_manual_ventilador.config(text="Apagar Ventilador")
        estado_ventilador_encendido = not estado_ventilador_encendido

    def detener_ciclo():
        nonlocal ejecucion_activa
        ejecucion_activa = False

    def on_closing():
        serial_control.cerrar()
        detener_ciclo()
        ventana_principal.destroy()

    etiqueta_temperatura = Label(lienzo_principal, text="Temperatura", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_temperatura.place(x=10, y=125)
    etiqueta_valor_temperatura = Label(lienzo_principal, text="-- °C", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_valor_temperatura.place(x=150, y=125)
    boton_grafica_temperatura = Button(lienzo_principal, text="Gráfica Temperatura", command=mostrar_ventana_graficos, bg="white", fg="black", font="Arial 8")
    boton_grafica_temperatura.place(x=375, y=125)

    etiqueta_humedad = Label(lienzo_principal, text="Humedad", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_humedad.place(x=10, y=150)
    etiqueta_valor_humedad = Label(lienzo_principal, text="-- %", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_valor_humedad.place(x=150, y=150)
    boton_grafica_humedad = Button(lienzo_principal, text="Gráfica Humedad", command=mostrar_ventana_graficos, bg="white", fg="black", font="Arial 8")
    boton_grafica_humedad.place(x=375, y=150)

    etiqueta_techo = Label(lienzo_principal, text="Techo", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_techo.place(x=10, y=175)
    etiqueta_estado_techo = Label(lienzo_principal, text="Techo Cerrado", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_estado_techo.place(x=150, y=175)
    boton_abrir_cerrar_techo = Button(lienzo_principal, text="Abrir Techo", command=alternar_techo, bg="white", fg="black", font="Arial 8")
    boton_abrir_cerrar_techo.place(x=375, y=175)

    etiqueta_luz = Label(lienzo_principal, text="Luz", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_luz.place(x=10, y=275)
    etiqueta_nivel_luz = Label(lienzo_principal, text="Luz Apagada", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_nivel_luz.place(x=150, y=275)
    boton_encendido_apagado_manual_luz = Button(lienzo_principal, text="Encender Luz", command=alternar_luz, bg="white", fg="black", font="Arial 10")
    boton_encendido_apagado_manual_luz.place(x=325, y=275)

    etiqueta_ventilador = Label(lienzo_principal, text="Ventilador", bg="cornflower blue", fg="white", font="Arial 16 bold")
    etiqueta_ventilador.place(x=10, y=300)
    etiqueta_estado_ventilador = Label(lienzo_principal, text="Ventilador Apagado", bg="cornflower blue", fg="white", font="Arial 16")
    etiqueta_estado_ventilador.place(x=150, y=300)
    boton_encendido_apagado_manual_ventilador = Button(lienzo_principal, text="Encender Ventilador", command=alternar_ventilador, bg="white", fg="black", font="Arial 10")
    boton_encendido_apagado_manual_ventilador.place(x=325, y=300)

    etiqueta_intervalo = Label(lienzo_principal, text="Intervalo de Toma de Datos", bg="cornflower blue", fg="white", font="Arial 14 bold")
    etiqueta_intervalo.place(x=10, y=500)
    escala_intervalo = Scale(lienzo_principal, from_=5, to=60, orient=HORIZONTAL, command=actualizar_intervalo, length=275, resolution=5)
    escala_intervalo.set(intervalo_datos)
    escala_intervalo.place(x=10, y=530)

    etiqueta_intervalo_luz = Label(lienzo_principal, text="Intervalo de Luz", bg="cornflower blue", fg="white", font="Arial 14 bold")
    etiqueta_intervalo_luz.place(x=10, y=580)
    escala_intervalo_luz = Scale(lienzo_principal, from_=15, to=120, orient=HORIZONTAL, command=actualizar_intervalo_luz, length=275, resolution=15)
    escala_intervalo_luz.set(intervalo_luz)
    escala_intervalo_luz.place(x=10, y=610)

    etiqueta_intervalo_ventilador = Label(lienzo_principal, text="Intervalo de Ventilador", bg="cornflower blue", fg="white", font="Arial 14 bold")
    etiqueta_intervalo_ventilador.place(x=10, y=660)
    escala_intervalo_ventilador = Scale(lienzo_principal, from_=15, to=120, orient=HORIZONTAL, command=actualizar_intervalo_ventilador, length=275, resolution=15)
    escala_intervalo_ventilador.set(intervalo_ventilador)
    escala_intervalo_ventilador.place(x=10, y=690)

    boton_guardar_intervalos = Button(lienzo_principal, text="Guardar Intervalos", command=guardar_intervalos, bg="white", fg="black", font="Arial 10")
    boton_guardar_intervalos.place(x=320, y=710)

    boton_salir = Button(lienzo_principal, text='Cerrar', command=on_closing, activebackground="#FFFFFF", activeforeground="#000000", fg="#FFFFFF", bg="#000000", cursor="ur_angle", relief=FLAT, overrelief=RAISED)
    boton_salir.place(x=203, y=850)

    ventana_principal.protocol("WM_DELETE_WINDOW", on_closing)
    ventana_principal.mainloop()

if __name__ == "__main__":
    ventana_principal()
