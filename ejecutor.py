from Conexion import obtener_conexion
from traductor import traducir_minisql
from lexer import AnalizadorLexico

def ejecutar_minisql(codigo):

    lx = AnalizadorLexico(codigo)
    lx.analizar()

    if lx.errores:
        return "Error léxico, no se ejecuta SQL"

    sql = traducir_minisql(lx.tokens)

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    #===Ejecutar SQL traducido a MySQL===#
    try:
        consultas = sql.split(";")
        resultado_final = ""

        for consulta in consultas:
            consulta = consulta.strip()
            if consulta == "":
                continue

            print(f"Ejecutando: [{consulta}]")

            cursor.execute(consulta)
            #===Consultas que devuelven resultados===#
            if consulta.upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
                resultados = cursor.fetchall()
                resultado_final += f"\n>> {consulta}\n"

                for fila in resultados:
                    resultado_final += " | ".join(str(x) for x in fila) + "\n"

        conexion.commit()

        if resultado_final.strip() == "":
            return "Consultas ejecutadas correctamente"

        return resultado_final

    finally:
        conexion.close()