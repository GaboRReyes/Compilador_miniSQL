#===REPRESENTACIÓN DE AST===#
def arbol_a_texto(nodo, nivel=0):
    texto = "  " * nivel + f"{nodo.tipo}"

    if nodo.valor:
        texto += f": {nodo.valor}"

    texto += "\n"

    for hijo in nodo.hijos:
        texto += arbol_a_texto(hijo, nivel + 1)

    return texto