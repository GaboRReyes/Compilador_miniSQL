import mysql.connector
#===== CONEXIÓN A MySQL ======#
def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            user='root', #usuario de MySQL
            password='linces2022', #contraseña de MysQL
            host='localhost', #servidor local
            port='3306' #puerto por defecto de MySQL
        )
        return conexion
    except Exception as e:
        print(f"Error al conectar: {e}")
        return None
    