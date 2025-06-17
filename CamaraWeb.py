import cv2
import os
import tkinter as tk
from tkinter import Label, Button, Entry, StringVar, Frame
from PIL import Image, ImageTk, ImageDraw, ImageFont
from datetime import datetime
from datetime import timedelta
import threading
import time
import platform
import subprocess

######INSTALAR pip install opencv-python Pillow para usar el cv2

FOLDER = "capturas"
LOG_FILE = "capturas_log.txt"
VIDEO_FOLDER = "timelapses"
os.makedirs(FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Capturador automático de fotos")

        self.cap = cv2.VideoCapture(0)

        self.label = Label(root)
        self.label.pack()

        self.btn_capturar = Button(root, text="Capturar Manual", command=self.capturar_foto)
        self.btn_capturar.pack()

        self.btn_ver = Button(root, text="Abrir Carpeta", command=self.abrir_carpeta)
        self.btn_ver.pack()

        Label(root, text="Intervalo automático (minutos, mínimo 30):").pack()
        self.intervalo_var = StringVar()
        self.intervalo_var.set("30")
        self.intervalo_entry = Entry(root, textvariable=self.intervalo_var)
        self.intervalo_entry.pack()

        self.btn_iniciar = Button(root, text="Iniciar Captura Automática", command=self.iniciar_auto)
        self.btn_iniciar.pack()

        Label(root, text="Últimas fotos capturadas:").pack()
        self.galeria_frame = Frame(root)
        self.galeria_frame.pack()
        self.miniaturas = []

        Label(root, text="Vista previa del video generado:").pack()
        self.label_video = Label(root)
        self.label_video.pack()

        self.btn_ver_video = Button(root, text="Ver último video", command=self.ver_video)
        self.btn_ver_video.pack()

        self.btn_generar_video = Button(root, text="Generar Video Ahora", command=self.generar_video)
        self.btn_generar_video.pack()


        self.btn_detener_video = Button(root, text="Detener Video", command=self.detener_video)
        self.btn_detener_video.pack()

        self.reproduciendo = False
        self.auto = False
        self.actualizar_frame()

        self.canvas_video = None
        self.btn_cerrar_video = None

        self.periodo_var = StringVar(value="Día")
        Label(root, text="Generar timelapse cada:").pack()
        self.opciones_periodo = ["Día", "Semana", "Mes"]
        self.menu_periodo = tk.OptionMenu(root, self.periodo_var, *self.opciones_periodo)
        self.menu_periodo.pack()
    


    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame_resized = cv2.resize(frame, (320, 240))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
        self.root.after(10, self.actualizar_frame)

    def capturar_foto(self):
        ret, frame = self.cap.read()
        if ret:
            ahora = datetime.now()
            timestamp = ahora.strftime("%Y-%m-%d %H:%M:%S")
            nombre = ahora.strftime("%Y%m%d_%H%M%S") + ".jpg"
            ruta = os.path.join(FOLDER, nombre)

            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            try:
                font = ImageFont.truetype("arial.ttf", 32)
            except:
                font = ImageFont.load_default()
            draw.text((10, 10), timestamp, font=font, fill=(255, 255, 0))
            img_pil.save(ruta)

            with open(LOG_FILE, "a") as f:
                f.write(f"{timestamp} -> Foto capturada: {nombre}\n")

            print(f"Foto guardada: {ruta}")
            self.actualizar_galeria()
            self.limpiar_fotos_si_exceden()
            self.verificar_y_generar_timelapse()


    def actualizar_galeria(self):
        for widget in self.galeria_frame.winfo_children():
            widget.destroy()

        archivos = sorted(os.listdir(FOLDER), reverse=True)[:3]
        for archivo in archivos:
            path = os.path.join(FOLDER, archivo)
            img = Image.open(path)
            img.thumbnail((100, 100))
            imgtk = ImageTk.PhotoImage(img)
            lbl = Label(self.galeria_frame, image=imgtk)
            lbl.image = imgtk
            lbl.pack(side=tk.LEFT, padx=5)

    def abrir_carpeta(self):
        sistema = platform.system()
        if sistema == "Windows":
            os.startfile(FOLDER)

    def iniciar_auto(self):
        if not self.auto:
            try:
                intervalo = int(self.intervalo_var.get())
                if intervalo < 0:
                    print("El intervalo mínimo es de 30 minutos.")
                    return
            except:
                print("Valor inválido para el intervalo.")
                return

            self.auto = True
            threading.Thread(target=self.captura_automatica, args=(intervalo,), daemon=True).start()
            self.btn_iniciar.config(state=tk.DISABLED)

    def captura_automatica(self, intervalo):
        while self.auto:
            self.capturar_foto()
            time.sleep(intervalo * 60)

    def limpiar_fotos_si_exceden(self):
        archivos = sorted([f for f in os.listdir(FOLDER) if f.endswith(".jpg")])
        if len(archivos) > 100:
            exceso = len(archivos) - 100
            for i in range(exceso):
                path_borrar = os.path.join(FOLDER, archivos[i])
                os.remove(path_borrar)
                print(f"Foto eliminada: {archivos[i]}")

    def generar_video(self):
        archivos = sorted([f for f in os.listdir(FOLDER) if f.endswith(".jpg")])
        if not archivos:
            print("No hay imágenes para generar el video.")
            return

        first_image_path = os.path.join(FOLDER, archivos[0])
        frame = cv2.imread(first_image_path)
        height, width, _ = frame.shape

        ahora = datetime.now()
        nombre_video = ahora.strftime("timelapse_%Y%m%d_%H%M%S.avi")
        ruta_video = os.path.join(VIDEO_FOLDER, nombre_video)

        out = cv2.VideoWriter(ruta_video, cv2.VideoWriter_fourcc(*'XVID'), 2, (width, height))

        for archivo in archivos:
            img_path = os.path.join(FOLDER, archivo)
            frame = cv2.imread(img_path)
            if frame is not None:
                out.write(frame)

        out.release()
        print(f"Video generado: {ruta_video}")

    def ver_video(self):
        archivos = sorted([f for f in os.listdir(VIDEO_FOLDER) if f.endswith(".avi")])
        if not archivos:
            print("No hay videos generados aún.")
            return

        ruta_video = os.path.join(VIDEO_FOLDER, archivos[-1])
        print(f"Reproduciendo video: {ruta_video}")

        self.reproduciendo = True

        # Crear canvas que cubre toda la ventana
        self.canvas_video = tk.Canvas(self.root, bg="white", width=self.root.winfo_width(), height=self.root.winfo_height())
        self.canvas_video.place(x=0, y=0, relwidth=1, relheight=1)

       
        self.btn_cerrar_video = Button(self.root, text="❌", command=self.detener_video, bg="red", fg="white")
        self.btn_cerrar_video.place(relx=1.0, rely=0.0, anchor="ne")

        # Iniciar reproducción
        threading.Thread(target=self.reproducir_video_en_canvas, args=(ruta_video,), daemon=True).start()


    def reproducir_video_en_canvas(self, ruta_video):
        cap = cv2.VideoCapture(ruta_video)

        while self.reproduciendo:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))  # Tamaño fijo o dinámico
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            if self.canvas_video:
                self.canvas_video.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas_video.image = imgtk

            time.sleep(0.1)

        cap.release()

    def verificar_y_generar_timelapse(self):
        archivos = sorted([f for f in os.listdir(FOLDER) if f.endswith(".jpg")])
        if not archivos:
            return

        fechas = []
        for archivo in archivos:
            try:
                fecha_str = archivo.split(".")[0]
                fecha = datetime.strptime(fecha_str, "%Y%m%d_%H%M%S")
                fechas.append(fecha)
            except:
                continue

        if not fechas:
            return

        fecha_mas_antigua = min(fechas)
        fecha_mas_reciente = max(fechas)
        diferencia = fecha_mas_reciente - fecha_mas_antigua

        periodo = self.periodo_var.get()

        if (
            (periodo == "Día" and diferencia >= timedelta(days=1)) or
            (periodo == "Semana" and diferencia >= timedelta(days=7)) or
            (periodo == "Mes" and diferencia >= timedelta(days=30))
        ):
            print(f"🕒 Generando video por periodo: {periodo}")
            self.generar_video()

            # Mover o eliminar las fotos ya usadas
            for archivo in archivos:
                os.remove(os.path.join(FOLDER, archivo))


    def detener_video(self):
        self.reproduciendo = False
        if self.canvas_video:
            self.canvas_video.destroy()
            self.canvas_video = None
        if self.btn_cerrar_video:
            self.btn_cerrar_video.destroy()
            self.btn_cerrar_video = None


    def cerrar(self):
        self.auto = False
        self.cap.release()
        self.root.destroy()

root = tk.Tk()
app = CameraApp(root)
root.protocol("WM_DELETE_WINDOW", app.cerrar)
root.mainloop()
