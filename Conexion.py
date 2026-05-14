import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

#===== CONEXIÓN A MySQL ======#
def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conexion
    except Exception as e:
        print(f"Error al conectar: {e}")
        return None