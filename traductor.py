from lexer import AnalizadorLexico

def traducir_minisql(tokens):

    #======TRADUCCIONES (DICCIONARIO DE PALABRAS MINISQL A MySQL)======
    traducciones = {
        "usar": "USE",
        "crear": "CREATE",
        "eliminar": "DROP",
        "modificar": "ALTER",
        "seleccionar": "SELECT",
        "insertar": "INSERT",
        "actualizar": "UPDATE",
        "borrar": "DELETE",
        "mostrar": "SHOW",
        "conceder": "GRANT",
        "revocar": "REVOKE",

        "tablas": "TABLES",
        "tabla": "TABLE",
        "base_de_datos": "DATABASE",
        "base": "DATABASE",
        "estructura": "DESCRIBE",

        "todo": "*",
        "valores": "VALUES",
        "en": "INTO",
        "desde": "FROM",
        "donde": "WHERE",

        "enteros": "INT",
        "caracteres": "VARCHAR",
        "decimales": "DECIMAL",

        "y": "AND",
        "o": "OR"
    }

    #===TRADUCTOR A MySQL===#
    resultado = []

    for tok in tokens:
        lex = tok.lexema.lower()

        if lex in traducciones:
            resultado.append(traducciones[lex])
        else:
            resultado.append(tok.lexema)

    return " ".join(resultado)