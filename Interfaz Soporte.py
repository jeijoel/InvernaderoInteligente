import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from PIL import Image, ImageTk

TICKETS_FILE = "tickets.txt"
USUARIOS_FILE = "usuarios.txt"


def cargar_llamadas():
    llamadas = []
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "r") as f:
            for linea in f:
                try:
                    ticket = json.loads(linea.strip())
                    if "fecha" not in ticket:
                        ticket["fecha"] = "2000-01-01 00:00:00"
                    llamadas.append(ticket)
                except json.JSONDecodeError:
                    continue
    return llamadas


def cargar_usuarios():
    usuarios = []
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as f:
            for linea in f:
                partes = linea.strip().split(",")
                if len(partes) >= 7:
                    usuario = {
                        "usuario": partes[0].strip(),
                        "contrasena": partes[1].strip(),
                        "id": partes[2].strip(),
                        "nombre": partes[3].strip(),
                        "ubicacion": partes[4].strip(),
                        "cantidad": partes[5].strip(),
                        "series": [s.strip() for s in partes[6].split(";")]
                    }
                    usuarios.append(usuario)
        return usuarios


class InterfazLlamadas:
    def __init__(self, root):
        self.root = root
        self.root.title("Llamadas de Servicio")

        style = ttk.Style()
        style.theme_use('clam')


        COLOR_PRIMARIO = "#096B35"
        COLOR_ACENTO = "#7AC35D"
        COLOR_FONDO_CLARO = "#FFFFFF"
        COLOR_FONDO_SUAVE = "#F7F7F7"

        self.root.configure(bg=COLOR_FONDO_CLARO)

        style.configure('TButton',
                        background=COLOR_PRIMARIO,
                        foreground=COLOR_FONDO_CLARO,
                        font=('Helvetica', 10, 'bold'),
                        padding=6)
        style.map('TButton',
                  background=[('active', COLOR_ACENTO)])

        style.configure('TCombobox',
                        fieldbackground=COLOR_FONDO_CLARO,
                        background=COLOR_PRIMARIO,
                        foreground='black',
                        arrowcolor=COLOR_PRIMARIO)

        style.configure('Treeview',
                        background=COLOR_FONDO_CLARO,
                        foreground='black',
                        rowheight=25,
                        fieldbackground=COLOR_FONDO_CLARO)

        style.map('Treeview',
                  background=[('selected', COLOR_ACENTO)])

        style.configure('Treeview.Heading',
                        font=('Helvetica', 10, 'bold'),
                        background=COLOR_PRIMARIO,
                        foreground=COLOR_FONDO_CLARO)

        style.configure('TLabel',
                        background=COLOR_FONDO_CLARO,
                        foreground='black')

        # Cambiar el ícono de la ventana (logo)
        logo_path = r"C:\Users\edwar\PycharmProjects\PythonProject\logo.png"

        try:
            logo_img_pil = Image.open(logo_path)
            logo_img_tk = ImageTk.PhotoImage(logo_img_pil)
            self.root.iconphoto(True, logo_img_tk)
        except Exception as e:
            print(f"Error al cargar el ícono de la ventana: {e}")

        self.llamadas_servicio = cargar_llamadas()
        self.usuarios_data = cargar_usuarios()


        self.main_content_frame = tk.Frame(self.root, bg=COLOR_FONDO_CLARO)
        self.main_content_frame.pack(fill="both", expand=True)


        filter_frame = tk.Frame(self.main_content_frame, bg=COLOR_FONDO_SUAVE)
        filter_frame.pack(pady=10, padx=10, fill='x')


        tk.Label(filter_frame, text="Filtrar por Estado:", bg=COLOR_FONDO_SUAVE, fg="black").pack(side='left', padx=5)
        self.estado_var = tk.StringVar()
        estados = ["Todos", "Pendiente", "En Proceso", "Resuelta"]
        self.estado_menu = ttk.Combobox(filter_frame, textvariable=self.estado_var, values=estados, state="readonly")
        self.estado_menu.current(0)
        self.estado_menu.pack(side='left', padx=5)
        self.estado_menu.bind("<<ComboboxSelected>>", self.actualizar_lista)

        tk.Label(filter_frame, text="Ordenar por Fecha:", bg=COLOR_FONDO_SUAVE, fg="black").pack(side='left', padx=15)
        self.orden_var = tk.StringVar()
        ordenes = ["Fecha descendente", "Fecha ascendente"]
        self.orden_menu = ttk.Combobox(filter_frame, textvariable=self.orden_var, values=ordenes, state="readonly")
        self.orden_menu.current(0)
        self.orden_menu.pack(side='left', padx=5)
        self.orden_menu.bind("<<ComboboxSelected>>", self.actualizar_lista)


        self.btn_refrescar = ttk.Button(self.main_content_frame, text="Refrescar Lista", command=self.refrescar_datos)
        self.btn_refrescar.pack(pady=5)

        # --- Tabla (Treeview) ---
        self.tree = ttk.Treeview(self.main_content_frame,
                                 columns=("cliente", "dispositivo", "motivo", "estado", "fecha"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.capitalize(), anchor='w')
            self.tree.column(col, width=150, anchor='w')
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)


        button_frame = tk.Frame(self.main_content_frame, bg=COLOR_FONDO_CLARO)
        button_frame.pack(pady=5)

        self.btn_ver = ttk.Button(button_frame, text="Ver Info del Ticket Seleccionado",
                                  command=self.abrir_ventana_info)
        self.btn_ver.pack(side='left', padx=10)

        self.btn_cambiar_estado = ttk.Button(button_frame, text="Cambiar Estado del Ticket",
                                             command=self.abrir_ventana_estado)
        self.btn_cambiar_estado.pack(side='left', padx=10)

        self.actualizar_lista()

    def refrescar_datos(self):
        self.llamadas_servicio = cargar_llamadas()
        self.usuarios_data = cargar_usuarios()
        self.actualizar_lista()

    def actualizar_lista(self, event=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtro = self.estado_var.get()
        orden_fecha = self.orden_var.get()

        llamadas_filtradas = [l for l in self.llamadas_servicio if filtro == "Todos" or l["estado"] == filtro]

        try:
            llamadas_filtradas.sort(
                key=lambda x: datetime.strptime(x["fecha"], "%Y-%m-%d %H:%M:%S"),
                reverse=(orden_fecha == "Fecha descendente")
            )
        except ValueError:
            pass

        for llamada in llamadas_filtradas:
            self.tree.insert("", "end", iid=id(llamada), values=(
                llamada["cliente"], llamada["dispositivo"], llamada["motivo"], llamada["estado"], llamada["fecha"]
            ))

    def abrir_ventana_info(self):
        selected_id = self.tree.focus()
        if not selected_id:
            messagebox.showwarning("Sin selección", "Selecciona un ticket.")
            return

        ticket = next((l for l in self.llamadas_servicio if id(l) == int(selected_id)), None)
        if not ticket:
            messagebox.showerror("Error", "No se pudo encontrar la información del ticket seleccionado.")
            return

        usuario_info = {}
        dispositivo_ticket = ticket.get("dispositivo", "")
        for u in self.usuarios_data:
            if dispositivo_ticket in u.get("series", []):
                usuario_info = u
                break

        ventana = tk.Toplevel(self.root)
        ventana.title("Información del Usuario")
        ventana.configure(bg="#FFFFFF")

        texto = (
            f"Nombre: {usuario_info.get('nombre', 'N/D')}\n"
            f"Ubicación: {usuario_info.get('ubicacion', 'N/D')}\n"
            f"Cantidad dispositivos: {usuario_info.get('cantidad', 'N/D')}\n"
            f"Series: {'; '.join(usuario_info.get('series', [])) if usuario_info.get('series') else 'N/D'}"
        )

        tk.Label(ventana, text=texto, justify="left", bg="#FFFFFF", fg="black", font=('Helvetica', 10)).pack(padx=20,
                                                                                                             pady=20)
        ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)

    def abrir_ventana_estado(self):
        selected_id = self.tree.focus()
        if not selected_id:
            messagebox.showwarning("Sin selección", "Selecciona un ticket.")
            return

        ticket = next((l for l in self.llamadas_servicio if id(l) == int(selected_id)), None)
        if not ticket:
            messagebox.showerror("Error", "No se pudo encontrar el ticket seleccionado.")
            return

        ventana_estado = tk.Toplevel(self.root)
        ventana_estado.title("Cambiar Estado del Ticket")
        ventana_estado.configure(bg="#FFFFFF")

        tk.Label(ventana_estado, text="Seleccione el nuevo estado:", bg="#FFFFFF", fg="black").pack(pady=10)

        nuevo_estado = tk.StringVar(value=ticket["estado"])
        estado_menu = ttk.Combobox(ventana_estado, textvariable=nuevo_estado,
                                   values=["Pendiente", "En Proceso", "Resuelta"], state="readonly")
        estado_menu.pack(pady=5)

        def guardar_estado():
            ticket["estado"] = nuevo_estado.get()
            self.guardar_llamadas()
            ventana_estado.destroy()
            self.actualizar_lista()
            messagebox.showinfo("Actualizado", "Estado actualizado correctamente.")

        ttk.Button(ventana_estado, text="Guardar", command=guardar_estado).pack(pady=10)
        ttk.Button(ventana_estado, text="Cerrar", command=ventana_estado.destroy).pack(pady=5)

    def guardar_llamadas(self):
        with open(TICKETS_FILE, "w") as f:
            for llamada in self.llamadas_servicio:
                f.write(json.dumps(llamada) + "\n")



root = tk.Tk()
app = InterfazLlamadas(root)
root.mainloop()