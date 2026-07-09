import mysql.connector


conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="biblioteca"
)

cursor = conexion.cursor()

def pedir_entero(mensaje):
    """Solicita un número entero utilizando recursividad."""

    try:
        return int(input(mensaje))
    except ValueError:
        print("Debes ingresar un número.")
        return pedir_entero(mensaje)


#CRUD

def registrar_libro():

    print("\n--- REGISTRAR LIBRO ---")
    titulo = input("Título: ")
    autor = input("Autor: ")
    anio = pedir_entero("Año: ")
    disponibles = pedir_entero("Cantidad disponible: ")

    sql = """
    INSERT INTO libros
    (titulo, autor, anio, disponibles)
    VALUES (%s,%s,%s,%s)
    """

    valores = (titulo, autor, anio, disponibles)

    cursor.execute(sql, valores)
    conexion.commit()

    print("Libro registrado correctamente.")


def consultar_libros():

    print("\n--- LISTA DE LIBROS ---")

    sql = "SELECT * FROM libros"

    cursor.execute(sql)

    registros = cursor.fetchall()

    if len(registros) == 0:
        print("No existen registros.")
        return

    for libro in registros:
        print(libro)


def buscar_libro():

    print("\n--- BUSCAR LIBRO ---")

    id_libro = pedir_entero("ID del libro: ")

    sql = "SELECT * FROM libros WHERE id=%s"

    cursor.execute(sql, (id_libro,))

    libro = cursor.fetchone()

    if libro is None:
        print("Libro no encontrado.")
    else:
        print(libro)


#
# MENÚ

def mostrar_menu():
    print(" SISTEMA DE BIBLIOTECA")
    print("**************************")
    print("1. Registrar libro")
    print("2. Mostrar libros")
    print("3. Buscar libro")
    print("4. Salir")


#Menu principal

def main():

    opcion = 0

    while opcion != 4:

        mostrar_menu()

        opcion = pedir_entero("Seleccione una opción: ")

        if opcion == 1:
            registrar_libro()

        elif opcion == 2:
            consultar_libros()

        elif opcion == 3:
            buscar_libro()

        elif opcion == 4:
            print("\nPrograma finalizado.")

        else:
            print("Opción no válida.")

    cursor.close()
    conexion.close()



main()