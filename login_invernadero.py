import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import webbrowser

from Aplicacion import ventana_principal


class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Green Invernadero")
        self.root.geometry("400x550")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(False, False)

        self.frames = {}

        # Crear un contenedor principal
        self.contenedor = tk.Frame(self.root, bg="#FFFFFF")
        self.contenedor.pack(fill="both", expand=True)

        # Crear los distintos frames
        self.frames["login"] = self.crear_pantalla_login()
        self.frames["registro"] = self.crear_pantalla_registro()

        self.mostrar_pantalla("login")

    def mostrar_pantalla(self, nombre):
        frame = self.frames[nombre]
        frame.tkraise()

    def crear_pantalla_login(self):
        frame = tk.Frame(self.contenedor, bg="#FFFFFF")
        frame.place(relwidth=1, relheight=1)

        # Logo
        try:
            logo = Image.open("logo.png")
            logo = logo.resize((250, 100), Image.LANCZOS)
            img_logo = ImageTk.PhotoImage(logo)
            etiqueta_logo = tk.Label(frame, image=img_logo, bg="#FFFFFF")
            etiqueta_logo.image = img_logo
            etiqueta_logo.pack(pady=(40, 20))
        except:
            pass

        # Cuadro de login
        cuadro = tk.Frame(frame, bg="#FFFFFF", bd=2, relief="groove",
                          highlightbackground="#096b35", highlightthickness=2)
        cuadro.place(relx=0.5, rely=0.67, anchor="center", width=350, height=300)

        tk.Label(cuadro, text="Iniciar Sesión", font=("Arial", 16, "bold"),
                 bg="#FFFFFF", fg="#096b35").pack(pady=(15, 5))

        tk.Label(cuadro, text="Usuario o ID de Dispositivo:", bg="#FFFFFF", font=("Arial", 10)).pack()
        self.entrada_usuario = tk.Entry(cuadro, font=("Arial", 10), width=25, justify="center")
        self.entrada_usuario.pack(pady=2)

        tk.Label(cuadro, text="Contraseña:", bg="#FFFFFF", font=("Arial", 10)).pack()
        self.entrada_contrasena = tk.Entry(cuadro, show="*", font=("Arial", 10), width=25, justify="center")
        self.entrada_contrasena.pack(pady=2)

        self.etiqueta_error = tk.Label(cuadro, text="", fg="red", bg="#FFFFFF", font=("Arial", 9))
        self.etiqueta_error.pack()

        tk.Button(cuadro, text="Entrar", font=("Arial", 11, "bold"),
                  bg="#096b35", fg="white", width=15,
                  command=self.procesar_login).pack(pady=10)

        tk.Button(cuadro, text="Registrarse", font=("Arial", 11, "bold"),
                  bg="#ffffff", fg="green", width=15, relief="flat", cursor="hand2",
                  command=lambda: self.mostrar_pantalla("registro")).pack(pady=5)
        # Botón de ayuda
        boton_ayuda = tk.Button(cuadro, text="❓", font=("Arial", 12, "bold"),
                                bg="#ffffff", fg="#096b35", bd=0,
                                activebackground="#ffffff", cursor="hand2",
                                command=self.abrir_ayuda)
        boton_ayuda.place(relx=0.97, rely=0.02, anchor="ne")
        self.modo_admin = False  # Por defecto usuario normal
        def toggle_modo():
                self.modo_admin = not self.modo_admin
                if self.modo_admin:
                    boton_modo.config(text="Modo: Admin")
                else:
                    boton_modo.config(text="Modo: Usuario")

        boton_modo = tk.Button(frame, text="Modo: Usuario", font=("Arial", 9, "bold"),
                                bg="#ffffff", fg="#096b35", bd=0, activebackground="#ffffff",
                                cursor="hand2", command=toggle_modo)
        boton_modo.place(relx=0.95, rely=0.03, anchor="ne")
        return frame

    def crear_pantalla_registro(self):
        frame = tk.Frame(self.contenedor, bg="#FFFFFF")
        frame.place(relwidth=1, relheight=1)

        entradas = {}

        def crear_entrada(texto, key, show=None):
            tk.Label(frame, text=texto, bg="#FFFFFF", font=("Arial", 10)).pack(pady=2)
            entrada = tk.Entry(frame, font=("Arial", 10), width=30, show=show)
            entrada.pack()
            entradas[key] = entrada

        tk.Label(frame, text="Registro de Usuario", font=("Arial", 16, "bold"), bg="#FFFFFF", fg="#096b35").pack(pady=10)

        crear_entrada("Nombre completo:", "nombre")
        crear_entrada("Ubicación:", "ubicacion")
        crear_entrada("Número de dispositivos:", "num_dispositivos")
        crear_entrada("Series (separadas por ;):", "series")
        crear_entrada("ID del dispositivo:", "id_disp")
        crear_entrada("Nombre de usuario:", "usuario")
        crear_entrada("Contraseña:", "contrasena", show="*")

        def guardar_usuario():
            datos = {k: v.get().strip() for k, v in entradas.items()}
            if any(not v for v in datos.values()):
                messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos.")
                return

            id_dispositivo_nuevo = datos['id_disp']

            # Verificar que no exista el id_disp en usuarios.txt
            try:
                with open("usuarios.txt", "r", encoding="utf-8") as archivo:
                    for linea in archivo:
                        campos = linea.strip().split(",")
                        if len(campos) >= 3:
                            id_existente = campos[2]
                            if id_dispositivo_nuevo == id_existente:
                                messagebox.showerror("Error de registro", f"El ID de dispositivo '{id_dispositivo_nuevo}' ya está registrado.")
                                return
            except FileNotFoundError:
                # Si el archivo no existe, no hay problema, se creará después
                pass

            # Si no existe, registrar usuario normalmente
            try:
                with open("usuarios.txt", "a+", encoding="utf-8") as archivo:
                    archivo.seek(0)
                    if archivo.read() and not archivo.read().endswith("\n"):
                        archivo.write(f"{datos['usuario']},{datos['contrasena']},{datos['id_disp']},{datos['nombre']},{datos['ubicacion']},{datos['num_dispositivos']},{datos['series']}\n")
                messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente.")
                self.mostrar_pantalla("login")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el usuario: {e}")


        tk.Button(frame, text="Registrar", bg="#096b35", fg="white",
                  font=("Arial", 10, "bold"), width=15,
                  command=guardar_usuario).pack(pady=10)

        tk.Button(frame, text="Cancelar y Volver", bg="white", fg="red",
                  font=("Arial", 10), width=15,
                  command=lambda: self.mostrar_pantalla("login")).pack()

        return frame

    def procesar_login(self):
            usuario = self.entrada_usuario.get().strip()
            contrasena = self.entrada_contrasena.get().strip()

            if not usuario or not contrasena:
                self.etiqueta_error.config(text="Completa todos los campos.")
                return

            if self.modo_admin:
                if Autenticador.validar_credenciales(usuario, contrasena, admin=True):
                    iniciar_sesion_admin(self.root)
                else:
                    self.etiqueta_error.config(text="Datos incorrectos.")
            else:
                if Autenticador.validar_credenciales(usuario, contrasena):
                    iniciar_sesion(self.root)
                else:
                    self.etiqueta_error.config(text="Datos incorrectos.")

    
     
    def abrir_ayuda(self):
        import webbrowser
        import os

        ruta_html = os.path.abspath("ayuda.html")
        if os.path.exists(ruta_html):
            webbrowser.open(f"file://{ruta_html}")
        else:
            from tkinter import messagebox
            messagebox.showerror("Archivo no encontrado", "El archivo 'ayuda.html' no se encuentra en el directorio.")

class Autenticador:
    @staticmethod
    def validar_credenciales(usuario, contrasena, admin=False):
        archivo_path = "administrador.txt" if admin else "usuarios.txt"
        try:
            with open(archivo_path, "r") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if len(datos) >= 2:
                        u, c = datos[0], datos[1]
                        if usuario == u and contrasena == c:
                            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer archivo: {archivo_path}\n{e}")
        return False

def iniciar_sesion_admin(root):
    root.destroy()  # Cierra login
    from Interfaz_Soporte import InterfazLlamadas
    soporte_root = tk.Tk()
    app = InterfazLlamadas(soporte_root)
    soporte_root.mainloop()
    

def iniciar_sesion(root):
    root.destroy()            # cierra la ventana de login
    ventana_principal()       # abre la interfaz principal

    
def main():
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
    

if __name__ == "__main__":
    main()
