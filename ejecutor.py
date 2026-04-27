from Conexion import obtener_conexion
from traductor import traducir_minisql
from lexer import AnalizadorLexico

def ejecutar_minisql(codigo):

    lx = AnalizadorLexico(codigo)
    lx.analizar()

    if lx.errores:
        return "Error léxico, no se ejecuta SQL"

    # 2. TRADUCTOR usando tokens
    sql = traducir_minisql(lx.tokens)

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        consultas = sql.split(";")
        resultado_final = ""

        for consulta in consultas:
            consulta = consulta.strip()
            if consulta == "":
                continue

            try:
                print(f"Ejecutando: [{consulta}]")

                cursor.execute(consulta)

                if consulta.upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
                    resultados = cursor.fetchall()
                    resultado_final += f"\n>> {consulta}\n"

                    for fila in resultados:
                        resultado_final += " | ".join(str(x) for x in fila) + "\n"

            except Exception as e:
                return f"Error en consulta: '{consulta}'\n{e}"

        conexion.commit()
        return resultado_final if resultado_final else "Consultas ejecutadas correctamente"

    finally:
        conexion.close()