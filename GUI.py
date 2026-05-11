import os
import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
from main import analizar
from ejecutor import ejecutar_minisql
from sintactico import AnalizadorSintactico
from utils_arbol import arbol_a_texto
from lexer import Token

# ===================================================================
#  PALETA DE COLORES POR TIPO DE TOKEN
# ===================================================================
COLOR_RESERVADA    = "#4FC3F7"   # 1001–1040  palabras reservadas → cian
COLOR_OPERADOR     = "#FFB74D"   # 2001–2010  operadores          → naranja
COLOR_SIMBOLO      = "#FFF176"   # 3001–3005  símbolos            → amarillo
COLOR_IDENTIFICADOR= "#FFFFFF"   # 6000+      identificadores     → blanco
COLOR_ENTERO       = "#AED581"   # 7000+      enteros             → verde lima
COLOR_FLOTANTE     = "#80CBC4"   # 8000+      flotantes           → verde menta
COLOR_CADENA       = "#EF9A9A"   # 9000+      cadenas de texto    → coral
COLOR_ERROR        = "#FF5252"   # errores léxicos                → rojo
COLOR_DEFAULT      = "#CCCCCC"   # cualquier otro                 → gris

COLOR_TAG = {
    COLOR_RESERVADA:     "reservada",
    COLOR_OPERADOR:      "operador",
    COLOR_SIMBOLO:       "simbolo",
    COLOR_IDENTIFICADOR: "identificador",
    COLOR_ENTERO:        "entero",
    COLOR_FLOTANTE:      "flotante",
    COLOR_CADENA:        "cadena",
    COLOR_ERROR:         "error_tok",
    COLOR_DEFAULT:       "default",
}

ALL_TAGS = list(COLOR_TAG.values())


def color_de_token(tipo: int) -> str:
    if Token.es_error(tipo):       return COLOR_ERROR
    if 1001 <= tipo <= 1040:       return COLOR_RESERVADA
    if 2001 <= tipo <= 2010:       return COLOR_OPERADOR
    if 3001 <= tipo <= 3005:       return COLOR_SIMBOLO
    if tipo >= 9000:               return COLOR_CADENA
    if tipo >= 8000:               return COLOR_FLOTANTE
    if tipo >= 7000:               return COLOR_ENTERO
    if tipo >= 6000:               return COLOR_IDENTIFICADOR
    return COLOR_DEFAULT


# ===================================================================
#  CONFIGURACIÓN
# ===================================================================
ctk.set_appearance_mode("dark")
FONT_MONO      = ("Courier New", 13)
FONT_MONO_SM   = ("Courier New", 12)
FONT_TITLE     = ("Courier New", 26, "bold")
FONT_SUB       = ("Courier New", 13)
COLOR_FONDO    = "#0D0F2B"
COLOR_PANEL    = "#13154A"
COLOR_CONSOLA_BG = "#0A0C1F"

# ===================================================================
#  VENTANA PRINCIPAL
# ===================================================================
root = ctk.CTk()
root.title("Compilador miniSQL")
root.geometry("1280x860")
root.minsize(900, 600)
root.update_idletasks()
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f"1280x860+{(sw-1280)//2}+{(sh-860)//2}")


# ===================================================================
#  HELPERS
# ===================================================================

def hacer_cuadro(parent, titulo_label, row, col):
    wrapper = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=8)
    wrapper.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    wrapper.grid_rowconfigure(1, weight=1)
    wrapper.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(wrapper, text=titulo_label, font=FONT_MONO,
                 text_color="#A0C4FF").grid(row=0, column=0, sticky="w",
                                            padx=8, pady=(6, 2))
    caja = ctk.CTkTextbox(wrapper, font=FONT_MONO_SM, wrap="none")
    caja.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 6))
    return caja


def _registrar_tags(tb: tk.Text):
    for color, tag in COLOR_TAG.items():
        tb.tag_configure(tag, foreground=color)


def insertar_tokens_coloreados(textbox: ctk.CTkTextbox, lx):
    tb: tk.Text = textbox._textbox
    _registrar_tags(tb)
    tb.insert("end", lx.resumen() + "\n\n")
    for i, tok in enumerate(lx.tokens, 1):
        nombre = Token.nombre(tok.tipo)
        marca  = "X" if Token.es_error(tok.tipo) else " "
        linea_txt = (
            f"{marca} {i:<4} {tok.tipo:>6}  {nombre:<22} "
            f"{repr(tok.lexema):<28} L{tok.linea}:C{tok.columna}\n"
        )
        tag = COLOR_TAG.get(color_de_token(tok.tipo), "default")
        tb.insert("end", linea_txt, tag)


# ===================================================================
#  COLOREADO EN TIEMPO REAL
# ===================================================================

def _colorear_consola(event=None):
    """Relexea el texto y aplica colores sobre la marcha."""
    codigo = consola.get("1.0", "end-1c")
    # Quitar tags anteriores
    for tag in ALL_TAGS:
        consola.tag_remove(tag, "1.0", "end")
    if not codigo.strip():
        return
    try:
        lx = analizar(codigo, "live")
    except Exception:
        return
    for tok in lx.tokens:
        tag    = COLOR_TAG.get(color_de_token(tok.tipo), "default")
        inicio = f"{tok.linea}.{tok.columna - 1}"
        fin    = f"{tok.linea}.{tok.columna - 1 + len(tok.lexema)}"
        consola.tag_add(tag, inicio, fin)


def _registrar_tags_consola():
    for color, tag in COLOR_TAG.items():
        consola.tag_configure(tag, foreground=color)


# ===================================================================
#  LÓGICA DE ANÁLISIS
# ===================================================================

def ejecutar_analisis():
    codigo = consola.get("1.0", "end-1c").strip()
    if not codigo:
        return

    for caja in (cuadro_tokens, cuadro_errores,
                 cuadro_tabla, cuadro_analisis, cuadro_resultados):
        caja.configure(state="normal")
        caja.delete("1.0", "end")

    lx = analizar(codigo, "Consulta desde GUI")

    insertar_tokens_coloreados(cuadro_tokens, lx)
    cuadro_tabla.insert("1.0", lx.tabla_simbolos())

    try:
        if lx.errores:
            cuadro_errores.insert("1.0", "\n".join(lx.errores))
            cuadro_analisis.insert("1.0", "No se realizó análisis sintáctico (errores léxicos)")
            resultado_sql = ""
        else:
            cuadro_errores.insert("1.0", "✓ Sin errores léxicos")
            parser = AnalizadorSintactico(lx.tokens)
            arbol  = parser.analizar()
            if parser.errores:
                errores_sin = "\n".join(f"[{cod}] {msg}" for cod, msg in parser.errores)
                cuadro_errores.insert("end", "\n\n" + errores_sin)
                cuadro_analisis.insert("1.0", "Errores sintácticos detectados")
                resultado_sql = ""
            else:
                texto_arbol = "".join(arbol_a_texto(nodo) for nodo in arbol)
                cuadro_analisis.insert("1.0", texto_arbol)
                resultado_sql = ejecutar_minisql(codigo)
    except Exception as e:
        resultado_sql = f"Error al ejecutar SQL:\n{e}"

    cuadro_resultados.insert("1.0", resultado_sql)

    for caja in (cuadro_tokens, cuadro_errores,
                 cuadro_tabla, cuadro_analisis, cuadro_resultados):
        caja.configure(state="disabled")

    _colorear_consola()


def cargar_archivo():
    ruta = filedialog.askopenfilename(
        title="Selecciona un archivo miniSQL",
        filetypes=[
            ("Archivos SQL",      "*.sql"),
            ("Archivos de texto", "*.txt"),
            ("Todos los archivos","*.*")
        ]
    )
    if not ruta or not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as f:
        codigo = f.read()
    consola.delete("1.0", "end")
    consola.insert("1.0", codigo)
    ejecutar_analisis()


# ===================================================================
#  LAYOUT
# ===================================================================
main_frame = ctk.CTkFrame(root, fg_color=COLOR_FONDO)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# ── Encabezado ──
header = ctk.CTkFrame(main_frame, fg_color="transparent")
header.pack(fill="x", pady=(0, 6))

ctk.CTkLabel(header, text="Compilador miniSQL",
             font=FONT_TITLE, text_color="#A0C4FF").pack(side="left", padx=10)

btn_frame = ctk.CTkFrame(header, fg_color="transparent")
btn_frame.pack(side="right", padx=10)

ctk.CTkButton(btn_frame, text="📂 Cargar archivo",
              corner_radius=15, fg_color="#3A7FF6",
              font=FONT_SUB, command=cargar_archivo).pack(side="left", padx=6)

ctk.CTkButton(btn_frame, text="▶  Ejecutar",
              corner_radius=15, fg_color="#25DA43",
              font=FONT_SUB, text_color="#000000",
              command=ejecutar_analisis).pack(side="left", padx=6)

# ── Consola de entrada (tk.Text nativo = soporta tags en modo editable) ──
consola_wrapper = ctk.CTkFrame(main_frame, fg_color=COLOR_PANEL, corner_radius=8)
consola_wrapper.pack(fill="x", padx=6, pady=(0, 8))

ctk.CTkLabel(consola_wrapper, text="📝 Consulta SQL",
             font=FONT_MONO, text_color="#A0C4FF").pack(anchor="w", padx=8, pady=(6, 2))

consola = tk.Text(
    consola_wrapper,
    height=7,
    font=FONT_MONO,
    bg=COLOR_CONSOLA_BG,
    fg=COLOR_DEFAULT,
    insertbackground="white",
    selectbackground="#2A2D6A",
    relief="flat",
    wrap="none",
    padx=6,
    pady=6,
    undo=True,
)
consola.pack(fill="x", padx=4, pady=(0, 6))

_registrar_tags_consola()
consola.bind("<KeyRelease>", _colorear_consola)

root.bind("<Control-Return>", lambda e: ejecutar_analisis())

# ── Grid de 5 paneles de resultado ──
grid = ctk.CTkFrame(main_frame, fg_color="transparent")
grid.pack(fill="both", expand=True, padx=6, pady=(0, 6))

for col in range(3):
    grid.grid_columnconfigure(col, weight=1)
for row in range(2):
    grid.grid_rowconfigure(row, weight=1)

cuadro_tokens     = hacer_cuadro(grid, "🔤 Tokens",            row=0, col=0)
cuadro_errores    = hacer_cuadro(grid, "⚠️  Errores",          row=0, col=1)
cuadro_tabla      = hacer_cuadro(grid, "📋 Tabla de símbolos", row=0, col=2)
cuadro_analisis   = hacer_cuadro(grid, "🌲 Árbol sintáctico",  row=1, col=0)
cuadro_resultados = hacer_cuadro(grid, "✅ Resultados",         row=1, col=1)

# ===================================================================
root.mainloop()
