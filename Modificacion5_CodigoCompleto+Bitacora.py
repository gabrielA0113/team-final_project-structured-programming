# Modificacion5_CodigoCompleto+BitacoraDeIA 
print("\033c")
import math
import mysql.connector
from mysql.connector import Error

# --- IMPORTACIÓN DE TU ARCHIVO DE CONEXIÓN ---
from conexion import crear_conexion, close_conection

#--- CONSTANTES
IVA_VALOR = 0.16
LIMITE_BASICO = 75
LIMITE_INTERMEDIO = 140
PRECIO_B = 1.023
PRECIO_I = 1.247
PRECIO_E = 3.646

#ESTRUCTURAS DE DATOS PARA EL PROYECTO
# Lista para almacenar registros temporales de los tickets generados
historial_de_operaciones = []
# Diccionario para configuraciones avanzadas del sistema
configuracion_sistema = {
    "nombre_app": "CFE Ticket System",
    "modo_debug": False
}

#--- DEL CODIGO (COLORES)
CIAN = "\033[36m"
AMARILLO = "\033[33m"
ROJO = "\033[31m"
RESET = "\033[0m"

# --- VARIABLES GLOBALES
contador_tickets = 0
acumulador_total_dinero = 0
acumulador_kwh_total = 0 


# ==========================================
# FUNCIONES DE BASE DE DATOS (CONEXIÓN DE TABLAS)
# ==========================================

def registrar_ticket_db(nombre, correo, telefono, tipo, consumo, total_dinero):
    """Inserta o actualiza el usuario en 'usuario' y vincula el ticket en 'tickets'."""
    conexion = crear_conexion()
    if conexion is None:
        print(f"{ROJO}Error: No hay conexión a la BD. El ticket no se guardará en MySQL.{RESET}")
        return False
    
    try:
        cursor = conexion.cursor()
        
        # 1. Buscamos si el usuario ya existe por su nombre
        query_buscar = "SELECT id_usuario FROM usuario WHERE nombre = %s"
        cursor.execute(query_buscar, (nombre.upper(),))
        resultado_usuario = cursor.fetchone()
        
        if resultado_usuario:
            id_usuario = resultado_usuario[0]
            # Si el usuario ya existe, actualizamos sus datos (por si cambió de correo, teléfono o tipo)
            query_actualizar = """
                UPDATE usuario SET correo = %s, telefono = %s, tipo = %s WHERE id_usuario = %s
            """
            cursor.execute(query_actualizar, (correo, telefono, tipo, id_usuario))
            conexion.commit()
            print(f"{AMARILLO}Datos del usuario existente actualizados.{RESET}")
        else:
            # 2. Si no existe, lo creamos con los datos reales que escribió en la consola
            query_insertar_usuario = """
                INSERT INTO usuario (nombre, correo, telefono, tipo) 
                VALUES (%s, %s, %s, %s)
            """
            datos_usuario = (nombre.upper(), correo, telefono, tipo)
            cursor.execute(query_insertar_usuario, datos_usuario)
            conexion.commit() 
            id_usuario = cursor.lastrowid # Obtenemos el ID generado automáticamente
        
        # 3. Guardamos el ticket conectándolo con el id_usuario en la columna 'cliente'
        query_ticket = """
            INSERT INTO tickets (cliente, consumo, cantidad, fecha)
            VALUES (%s, %s, %s, CURDATE())
        """
        cursor.execute(query_ticket, (str(id_usuario), consumo, total_dinero))
        conexion.commit()
        
        print(f"{CIAN}Ticket guardado y conectado en MySQL con Éxito (Usuario ID: {id_usuario})!{RESET}")
        return True
        
    except Error as e:
        print(f"{ROJO}Error al intentar interactuar con MySQL: {e}{RESET}")
        conexion.rollback() # Revierte cambios si ocurre un error inesperado
        return False
    finally:
        cursor.close()
        close_conection(conexion)


def obtener_reporte_db():
    """Extrae las estadísticas históricas directo de la base de datos."""
    conexion = crear_conexion()
    if conexion is None:
        return 0, 0.0, 0.0
    
    try:
        cursor = conexion.cursor()
        query = "SELECT COUNT(id_ticket), SUM(consumo), SUM(cantidad) FROM tickets"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        total_tickets = resultado[0] if resultado[0] is not None else 0
        energia_total = float(resultado[1]) if resultado[1] is not None else 0.0
        caja_total = float(resultado[2]) if resultado[2] is not None else 0.0
        
        return total_tickets, energia_total, caja_total
        
    except Error as e:
        print(f"{ROJO}Error al leer estadísticas de MySQL: {e}{RESET}")
        return 0, 0.0, 0.0
    finally:
        cursor.close()
        close_conection(conexion)


def eliminar_usuario_db(nombre):
    """Elimina un usuario y sus registros asociados de la base de datos."""
    conexion = crear_conexion()
    if conexion is None:
        print(f"{ROJO}Error: No hay conexión a la BD.{RESET}")
        return False
    
    try:
        cursor = conexion.cursor()
        # 1. Buscar si el usuario existe
        query_buscar = "SELECT id_usuario FROM usuario WHERE nombre = %s"
        cursor.execute(query_buscar, (nombre.upper(),))
        resultado = cursor.fetchone()
        
        if not resultado:
            print(f"{ROJO}Error: El usuario no existe en la base de datos.{RESET}")
            return False
            
        id_usuario = resultado[0]
        
        # 2. Eliminar registros dependientes en la tabla 'tickets' primero (por restricciones de llave foránea)
        query_tickets = "DELETE FROM tickets WHERE cliente = %s"
        cursor.execute(query_tickets, (str(id_usuario),))
        
        # 3. Eliminar al usuario
        query_usuario = "DELETE FROM usuario WHERE id_usuario = %s"
        cursor.execute(query_usuario, (id_usuario,))
        
        conexion.commit()
        print(f"{CIAN}Usuario y sus tickets asociados eliminados exitosamente de MySQL.{RESET}")
        return True
        
    except Error as e:
        print(f"{ROJO}Error al eliminar en MySQL: {e}{RESET}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        close_conection(conexion)
def modificar_usuario_db(nombre):
    """Modifica los datos de un usuario existente."""
    conexion = crear_conexion()

    if conexion is None:
        print(f"{ROJO}Error: No hay conexión a la BD.{RESET}")
        return False

    try:
        cursor = conexion.cursor()

        query_buscar = "SELECT id_usuario FROM usuario WHERE nombre = %s"
        cursor.execute(query_buscar, (nombre.upper(),))
        resultado = cursor.fetchone()

        if not resultado:
            print(f"{ROJO}Error: El usuario no existe en la base de datos.{RESET}")
            return False

        id_usuario = resultado[0]

        print(f"\n{AMARILLO}Ingrese los nuevos datos:{RESET}")

        correo = solicitar_correo()
        telefono = solicitar_telefono()
        tipo = solicitar_tipo()

        query_actualizar = """
            UPDATE usuario
            SET correo = %s,
                telefono = %s,
                tipo = %s
            WHERE id_usuario = %s
        """

        cursor.execute(query_actualizar, (correo, telefono, tipo, id_usuario))
        conexion.commit()

        print(f"{CIAN}Usuario actualizado correctamente.{RESET}")
        return True

    except Error as e:
        print(f"{ROJO}Error al actualizar en MySQL: {e}{RESET}")
        conexion.rollback()
        return False

    finally:
        cursor.close()
        close_conection(conexion)

# ==========================================
# FUNCIONES PARA EL NEGOCIO
# ==========================================

def calcular_pago_cfe(consumo_kwh):
    """Calcula subtotal, IVA y total de acuerdo a tarifas CFE."""
    costo_basico = 0.0
    costo_intermedio = 0.0
    costo_excedente = 0.0
    
    if consumo_kwh <= LIMITE_BASICO:
        subtotal = consumo_kwh * PRECIO_B
    elif consumo_kwh <= LIMITE_INTERMEDIO:
        costo_basico = LIMITE_BASICO * PRECIO_B
        costo_intermedio = (consumo_kwh - LIMITE_BASICO) * PRECIO_I
        subtotal = costo_basico + costo_intermedio
    else:
        costo_basico = LIMITE_BASICO * PRECIO_B
        costo_intermedio = (LIMITE_INTERMEDIO - LIMITE_BASICO) * PRECIO_I
        costo_excedente = (consumo_kwh - LIMITE_INTERMEDIO) * PRECIO_E
        subtotal = costo_basico + costo_intermedio + costo_excedente
            
    iva = subtotal * IVA_VALOR
    total = subtotal + iva
    
    return math.floor(subtotal), iva, math.ceil(total)

def generar_ticket_visual(nom, cons, sub, iv, tot, tip):
    """Genera la visualización gráfica del ticket."""
    print(f"\n{CIAN}╔" + "═"*38 + "╗")
    print(f"║      {configuracion_sistema['nombre_app']} ║")
    print(f"╠" + "═"*38 + "╣")
    print(f"{RESET}  CLIENTE:  {nom.upper()}")
    print(f"  TIPO:     {tip.upper()}")
    print(f"  CONSUMO:  {cons} kWh")
    print(f"{CIAN}╟" + "─"*38 + "╢")
    print(f"{RESET}  SUBTOTAL: $ {sub}")
    print(f"  IVA:      $ {iv:.2f}")
    print(f"  TOTAL:    $ {tot} MXN")
    print(f"{CIAN}╚" + "═"*38 + "╝")
    print(f"{AMARILLO}--------------------------------------------{RESET}")

# ==========================================
# FUNCIONES DE VALIDACIÓN Y GESTIÓN
# ==========================================

def solicitar_nombre():
    """Valida y retorna un nombre de cliente limpio."""
    while True:
        nombre = input("\nNombre del cliente: ").strip()
        if nombre.replace(" ", "").isalnum() and len(nombre) > 0:
            return nombre
        print(f"{ROJO}Error: Solo se permiten letras, números y espacios.{RESET}")

def solicitar_correo():
    """Valida que el correo contenga un '@' y un punto."""
    while True:
        correo = input("Correo electrónico: ").strip()
        if "@" in correo and "." in correo and len(correo) > 5:
            return correo
        print(f"{ROJO}Error: Ingrese un correo electrónico válido (ejemplo@dominio.com).{RESET}")

def solicitar_telefono():
    """Valida que el teléfono contenga únicamente números."""
    while True:
        telefono = input("Teléfono (10 dígitos): ").strip()
        if telefono.isdigit() and len(telefono) >= 8:
            return telefono
        print(f"{ROJO}Error: El teléfono solo debe contener números (mínimo 8 dígitos).{RESET}")

def solicitar_tipo():
    """Valida y retorna el tipo de lugar (Residencia, Negocio, Industria, etc.)."""
    while True:
        tipo = input("Tipo de inmueble (Residencia / Comercio / Industria): ").strip().capitalize()
        if len(tipo) > 2 and tipo.replace(" ", "").isalpha():
            return tipo
        print(f"{ROJO}Error: Ingrese un tipo válido (solo letras).{RESET}")

def solicitar_consumo(nombre):
    """Valida y retorna un consumo numérico flotante positivo."""
    while True:
        try:
            kwh_consumidos = float(input(f"Consumo de {nombre} (kWh): "))
            if kwh_consumidos > 0:
                return kwh_consumidos
            print(f"{ROJO}Error: El consumo debe ser mayor a 0.{RESET}")
        except ValueError:
            print(f"{ROJO}Error: Debe ingresar un valor numérico válido.{RESET}")

def mostrar_reporte_estadistico(tickets, kwh_total, dinero_total):
    """Imprime el cierre de caja y estadísticas acumuladas."""
    print(f"\n{CIAN}==================================={RESET}")
    print("    ESTADÍSTICAS HISTÓRICAS EN BD")
    print(f"{CIAN}==================================={RESET}")
    print(f"  Tickets emitidos: {tickets}")
    print(f"  Energía total:    {kwh_total:.2f} kWh")
    print(f"  Total en Caja:    $ {dinero_total} MXN")
    print(f"{CIAN}==================================={RESET}")
    print(f"{AMARILLO}Registros en memoria de esta sesión:{RESET}")
    for item in historial_de_operaciones:
        print(f" - {item['cliente']} ({item['tipo']}): ${item['monto']}")

def gestionar_pago(total_a_pagar):
    """Administra el cobro en efectivo y activa el desglose."""
    while True:
        try:
            pago_cliente = float(input(f"¿Con cuánto paga el cliente? (Total: $ {total_a_pagar} MXN): "))
            if pago_cliente >= total_a_pagar:
                cambio = pago_cliente - total_a_pagar
                print(f"\n{CIAN}Cambio total a devolver: $ {cambio:.2f} MXN{RESET}")
                if cambio > 0:
                    desglose = desglose_cambio_recursivo(math.floor(cambio))
                    print(f"{AMARILLO}Desglose sugerido de cambio:{RESET}")
                    for denominacion, cantidad in desglose.items():
                        tipo_num = "Billete" if denominacion >= 20 else "Moneda"
                        print(f"  * {cantidad} {tipo_num}(s) de $ {denominacion} MXN")
                return
            print(f"{ROJO}Error: El pago debe ser igual o mayor al total.{RESET}")
        except ValueError:
            print(f"{ROJO}Error: Ingrese una cantidad de dinero válida.{RESET}")

# ==========================================
# FUNCION RECURSIVA
# ==========================================

def desglose_cambio_recursivo(monto, billetes=[500, 200, 100, 50, 20, 10, 5, 2, 1], idx=0, desglose=None):
    """Algoritmo recursivo para desglose de cambio."""
    if desglose is None:
        desglose = {}
    if monto <= 0 or idx >= len(billetes):
        return desglose
    
    denominacion_actual = billetes[idx]
    cantidad_piezas = int(monto // denominacion_actual)
    
    if cantidad_piezas > 0:
        desglose[denominacion_actual] = cantidad_piezas
        
    nuevo_monto = monto % denominacion_actual
    return desglose_cambio_recursivo(nuevo_monto, billetes, idx + 1, desglose)

# ===================================
# 4. MENU DEL CONTROL PRINCIPAL
# ===================================

opcion_elegida = 0

while opcion_elegida != 5:
    print(f"\n{CIAN}=== {configuracion_sistema['nombre_app']} ==={RESET}")
    print("1. Registrar nuevo servicio")
    print("2. Reporte de ingresos")
    print("3. Modificar registro de usuario")
    print("4. Eliminar registro de usuario")
    print("5. Salir")
    
    try:
        opcion_elegida = int(input(f"{AMARILLO}Seleccione opción:{RESET} "))
    except ValueError:
        print(f"{ROJO}Error: Debe ingresar un número entero.{RESET}")
        continue

    if opcion_elegida == 1:
        pregunta = 'si'
        while pregunta == 'si':
            # --- SOLICITUD DE TODOS LOS DATOS DEL USUARIO ---
            nombre = solicitar_nombre()
            correo = solicitar_correo()
            telefono = solicitar_telefono()
            tipo = solicitar_tipo()
            
            kwh_consumidos = solicitar_consumo(nombre)
            res_sub, res_iva, res_total = calcular_pago_cfe(kwh_consumidos)
            
            generar_ticket_visual(nombre, kwh_consumidos, res_sub, res_iva, res_total, tipo)
            gestionar_pago(res_total)

            # --- REGISTRO CON TODOS LOS CAMPOS EN LA BASE DE DATOS ---
            registrar_ticket_db(nombre, correo, telefono, tipo, kwh_consumidos, res_total)

            # Agregando a la Lista (Array) local para cumplir el requerimiento de memoria
            registro_nuevo = {"cliente": nombre, "tipo": tipo, "monto": res_total}
            historial_de_operaciones.append(registro_nuevo)

            # Actualización de contadores globales
            contador_tickets += 1
            acumulador_total_dinero += res_total
            acumulador_kwh_total += kwh_consumidos

            while True:
                pregunta = input("\n¿Desea agregar otro cliente? (si/no): ").lower().strip()
                if pregunta in ["si", "no"]:
                    break
                else:
                    print(f"{ROJO}Error: Solo responda 'si' o 'no'.{RESET}")

    elif opcion_elegida == 2:
        tickets_bd, kwh_bd, dinero_bd = obtener_reporte_db()
        mostrar_reporte_estadistico(tickets_bd, kwh_bd, dinero_bd)

    elif opcion_elegida == 3:
        nombre = solicitar_nombre()
        modificar_usuario_db(nombre)

    elif opcion_elegida == 4:
        nombre_a_borrar = solicitar_nombre()
        eliminar_usuario_db(nombre_a_borrar)

    elif opcion_elegida == 5:
         print("Finalizando sistema. Gracias por usar CFE Ticket System.")

    else:
        print(f"{ROJO}Opción inválida, ingrese una opción válida (1-5).{RESET}")

# --- BITÁCORA DE IA ---
# 1. Se integró 'historial_de_operaciones' (Lista) y 'configuracion_sistema' (Diccionario).
# 2. Se crearon funciones de validación para correo, teléfono y tipo de inmueble.
# 3. La función registrar_ticket_db realiza un UPDATE si el usuario ya existe, o un INSERT si es nuevo.
# 4. El ticket visual y el historial temporal ahora muestran el tipo de inmueble.
# 5. Se eliminó la Opción 4 y toda referencia a la versión del sistema.
# 6. Se implementó la función 'eliminar_usuario_db' para completar la operación Delete (CRUD).
# 7. Se actualizó el menú principal con la Opción 3 para eliminación y la Opción 4 para salida.