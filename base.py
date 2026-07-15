# SISTEMA DE ESCRITORIO PARA EL CÁLCULO DE TICKETS (PROYECTO FINAL)
print("\033c")
import math

IVA_VALOR = 0.16
LIMITE_BASICO = 75
LIMITE_INTERMEDIO = 140
PRECIO_B = 1.023
PRECIO_I = 1.247
PRECIO_E = 3.646

# --- COLORES ANSI ---
CIAN = "\033[36m"
AMARILLO = "\033[33m"
ROJO = "\033[31m"
RESET = "\033[0m"

contador_tickets = 0
acumulador_total_dinero = 0
acumulador_kwh_total = 0 

def calcular_pago_cfe(consumo_kwh):
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
    print(f"\n{CIAN}╔" + "═"*38 + "╗")
    print(f"║       SISTEMA DE CÁLCULO DE TICKETS  ║")
    print(f"╠" + "═"*38 + "╣")
    print(f"{RESET}  CLIENTE:  {nom.upper()}")
    print(f"  CONSUMO:  {cons} kWh")
    print(f"{CIAN}╟" + "─"*38 + "╢")
    print(f"{RESET}  SUBTOTAL: $ {sub}")
    print(f"  IVA:      $ {iv:.2f}")
    print(f"  TOTAL:    $ {tot} MXN")
    print(f"{CIAN}╚" + "═"*38 + "╝")
    print(f"{AMARILLO}--------------------------------------------{RESET}")

opcion_elegida = 0

while opcion_elegida != 3:
    print(f"\n{CIAN}=== SISTEMA DE GESTIÓN CFE ==={RESET}")
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

            while True:
                nombre = input("\nNombre del cliente: ")
                if nombre.replace(" ", "").isalnum():
                    break
                else:
                    print(f"{ROJO}Error: Solo se permiten letras y números.{RESET}")

            while True:
                try:
                    kwh_consumidos = float(input(f"Consumo de {nombre}: "))
                    if kwh_consumidos > 0:
                        break
                    else:
                        print(f"{ROJO}Error: El consumo debe ser positivo.{RESET}")
                except ValueError:
                    print(f"{ROJO}Error: Debe ingresar un número válido.{RESET}")

            res_sub, res_iva, res_total = calcular_pago_cfe(kwh_consumidos)
            generar_ticket_visual(nombre, kwh_consumidos, res_sub, res_iva, res_total)

            contador_tickets += 1
            acumulador_total_dinero += res_total
            acumulador_kwh_total += kwh_consumidos

            while True:
                pregunta = input("¿Desea agregar otro cliente? (si/no): ").lower()
                if pregunta in ["si", "no"]:
                    break
                else:
                    print(f"{ROJO}Error: Solo responda 'si' o 'no'.{RESET}")

    elif opcion_elegida == 2:
        print(f"\n===============================")
        print("ESTADÍSTICAS DE LO SOLICITADO")
        print("===============================")
        print(f"  Tickets: {contador_tickets}")
        print(f"  Energía: {acumulador_kwh_total:.2f} kWh")
        print(f"  Caja:    $ {acumulador_total_dinero}")
        print(f"==================================")

    elif opcion_elegida == 3:
        print("Finalizando programa...")
        
    else:
        print(f"{ROJO}Opción inválida, ingrese una opción válida.{RESET}")