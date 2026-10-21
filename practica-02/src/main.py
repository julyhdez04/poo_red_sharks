"""Script principal: simulación interactiva de la red IoT."""
 
from nodos_hijos import NodoSensor, NodoActuador
 
 
def pedir_numero(mensaje: str, tipo=float):
    try:
        return tipo(input(mensaje))
    except ValueError:
        print("  Entrada no válida: se esperaba un número.")
        return None
 
 
def elegir(diccionario: dict, etiqueta: str):
    print(f"  {etiqueta} disponibles: {', '.join(diccionario)}")
    return diccionario.get(input("  ID: ").strip())
 
 
def main() -> None:
    sensor_temp = NodoSensor("TEMP-01", "192.168.1.10", "Invernadero",
                             "Temperatura", "°C", -10, 60, 30)
    sensor_luz = NodoSensor("LUZ-01", "192.168.1.11", "Invernadero",
                            "Luz", "lux", 0, 1000, 800)
    actuador_ventilador = NodoActuador("VENT-01", "192.168.1.20", "Invernadero",
                                       "Ventilador")
 
    # Lista mixta: cada objeto responde según su propia clase (polimorfismo)
    red_iot = [sensor_temp, actuador_ventilador, sensor_luz]
    sensores = {"TEMP-01": sensor_temp, "LUZ-01": sensor_luz}
    actuadores = {"VENT-01": actuador_ventilador}
 
    menu = ("\n=== RED IoT - HMI ===\n"
            "1. Conectar todos los nodos\n"
            "2. Telemetría de toda la red\n"
            "3. Cambiar límite de alerta de un sensor\n"
            "4. Encender un actuador\n"
            "5. Apagar un actuador\n"
            "0. Salir")
 
    while True:
        print(menu)
        opcion = input("Opción: ").strip()
 
        if opcion == "1":
            for dispositivo in red_iot:
                dispositivo.conectar()
        elif opcion == "2":
            for dispositivo in red_iot:
                dispositivo.enviar_telemetria()
        elif opcion == "3":
            sensor = elegir(sensores, "Sensores")
            valor = pedir_numero("  Nuevo límite: ") if sensor else None
            if valor is not None:
                try:
                    sensor.limite_alerta = valor
                    print(f"  Límite actualizado a {sensor.limite_alerta}")
                except (ValueError, TypeError) as error:
                    print(f"  Rechazado: {error}")
            elif sensor is None:
                print("  ID no encontrado.")
        elif opcion == "4":
            actuador = elegir(actuadores, "Actuadores")
            if actuador is None:
                print("  ID no encontrado.")
                continue
            potencia = pedir_numero("  Potencia PWM (0-100): ", int)
            if potencia is not None:
                try:
                    actuador.encender(potencia)
                except (ValueError, TypeError) as error:
                    print(f"  Rechazado: {error}")
        elif opcion == "5":
            actuador = elegir(actuadores, "Actuadores")
            if actuador is not None:
                actuador.apagar()
            else:
                print("  ID no encontrado.")
        elif opcion == "0":
            print("Fin de la simulación.")
            break
        else:
            print("Opción no válida.")
 
 
if __name__ == "__main__":
    main()
 
