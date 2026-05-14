import os
import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
 
from lexer       import AnalizadorLexico, Token
from sintactico  import AnalizadorSintactico
from semantico   import AnalizadorSemantico
from traductor   import traducir_minisql
from utils_arbol import arbol_a_texto
from Conexion    import obtener_conexion
 
ESQUEMA = {}

# PALETA DE COLORES POR TIPO DE TOKEN
COLOR_RESERVADA    = "#4FC3F7"   # palabras reservadas → cian
COLOR_OPERADOR     = "#FFB74D"   # operadores          → naranja
COLOR_SIMBOLO      = "#FFF176"   # símbolos            → amarillo
COLOR_IDENTIFICADOR= "#FFFFFF"   # identificadores     → blanco
COLOR_ENTERO       = "#AED581"   # enteros             → verde claro
COLOR_FLOTANTE     = "#80CBC4"   # flotantes           → verde
COLOR_CADENA       = "#EF9A9A"   # cadenas de texto    → coral
COLOR_ERROR        = "#FF5252"   # errores léxicos     → rojo
COLOR_DEFAULT      = "#CCCCCC"   # cualquier otro      → gris
 
# Colores semánticos para el panel de semántica
COLOR_SEM_OK     = "#69F0AE"   # verde 
COLOR_SEM_ERROR  = "#FF5252"   # rojo
COLOR_SEM_AVISO  = "#FFD740"   # ámbar
 
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
    if Token.es_error(tipo):      return COLOR_ERROR
    if 1001 <= tipo <= 1050:      return COLOR_RESERVADA
    if 2001 <= tipo <= 2010:      return COLOR_OPERADOR
    if 3001 <= tipo <= 3005:      return COLOR_SIMBOLO
    if tipo >= 9000:              return COLOR_CADENA
    if tipo >= 8000:              return COLOR_FLOTANTE
    if tipo >= 7000:              return COLOR_ENTERO
    if tipo >= 6000:              return COLOR_IDENTIFICADOR
    return COLOR_DEFAULT
 
# CONFIGURACIÓN GLOBAL DE ESTILO
ctk.set_appearance_mode("dark")
 
FONT_MONO     = ("Courier New", 13)
FONT_MONO_SM  = ("Courier New", 11)
FONT_TITLE    = ("Courier New", 22, "bold")
FONT_SUB      = ("Courier New", 13)
 
COLOR_FONDO       = "#0D0F2B"
COLOR_PANEL       = "#13154A"
COLOR_CONSOLA_BG  = "#0A0C1F"
COLOR_ACCENT      = "#A0C4FF"
 
# VENTANA PRINCIPAL
root = ctk.CTk()
root.title("Compilador miniSQL — en Español")
root.geometry("1400x900")
root.minsize(1000, 650)
root.update_idletasks()
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f"1400x900+{(sw-1400)//2}+{(sh-900)//2}")
 
# HELPERS DE CONSTRUCCIÓN DE UI 
def hacer_cuadro(parent, titulo_label, row, col, colspan=1):
    """Crea un panel con título y CTkTextbox interno."""
    wrapper = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=8)
    wrapper.grid(row=row, column=col, columnspan=colspan,
                 padx=5, pady=5, sticky="nsew")
    wrapper.grid_rowconfigure(1, weight=1)
    wrapper.grid_columnconfigure(0, weight=1)
 
    ctk.CTkLabel(wrapper, text=titulo_label, font=FONT_MONO,
                 text_color=COLOR_ACCENT).grid(row=0, column=0, sticky="w",
                                               padx=8, pady=(6, 2))
    caja = ctk.CTkTextbox(wrapper, font=FONT_MONO_SM, wrap="none")
    caja.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 6))
    return caja
 
 
def _registrar_tags(widget: tk.Text):
    """Configura los tags de color sobre el widget tk.Text subyacente."""
    for color, tag in COLOR_TAG.items():
        widget.tag_configure(tag, foreground=color)
    # Tags semánticos adicionales
    widget.tag_configure("sem_ok",    foreground=COLOR_SEM_OK)
    widget.tag_configure("sem_error", foreground=COLOR_SEM_ERROR)
    widget.tag_configure("sem_aviso", foreground=COLOR_SEM_AVISO)
    widget.tag_configure("fase",      foreground=COLOR_ACCENT, font=("Courier New", 11, "bold"))
    widget.tag_configure("ok_fase",   foreground=COLOR_SEM_OK, font=("Courier New", 11, "bold"))
    widget.tag_configure("err_fase",  foreground=COLOR_SEM_ERROR, font=("Courier New", 11, "bold"))
 
 
def _tb(caja: ctk.CTkTextbox) -> tk.Text:
    """Devuelve el widget tk.Text interno de un CTkTextbox."""
    return caja._textbox
 
 
def _insertar(caja: ctk.CTkTextbox, texto: str, tag: str = ""):
    """Inserta texto con tag opcional en un CTkTextbox (estado normal)."""
    tb = _tb(caja)
    if tag:
        tb.insert("end", texto, tag)
    else:
        tb.insert("end", texto)
 
 
def _limpiar(caja: ctk.CTkTextbox):
    caja.configure(state="normal")
    caja.delete("1.0", "end")
 
 
def _bloquear(caja: ctk.CTkTextbox):
    caja.configure(state="disabled")
 
# COLOREADO EN TIEMPO REAL (consola de entrada)
def _registrar_tags_consola():
    for color, tag in COLOR_TAG.items():
        consola.tag_configure(tag, foreground=color)
 
 
def _colorear_consola(event=None):
    codigo = consola.get("1.0", "end-1c")
    for tag in ALL_TAGS:
        consola.tag_remove(tag, "1.0", "end")
    if not codigo.strip():
        return
    try:
        lx = AnalizadorLexico(codigo)
        lx.analizar()
    except Exception:
        return
    for tok in lx.tokens:
        tag   = COLOR_TAG.get(color_de_token(tok.tipo), "default")
        ini   = f"{tok.linea}.{tok.columna - 1}"
        fin   = f"{tok.linea}.{tok.columna - 1 + len(tok.lexema)}"
        consola.tag_add(tag, ini, fin)
  
def insertar_tokens_coloreados(lx: AnalizadorLexico):
    tb = _tb(cuadro_tokens)
    _registrar_tags(tb)
 
    tb.insert("end", lx.resumen() + "\n\n")
    for i, tok in enumerate(lx.tokens, 1):
        nombre   = Token.nombre(tok.tipo)
        marca    = "X" if Token.es_error(tok.tipo) else " "
        linea_txt = (
            f"{marca} {i:<4} {tok.tipo:>6}  {nombre:<22}"
            f"  {repr(tok.lexema):<26}  L{tok.linea}:C{tok.columna}\n"
        )
        tag = COLOR_TAG.get(color_de_token(tok.tipo), "default")
        tb.insert("end", linea_txt, tag)
 
 
# INSERTAR ÁRBOL SINTÁCTICO CON COLORES
 
_NODO_COLORES = {
    "SELECT":     "#4FC3F7",  "INSERT":  "#4FC3F7",
    "DELETE":     "#4FC3F7",  "UPDATE":  "#4FC3F7",
    "CREATE":     "#4FC3F7",  "DROP":    "#4FC3F7",
    "USAR":       "#4FC3F7",  "SHOW":    "#4FC3F7",
    "CONDICION":  "#FFB74D",  "COND_SIMPLE": "#FFD54F",
    "OP_LOGICO":  "#FF8A65",
    "COLUMNAS":   "#AED581",  "COL":     "#C5E1A5",
    "TABLA":      "#80CBC4",
    "OPERADOR":   "#FFB74D",  "VALOR":   "#EF9A9A",
    "COLUMNA":    "#FFFFFF",
    "LIMITE":     "#B39DDB",  "ORDER_BY":"#B39DDB",
    "GROUP_BY":   "#B39DDB",
    "VALORES":    "#EF9A9A",  "SET":     "#FFB74D",
    "ASIGNACION": "#FFF176",
}
 
 
def _insertar_arbol_coloreado(nodo, nivel=0):
    """Inserta recursivamente el árbol con indentación y colores."""
    tb = _tb(cuadro_arbol)
 
    prefijo = "  " * nivel
    conector = "└─ " if nivel > 0 else "● "
    label = nodo.tipo + (f": {nodo.valor}" if nodo.valor else "")
    linea = prefijo + conector + label + "\n"
 
    color = _NODO_COLORES.get(nodo.tipo, COLOR_DEFAULT)
    # Registramos el tag dinámico si no existe
    tag_name = f"nodo_{nodo.tipo}"
    try:
        tb.tag_configure(tag_name, foreground=color)
    except Exception:
        pass
    tb.insert("end", linea, tag_name)
 
    for hijo in nodo.hijos:
        _insertar_arbol_coloreado(hijo, nivel + 1)
 
 
#LOGICA DE ANALISIS

def ejecutar_analisis():
    codigo = consola.get("1.0", "end-1c").strip()
    if not codigo:
        return
 
    # Limpiar todos los paneles
    for caja in (cuadro_tokens, cuadro_errores, cuadro_tabla,
                 cuadro_arbol, cuadro_semantico, cuadro_resultados):
        _limpiar(caja)
 
    tb_err = _tb(cuadro_errores)
    _registrar_tags(tb_err)
 
    # FASE 1: LÉXICO
    tb_err.insert("end", "══ LÉXICO ════════════════════════════════\n", "fase")
 
    lx = AnalizadorLexico(codigo)
    lx.analizar()
 
    insertar_tokens_coloreados(lx)
    _tb(cuadro_tokens)  # ya insertado
 
    # Tabla de símbolos
    cuadro_tabla.insert("1.0", lx.tabla_simbolos())
 
    if lx.errores:
        for err in lx.errores:
            tb_err.insert("end", f"  [X] {err}\n", "err_fase")
        tb_err.insert("end", f"\n  ({len(lx.errores)} error(es) lexicos — se continua)\n\n")
    else:
        tb_err.insert("end", "  [OK] Sin errores lexicos\n\n", "ok_fase")
 
    # FASE 2: SINTÁCTICO 
    tb_err.insert("end", "══ SINTÁCTICO ════════════════════════════\n", "fase")
 
    sint = AnalizadorSintactico(lx.tokens)
    arbol = sint.analizar()
 
    # Árbol sintáctico
    tb_arbol = _tb(cuadro_arbol)
    _registrar_tags(tb_arbol)
 
    if arbol:
        for nodo in arbol:
            _insertar_arbol_coloreado(nodo)
    else:
        tb_arbol.insert("end", "  (sin arbol — revisa errores)\n")
 
    if sint.errores:
        for cod, msg in sint.errores:
            tb_err.insert("end", f"  [X] [{cod}] {msg}\n", "err_fase")
        tb_err.insert("end", f"\n  ({len(sint.errores)} error(es) sintactico(s))\n\n")
        # Aun así continuamos para mostrar lo que se pudo analizar
    else:
        tb_err.insert("end", "  [OK] Sin errores sintacticos\n\n", "ok_fase")
 
    # FASE 3: SEMÁNTICO 
    tb_err.insert("end", "══ SEMÁNTICO ═════════════════════════════\n", "fase")
 
    tb_sem = _tb(cuadro_semantico)
    _registrar_tags(tb_sem)
 
    sem = AnalizadorSemantico(arbol, esquema=ESQUEMA)
    ok_sem = sem.analizar()
 
    # Panel semántico: mostrar resultado completo
    if not sem.errores and not sem.avisos:
        tb_sem.insert("end", "[OK] Analisis semantico correcto\n", "sem_ok")
        tb_sem.insert("end", "  No se encontraron errores ni advertencias.\n")
    else:
        if sem.errores:
            tb_sem.insert("end", f"[X] {len(sem.errores)} error(es) semantico(s):\n\n", "sem_error")
            for cod, msg in sem.errores:
                tb_sem.insert("end", f"  [{cod}] {msg}\n", "sem_error")
        if sem.avisos:
            tb_sem.insert("end", f"\n[!] {len(sem.avisos)} aviso(s):\n\n", "sem_aviso")
            for av in sem.avisos:
                tb_sem.insert("end", f"  > {av}\n", "sem_aviso")
 
    # Errores semánticos → panel de errores también
    if sem.errores:
        for cod, msg in sem.errores:
            tb_err.insert("end", f"  [X] [{cod}] {msg}\n", "err_fase")
        tb_err.insert("end", f"\n  ({len(sem.errores)} error(es) semantico(s))\n\n")
    else:
        tb_err.insert("end", "  [OK] Sin errores semanticos\n", "ok_fase")
        if sem.avisos:
            tb_err.insert("end", f"  [!] {len(sem.avisos)} aviso(s) semantico(s)\n", "sem_aviso")
        tb_err.insert("end", "\n")
 
    # FASE 4: TRADUCCIÓN / GENERACIÓN DE CÓDIGO
    tb_err.insert("end", "== TRADUCCION ====================================\n", "fase")
 
    if sint.errores or sem.errores:
        tb_err.insert("end", "  [X] Traduccion omitida por errores previos.\n", "err_fase")
        tb_res = _tb(cuadro_resultados)
        _registrar_tags(tb_res)
        tb_res.insert("end", "(Sin SQL — corrige los errores primero)\n", "err_fase")
        for caja in (cuadro_tokens, cuadro_errores, cuadro_tabla,
                     cuadro_arbol, cuadro_semantico, cuadro_resultados):
            _bloquear(caja)
        _colorear_consola()
        return
 
    try:
        sql = traducir_minisql(lx.tokens)
    except Exception as e:
        tb_err.insert("end", f"  [X] Error en traduccion: {e}\n", "err_fase")
        for caja in (cuadro_tokens, cuadro_errores, cuadro_tabla,
                     cuadro_arbol, cuadro_semantico, cuadro_resultados):
            _bloquear(caja)
        _colorear_consola()
        return
 
    tb_err.insert("end", "  [OK] SQL generado correctamente\n\n", "ok_fase")
 
    # Mostrar el SQL traducido en el panel de resultados (encabezado)
    tb_res = _tb(cuadro_resultados)
    _registrar_tags(tb_res)
    tb_res.insert("end", "-- SQL generado --\n\n", "fase")
    tb_res.insert("end", sql + "\n\n", "sem_ok")
 
    # ── FASE 5: EJECUCIÓN EN MySQL via Conexion.py ───────────────────────────
    tb_err.insert("end", "== EJECUCION MySQL ================================\n", "fase")
    tb_res.insert("end", "-- Resultado MySQL --\n\n", "fase")
 
    conexion = obtener_conexion()
    if conexion is None:
        tb_err.insert("end", "  [X] No se pudo conectar a MySQL (revisa Conexion.py)\n", "err_fase")
        tb_res.insert("end", "  Sin conexion a MySQL.\n", "err_fase")
    else:
        try:
            cursor = conexion.cursor()
            # Dividir por ';' para soportar múltiples sentencias
            sentencias = [s.strip() for s in sql.split(";") if s.strip()]
            alguna_consulta = False
 
            for sentencia in sentencias:
                try:
                    cursor.execute(sentencia)
                    # Sentencias que devuelven filas
                    if sentencia.upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
                        alguna_consulta = True
                        columnas = [desc[0] for desc in cursor.description] if cursor.description else []
                        filas    = cursor.fetchall()
 
                        # Encabezado de columnas
                        encabezado = "  " + " | ".join(f"{c:<15}" for c in columnas)
                        separador  = "  " + "-" * len(encabezado)
                        tb_res.insert("end", f">> {sentencia[:60]}...\n" if len(sentencia) > 60
                                      else f">> {sentencia}\n", "fase")
                        tb_res.insert("end", encabezado + "\n", "reservada")
                        tb_res.insert("end", separador  + "\n")
 
                        if filas:
                            for fila in filas:
                                linea = "  " + " | ".join(f"{str(v):<15}" for v in fila)
                                tb_res.insert("end", linea + "\n", "identificador")
                            tb_res.insert("end", f"\n  {len(filas)} fila(s) encontrada(s)\n\n")
                        else:
                            tb_res.insert("end", "  (sin filas)\n\n")
 
                    else:
                        # INSERT / UPDATE / DELETE / CREATE / DROP / USE
                        conexion.commit()
                        afectadas = cursor.rowcount if cursor.rowcount >= 0 else 0
                        tb_res.insert("end", f">> {sentencia[:60]}\n", "fase")
                        tb_res.insert("end",
                            f"  [OK] Ejecutado — {afectadas} fila(s) afectada(s)\n\n",
                            "ok_fase")
 
                    tb_err.insert("end", f"  [OK] {sentencia[:50]}...\n" if len(sentencia) > 50
                                  else f"  [OK] {sentencia}\n", "ok_fase")
 
                except Exception as e_sql:
                    tb_err.insert("end", f"  [X] Error SQL: {e_sql}\n", "err_fase")
                    tb_res.insert("end", f"  [X] Error: {e_sql}\n\n", "err_fase")
 
            if not alguna_consulta and not sentencias:
                tb_res.insert("end", "  (no se detectaron sentencias a ejecutar)\n")
 
        except Exception as e_conn:
            tb_err.insert("end", f"  [X] Error de conexion: {e_conn}\n", "err_fase")
            tb_res.insert("end", f"  [X] Error de conexion: {e_conn}\n", "err_fase")
        finally:
            try:
                conexion.close()
            except Exception:
                pass
 
    # Bloquear todos los paneles
    for caja in (cuadro_tokens, cuadro_errores, cuadro_tabla,
                 cuadro_arbol, cuadro_semantico, cuadro_resultados):
        _bloquear(caja)
 
    # Actualizar colores en consola
    _colorear_consola()
 
 
def cargar_archivo():
    ruta = filedialog.askopenfilename(
        title="Selecciona un archivo miniSQL",
        filetypes=[
            ("Archivos SQL",    "*.sql"),
            ("Archivos de texto","*.txt"),
            ("Todos",           "*.*"),
        ]
    )
    if not ruta or not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as f:
        codigo = f.read()
    consola.delete("1.0", "end")
    consola.insert("1.0", codigo)
    ejecutar_analisis()
  
# LAYOUT PRINCIPAL

main_frame = ctk.CTkFrame(root, fg_color=COLOR_FONDO)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)
 
# ── Encabezado ────────────────────────────────────────────────────────────────
header = ctk.CTkFrame(main_frame, fg_color="transparent")
header.pack(fill="x", pady=(0, 6))
 
ctk.CTkLabel(header, text="Compilador  miniSQL",
             font=FONT_TITLE, text_color=COLOR_ACCENT).pack(side="left", padx=10)
 
btn_frame = ctk.CTkFrame(header, fg_color="transparent")
btn_frame.pack(side="right", padx=10)
 
ctk.CTkButton(btn_frame, text="Cargar archivo",
              corner_radius=15, fg_color="#3A7FF6",
              font=FONT_SUB, command=cargar_archivo).pack(side="left", padx=6)
 
ctk.CTkButton(btn_frame, text="Ejecutar  (Ctrl+Enter)",
              corner_radius=15, fg_color="#25DA43",
              font=FONT_SUB, text_color="#000000",
              command=ejecutar_analisis).pack(side="left", padx=6)
 
# Consola de entrada 
consola_wrapper = ctk.CTkFrame(main_frame, fg_color=COLOR_PANEL, corner_radius=8)
consola_wrapper.pack(fill="x", padx=6, pady=(0, 8))
 
ctk.CTkLabel(consola_wrapper, text="Consulta SQL  (MiniSQL en Español)",
             font=FONT_MONO, text_color=COLOR_ACCENT).pack(anchor="w", padx=8, pady=(6, 2))
 
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
 
# ── Grid de resultados — 3 columnas × 2 filas = 6 paneles ────────────────────
#
#   Col0              Col1                Col2
#   ─────────────────────────────────────────────────────
#   Tokens            Errores             Tabla simbolos
#   Arbol sint.       Semantico           SQL Traducido
#
grid = ctk.CTkFrame(main_frame, fg_color="transparent")
grid.pack(fill="both", expand=True, padx=6, pady=(0, 6))
 
for c in range(3):
    grid.grid_columnconfigure(c, weight=1)
for r in range(2):
    grid.grid_rowconfigure(r, weight=1)
 
# Fila 0
cuadro_tokens    = hacer_cuadro(grid, "Tokens",             row=0, col=0)
cuadro_errores   = hacer_cuadro(grid, "Errores por fase",   row=0, col=1)
cuadro_tabla     = hacer_cuadro(grid, "Tabla de simbolos",  row=0, col=2)
 
# Fila 1
cuadro_arbol     = hacer_cuadro(grid, "Arbol sintactico",   row=1, col=0)
cuadro_semantico = hacer_cuadro(grid, "Analisis semantico", row=1, col=1)
cuadro_resultados= hacer_cuadro(grid, "Resultados MySQL",   row=1, col=2)
 
# ══════════════════════════════════════════════════════════════════════════════
root.mainloop()
