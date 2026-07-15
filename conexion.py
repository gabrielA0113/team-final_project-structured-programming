import mysql.connector
from mysql.connector import Error

def crear_conexion():
    conexion = None
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="energia",
            port="3306"
        )

        if conexion.is_connected():
            print("Conexion exitosa a la base de datos MySQL")
            return conexion
        
    except Error as e:
        print (f"Error connection MySQL: {e} ")
        return None
    
def close_conection(conection):
    if conection is not None and conection.is_connected():
        conection.close()
        print ("The conection to MySQL has been closed ")

# Bloque de prueba para ejecutar el código
if __name__ == "__main__":
    # 1. Intentamos abrir la conexión y la guardamos en una variable
    mi_conexion = crear_conexion()
    
    # 2. Si la conexión tuvo éxito (no es None), la cerramos para probar la segunda función
    if mi_conexion:
        close_conection(mi_conexion)
