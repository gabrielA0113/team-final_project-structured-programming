# SISTEMA DE ESCRITORIO PARA EL CÁLCULO DE TICKETS (PROYECTO FINAL)
print("\033c")
import math

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
    "version": "2.0.1",
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

def generar_ticket_visual(nom, cons, sub, iv, tot):
    """Genera la visualización gráfica del ticket."""
    print(f"\n{CIAN}╔" + "═"*38 + "╗")
    print(f"║      {configuracion_sistema['nombre_app']} ║")
    print(f"╠" + "═"*38 + "╣")
    print(f"{RESET}  CLIENTE:  {nom.upper()}")
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
    print("    ESTADÍSTICAS DE LO SOLICITADO")
    print(f"{CIAN}==================================={RESET}")
    print(f"  Tickets emitidos: {tickets}")
    print(f"  Energía total:    {kwh_total:.2f} kWh")
    print(f"  Total en Caja:    $ {dinero_total} MXN")
    print(f"{CIAN}==================================={RESET}")
    # Mostramos historial guardado en la lista
    print(f"{AMARILLO}Últimos registros en memoria:{RESET}")
    for item in historial_de_operaciones:
        print(f" - {item['cliente']}: ${item['monto']}")

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
                        tipo = "Billete" if denominacion >= 20 else "Moneda"
                        print(f"  * {cantidad} {tipo}(s) de $ {denominacion} MXN")
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

while opcion_elegida != 3:
    print(f"\n{CIAN}=== {configuracion_sistema['nombre_app']} v{configuracion_sistema['version']} ==={RESET}")
    print("1. Registrar nuevo servicio")
    print("2. Reporte de ingresos")
    print("3. Salir")
    
    try:
        opcion_elegida = int(input(f"{AMARILLO}Seleccione opción:{RESET} "))
    except ValueError:
        print(f"{ROJO}Error: Debe ingresar un número entero.{RESET}")
        continue

    if opcion_elegida == 1:
        pregunta = 'si'
        while pregunta == 'si':
            nombre = solicitar_nombre()
            kwh_consumidos = solicitar_consumo(nombre)
            res_sub, res_iva, res_total = calcular_pago_cfe(kwh_consumidos)
            
            generar_ticket_visual(nombre, kwh_consumidos, res_sub, res_iva, res_total)
            gestionar_pago(res_total)

            # Agregando a la Lista (Array)
            registro_nuevo = {"cliente": nombre, "monto": res_total}
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
        mostrar_reporte_estadistico(contador_tickets, acumulador_kwh_total, acumulador_total_dinero)

    elif opcion_elegida == 3:
        print("Finalizando sistema. Gracias por usar CFE Ticket System.")
        
    else:
        print(f"{ROJO}Opción inválida, ingrese una opción válida (1-3).{RESET}")

# --- BITÁCORA DE IA ---
# 1. Se integró 'historial_de_operaciones' (Lista) para persistencia en ejecución.
# 2. Se integró 'configuracion_sistema' (Diccionario) para metadatos del programa.
# 3. Se mantuvo la estructura original.