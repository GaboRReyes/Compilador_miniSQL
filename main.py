"main.py — Programa Principal para Analizador Léxico de MiniSQL en Español"
import sys, os
from lexer import AnalizadorLexico, Token

def sep(titulo="", ancho=65):
    if titulo: print(f"  {titulo}")
    else:      print(f"{'─'*ancho}")

def imprimir_resultado(lx, tokens):
    print(f"\n  {'#':<4} {'Cód':>6}  {'Tipo':<22} {'Lexema':<28} Posición")
    print(f"  {'─'*4} {'─'*6}  {'─'*22} {'─'*28} {'─'*10}")
    for i, tok in enumerate(tokens, 1):
        nombre = Token.nombre(tok.tipo)
        marca  = "X" if Token.es_error(tok.tipo) else " "
        print(f"{marca} {i:<4} {tok.tipo:>6}  {nombre:<22} {repr(tok.lexema):<28} L{tok.linea}:C{tok.columna}")
    if lx.errores:
        print(f"\n  ERRORES ({len(lx.errores)}):")
        for e in lx.errores: print(f"     {e}")
    else:
        print("\n  Sin errores léxicos")
    print(f"\n  {lx.resumen()}")

def analizar(codigo, titulo=""):
    if titulo: sep(titulo)
    lx = AnalizadorLexico(codigo)
    toks = lx.analizar()
    lineas = [l for l in codigo.strip().split('\n') if l.strip()]
    print("\n  Código:")
    for l in lineas[:6]: print(f"    {l}")
    if len(lineas) > 6: print("    ...")
    imprimir_resultado(lx, toks)
    print(lx.tabla_simbolos())
    return lx



def analizar_archivo(ruta):
    if not os.path.exists(ruta):
        print(f"  Archivo no encontrado: {ruta}"); sys.exit(1)
    with open(ruta, encoding='utf-8') as f:
        codigo = f.read()
    analizar(codigo, f"Analizando: {ruta}")

if __name__ == "__main__":
    args = sys.argv[1:]
    analizar_archivo("entrada.sql")
