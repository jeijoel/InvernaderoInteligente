import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from PIL import Image, ImageTk, ImageFilter


TICKETS_FILE = "tickets.txt"



def enviar_ticket():
    usuario = entry_usuario.get().strip()
    cliente = entry_cliente.get().strip()
    dispositivo = entry_dispositivo.get().strip()
    descripcion = text_descripcion.get("1.0", tk.END).strip()

    if not all([usuario, cliente, dispositivo, descripcion]):
        messagebox.showwarning("Campos incompletos", "Por favor, completa todos los campos.")
        return

    ticket = {
        "usuario": usuario,
        "cliente": cliente,
        "dispositivo": dispositivo,
        "motivo": descripcion,
        "estado": "Pendiente",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open(TICKETS_FILE, "a") as f:
            f.write(json.dumps(ticket) + "\n")
        messagebox.showinfo("Enviado", "Tu solicitud ha sido enviada.")

        # Limpiar los campos después de enviar
        entry_usuario.delete(0, tk.END)
        entry_cliente.delete(0, tk.END)
        entry_dispositivo.delete(0, tk.END)
        text_descripcion.delete("1.0", tk.END)
        entry_usuario.focus_set()  # Poner el foco de nuevo en el primer campo

    except IOError as e:
        messagebox.showerror("Error de archivo", f"No se pudo guardar el ticket: {e}")



bg_image_original_pil = None
bg_image_tk = None
background_canvas = None
bg_image_id = None
main_frame = None


def _resize_background_canvas(event=None):
    global bg_image_tk, bg_image_id, background_canvas, bg_image_original_pil, main_frame

    if main_frame is None or not hasattr(background_canvas, 'winfo_width'):
        root.after(100, _resize_background_canvas)
        return

    new_width = main_frame.winfo_width()
    new_height = main_frame.winfo_height()

    if new_width < 1 or new_height < 1:
        root.after(100, _resize_background_canvas)
        return

    if bg_image_original_pil and background_canvas:
        background_canvas.config(width=new_width, height=new_height)

        img_width, img_height = bg_image_original_pil.size


        scale = max(new_width / img_width, new_height / img_height)
        new_img_width = int(img_width * scale)
        new_img_height = int(img_height * scale)

        resized_img_pil = bg_image_original_pil.resize((new_img_width, new_img_height), Image.LANCZOS)

        if resized_img_pil.mode != 'RGBA':
            resized_img_pil = resized_img_pil.convert('RGBA')
        alpha = resized_img_pil.split()[-1]
        alpha = alpha.point(lambda i: i * 0.15)  # 15% de opacidad
        resized_img_pil.putalpha(alpha)

        bg_image_tk = ImageTk.PhotoImage(resized_img_pil)


        background_canvas.coords(bg_image_id, new_width / 2, new_height / 2)
        background_canvas.itemconfig(bg_image_id, image=bg_image_tk)


        background_canvas.lower()



root = tk.Tk()
root.title("Crear Ticket de Servicio")
root.geometry("400x450")
root.resizable(True, True)

#Colores
COLOR_PRIMARIO = "#096B35"
COLOR_ACENTO = "#7AC35D"
COLOR_FONDO_CLARO = "#FFFFFF"
COLOR_FONDO_SUAVE = "#F0F0F0"


style = ttk.Style()
style.theme_use('clam')


style.configure('TLabel',
                background=COLOR_FONDO_CLARO,
                foreground='black',
                font=('Helvetica', 10))

style.configure('TEntry',
                fieldbackground=COLOR_FONDO_CLARO,
                foreground='black',
                font=('Helvetica', 10))



style.configure('TButton',
                background=COLOR_PRIMARIO,
                foreground=COLOR_FONDO_CLARO,
                font=('Helvetica', 10, 'bold'),
                padding=8)
style.map('TButton',
          background=[('active', COLOR_ACENTO)])


root.configure(bg=COLOR_FONDO_CLARO)


logo_path_icon = r"C:\Users\dilan\InvernaderoInteligente\logo.png"
try:
    icon_img_pil = Image.open(logo_path_icon)
    icon_img_tk = ImageTk.PhotoImage(icon_img_pil)
    root.iconphoto(True, icon_img_tk)
except Exception as e:
    print(f"Advertencia: No se pudo cargar el ícono de la ventana. Error: {e}")


main_frame = ttk.Frame(root, padding="20 20 20 20")
main_frame.pack(fill="both", expand=True)


style.configure('TFrame', background=COLOR_FONDO_CLARO)


logo_fondo_path = r"C:\Users\edwar\PycharmProjects\PythonProject\logo.png"
try:
    bg_image_original_pil = Image.open(logo_fondo_path)

    background_canvas = tk.Canvas(main_frame, highlightthickness=0, bg=COLOR_FONDO_CLARO)
    background_canvas.place(x=0, y=0, relwidth=1, relheight=1)


    bg_image_tk = ImageTk.PhotoImage(bg_image_original_pil.filter(ImageFilter.GaussianBlur(radius=8)).convert('RGBA'))
    bg_image_id = background_canvas.create_image(
        0, 0, image=bg_image_tk, anchor="center"
    )


    main_frame.bind("<Configure>", _resize_background_canvas)
    background_canvas.lower()

except Exception as e:
    print(f"Advertencia: No se pudo cargar o procesar la imagen de fondo. Error: {e}")




ttk.Label(main_frame, text="Usuario:").pack(anchor='w', pady=(5, 0))
entry_usuario = ttk.Entry(main_frame, width=40)
entry_usuario.pack(fill='x', pady=(0, 10))


ttk.Label(main_frame, text="Cliente:").pack(anchor='w', pady=(5, 0))
entry_cliente = ttk.Entry(main_frame, width=40)
entry_cliente.pack(fill='x', pady=(0, 10))


ttk.Label(main_frame, text="ID Dispositivo:").pack(anchor='w', pady=(5, 0))
entry_dispositivo = ttk.Entry(main_frame, width=40)
entry_dispositivo.pack(fill='x', pady=(0, 10))


ttk.Label(main_frame, text="Descripción del problema:").pack(anchor='w', pady=(5, 0))
text_descripcion = tk.Text(main_frame, height=5, width=40,
                           bg=COLOR_FONDO_CLARO, fg='black', font=('Helvetica', 10),
                           relief="solid", bd=1)
text_descripcion.pack(fill='x', pady=(0, 15))


send_button = ttk.Button(main_frame, text="Enviar Ticket", command=enviar_ticket)

send_button.pack(pady=10)
root.after(150, _resize_background_canvas)
entry_usuario.focus_set()
root.mainloop()