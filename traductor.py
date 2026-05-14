"""
traductor.py — Traduce tokens MiniSQL a SQL estándar (MySQL)
CORRECCIONES:
  - "y"  → AND  (ya estaba, pero ahora llega correctamente desde el sintáctico)
  - "o"  → OR   (ídem)
  - "todo" → *  (corrección: antes salía como cadena "TODO")
  - Soporte para ORDENAR ASCENDENTE / DESCENDENTE → ORDER BY ASC/DESC
  - Soporte para LIMITE N → LIMIT N
  - AGRUPAR → GROUP BY
  - Limpieza de espacios antes de comas y punto y coma
"""

from lexer import Token

# Diccionario completo de palabras reservadas MiniSQL → SQL estándar
TRADUCCIONES = {
    "usar":              "USE",
    "crear":             "CREATE",
    "eliminar":          "DROP",
    "modificar":         "ALTER",
    "seleccionar":       "SELECT",
    "insertar":          "INSERT",
    "actualizar":        "UPDATE",
    "borrar":            "DELETE",
    "mostrar":           "SHOW",
    "conceder":          "GRANT",
    "revocar":           "REVOKE",
    "establecer":        "SET",
    "tablas":            "TABLES",
    "tabla":             "TABLE",
    "base_de_datos":     "DATABASES",
    "base":              "DATABASE",
    "bases":             "DATABASES",
    "estructura":        "DESCRIBE",
    "todo":              "*",
    "valores":           "VALUES",
    "en":                "INTO",
    "desde":             "FROM",
    "donde":             "WHERE",
    "teniendo":          "HAVING",
    "limite":            "LIMIT",
    "ordenar":           "ORDER BY",
    "agrupar":           "GROUP BY",
    "ascendente":        "ASC",
    "descendente":       "DESC",
    "enteros":           "INT",
    "caracteres":        "VARCHAR(255)",
    "decimales":         "DECIMAL(10,2)",
    "no_nulo":           "NOT NULL",
    "todos_privilegios": "ALL PRIVILEGES",
    "permisos":          "PRIVILEGES",
    "identificado_por":  "IDENTIFIED BY",
    "contraseña":        "PASSWORD",
    "y":                 "AND",
    "o":                 "OR",
    "a":                 "TO",
    "para":              "FOR",
    "usuario":           "USER",
    "perfil":            "PROFILE",
}


def traducir_minisql(tokens):
    """
    Convierte una lista de TokenResultado en una cadena SQL estándar.
    Maneja correctamente AND/OR, ORDER BY, GROUP BY, LIMIT y columnas múltiples.
    """
    partes = []
    i = 0
    n = len(tokens)

    while i < n:
        tok = tokens[i]
        lex = tok.lexema.lower()

        # Ignorar tokens de error léxico
        if Token.es_error(tok.tipo):
            i += 1
            continue

        traducido = TRADUCCIONES.get(lex)
        if traducido is not None:
            partes.append(traducido)
        else:
            partes.append(tok.lexema)

        i += 1

    # Unir con espacios
    resultado = " ".join(partes)

    # Limpiar espacios antes de comas, punto y coma, paréntesis de cierre
    resultado = _limpiar_espacios(resultado)

    return resultado


def _limpiar_espacios(sql):
    """
    Post-proceso para mejorar la legibilidad del SQL generado.
    - Elimina espacio ANTES de: , ; )
    - Elimina espacio DESPUÉS de: (
    """
    import re
    sql = re.sub(r'\s+([,;)])', r'\1', sql)
    sql = re.sub(r'(\()\s+', r'\1', sql)
    # Normalizar múltiples espacios
    sql = re.sub(r'  +', ' ', sql)
    return sql.strip()
