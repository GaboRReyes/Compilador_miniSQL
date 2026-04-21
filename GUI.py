import customtkinter as ctk
from tkinter import filedialog
from main import analizar, analizar_archivo

# Configuración inicial de customtkinter
ctk.set_appearance_mode("dark")

# Ventana principal
root = ctk.CTk()
root.title("Compilador miniSQL")
root.geometry("700x500")
root.minsize(500, 400)

color_fondo = "#191742"


def cargar_archivo():
    ruta = filedialog.askopenfilename(
        title="Selecciona un archivo miniSQL",
        filetypes=[
            ("Archivos SQL", "*.sql"),
            ("Archivos de texto", "*.txt"),
            ("Todos los archivos", "*.*")
        ]
    )

    if ruta:
        print("Archivo seleccionado:", ruta)
        analizar_archivo(ruta)


# CONTENEDOR
frame = ctk.CTkFrame(root, fg_color=color_fondo)
frame.pack(fill="both", expand=True)

#CONTENEDOR DE BOTONES
botones_frame = ctk.CTkFrame(frame, fg_color="transparent")

#TITULO
titulo = ctk.CTkLabel(
    frame,
    text="Compilador miniSQL",
    font=("Courier New", 24, "bold"),
    text_color="white"
)

#DESCRIPCION
descripcion = ctk.CTkLabel(
    frame,
    text="Escribe o carga tu consulta miniSQL",
    font=("Courier New", 12),
    text_color="white"
)

#BOTON EJECUTAR
btn_ejecutar = ctk.CTkButton(
    botones_frame,
    text="Ejecutar ▶",
    corner_radius=15,
    fg_color="#25DA43",
    command=lambda: analizar(consola.get("1.0", "end"),"CODIGO ESCRITO EN CONSOLA")
)

#BOTON CARGAR
btn_cargar = ctk.CTkButton(
    botones_frame,
    text="Cargar archivo",
    corner_radius=15,
    fg_color="#3A7FF6",
    command= cargar_archivo
)

#CONSOLA DE COMANDOS
consola = ctk.CTkTextbox(
    frame,
    width=600,
    height=120,
    font=("Courier New", 11)
)

#Texto de ayuda en consola
ayudaTxt = ctk.CTkLabel(
    frame,
    text="Escribe tu consulta en la consola ↓",
    font=("Courier New", 12),
    text_color="white"
)

titulo.pack(anchor="w", padx=15, pady=(10, 0))
descripcion.pack(anchor="w", padx=15, pady=(0, 10)) 
botones_frame.pack(anchor="w", padx=15, pady=(0, 20))
btn_ejecutar.pack(side="left", padx=10)
btn_cargar.pack(side="left", padx=10)
ayudaTxt.pack(anchor="w", padx=15, pady=(0, 5))
consola.pack(fill="x", padx=15, pady=5)

# Texto inicial en consola
consola.configure(text_color="gray")


root.mainloop()