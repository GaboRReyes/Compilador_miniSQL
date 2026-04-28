import os
import sys
import customtkinter as ctk
from tkinter import filedialog
from main import analizar
from ejecutor import ejecutar_minisql
from sintactico import AnalizadorSintactico
from utils_arbol import arbol_a_texto


#===Configuración inicial de customtkinter===#
ctk.set_appearance_mode("dark")

#===Ventana principal===#
root = ctk.CTk()
root.title("Compilador miniSQL")
root.geometry("600x500")
root.minsize(500, 400)
root.update_idletasks()
x = (root.winfo_screenwidth()  // 2) - (600 // 2)
y = (root.winfo_screenheight() // 2) - (500 // 2)
root.geometry(f"{600}x{500}+{x}+{y}")

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

    if not os.path.exists(ruta):
        print(f"  Archivo no encontrado: {ruta}"); sys.exit(1)
    with open(ruta, encoding='utf-8') as f:
        codigo = f.read()
    abrir_resultados(codigo)

def abrir_resultados(codigo=None):
    
    if codigo is None:
        codigo = consola.get("1.0", "end").strip()

    root.withdraw()

    ventana = ctk.CTkToplevel()
    ventana.title("Resultados del análisis")
    ventana.geometry("1000x800")
    ventana.grab_set()
    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth()  // 2) - (1000 // 2)
    y = (ventana.winfo_screenheight() // 2) - (800 // 2)
    ventana.geometry(f"{1000}x{800}+{x}+{y}")

    #===CONTENEDOR PRINCIPAL===#
    main_frame = ctk.CTkFrame(ventana)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    main_frame.grid_rowconfigure((0, 1), weight=1)
    main_frame.grid_columnconfigure((0, 1), weight=1)

    def hacer_cuadro(row, col, titulo_label):
        wrapper = ctk.CTkFrame(main_frame, fg_color="transparent")
        wrapper.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(wrapper, text=titulo_label, font=("Courier New", 11, "bold")).grid(row=0, column=0, sticky="w", padx=4)
        caja = ctk.CTkTextbox(wrapper, font=("Courier New", 11))
        caja.grid(row=1, column=0, sticky="nsew")
        return caja

    cuadro_codigo     = hacer_cuadro(0, 0, "Código SQL")
    cuadro_tokens     = hacer_cuadro(0, 1, "Tokens")
    cuadro_errores    = hacer_cuadro(1, 0, "Errores")
    cuadro_tabla      = hacer_cuadro(1, 1, "Tabla de símbolos")
    cuadro_analisis   = hacer_cuadro(2, 0, "Análisis")
    cuadro_resultados = hacer_cuadro(2, 1, "Resultados")

    # === EJECUTAR ANÁLISIS ===#
    lx = analizar(codigo, "Consulta desde GUI")

    #===Construir lista de tokens como texto===#
    lineas_tokens = []
    for i, tok in enumerate(lx.tokens, 1):
        from lexer import Token
        nombre = Token.nombre(tok.tipo)
        marca  = "X" if Token.es_error(tok.tipo) else " "
        lineas_tokens.append(f"{marca} {i:<4} {tok.tipo:>6}  {nombre:<22} {repr(tok.lexema):<28} L{tok.linea}:C{tok.columna}")

    cuadro_codigo.insert("1.0", codigo)
    cuadro_tokens.insert("1.0", lx.resumen() + "\n\n" + "\n".join(lineas_tokens))
    cuadro_errores.insert("1.0", "\n".join(lx.errores) if lx.errores else "Sin errores léxicos")
    cuadro_tabla.insert("1.0", lx.tabla_simbolos())

    try:
        if lx.errores:
            cuadro_analisis.insert("1.0", "Error léxico")
            resultado_sql = ""
        else:
            #===ANALIZADOR SINTÁCTICO===#
            parser = AnalizadorSintactico(lx.tokens)

            arbol = parser.analizar()

            if parser.errores:
                cuadro_analisis.insert("1.0", "\n".join(parser.errores))
                resultado_sql = ""
            else:
                texto_arbol = ""

                for nodo in arbol:
                    texto_arbol += arbol_a_texto(nodo)

                cuadro_analisis.insert("1.0", texto_arbol)
                resultado_sql = ejecutar_minisql(codigo)
    except Exception as e:
        resultado_sql = f"Error al ejecutar SQL:\n{e}"
    cuadro_resultados.insert("1.0", resultado_sql)

    #===Hacer los cuadros de solo lectura===#
    for caja in (cuadro_codigo, cuadro_tokens, cuadro_errores, cuadro_tabla, cuadro_analisis, cuadro_resultados):
        caja.configure(state="disabled")

    #===BOTÓN REGRESAR===#
    def regresar():
        ventana.destroy()
        root.deiconify()

    ctk.CTkButton(ventana, text="⬅ Regresar", command=regresar).pack(pady=10)


#===CONTENEDOR===#
frame = ctk.CTkFrame(root, fg_color=color_fondo)
frame.pack(fill="both", expand=True)

#===CONTENEDOR DE BOTONES===#
botones_frame = ctk.CTkFrame(frame, fg_color="transparent")

#===TITULO===#
titulo = ctk.CTkLabel(
    frame,
    text="Compilador miniSQL",
    font=("Courier New", 24, "bold"),
    text_color="white"
)

#===DESCRIPCION===#
descripcion = ctk.CTkLabel(
    frame,
    text="Escribe o carga tu consulta miniSQL",
    font=("Courier New", 12),
    text_color="white"
)

#===BOTON EJECUTAR===#
btn_ejecutar = ctk.CTkButton(
    botones_frame,
    text="Ejecutar ▶",
    corner_radius=15,
    fg_color="#25DA43",
    command=lambda: abrir_resultados()
)

#===BOTON CARGAR===#
btn_cargar = ctk.CTkButton(
    botones_frame,
    text="Cargar archivo",
    corner_radius=15,
    fg_color="#3A7FF6",
    command= cargar_archivo
)

#===CONSOLA DE COMANDOS===#
consola = ctk.CTkTextbox(
    frame,
    width=600,
    height=120,
    font=("Courier New", 11)
)

#===Texto de ayuda en consola===#
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

#===Texto inicial en consola===#
consola.configure(text_color="gray")


root.mainloop()
