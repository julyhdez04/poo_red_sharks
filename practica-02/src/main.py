"""Script principal: simulación interactiva de la red IoT."""
 
from nodos_hijos import NodoSensor, NodoActuador
 
 
def main() -> None:
    sensor_temp = NodoSensor("TEMP-01", "192.168.1.10", "Invernadero",
                             "Temperatura", "°C", -10, 60, 30)
    sensor_luz = NodoSensor("LUZ-01", "192.168.1.11", "Invernadero",
                            "Luz", "lux", 0, 1000, 800)
    actuador_ventilador = NodoActuador("VENT-01", "192.168.1.20", "Invernadero",
                                       "Ventilador")
 
    # Lista mixta: cada objeto responde según su propia clase (polimorfismo)
    red_iot = [sensor_temp, actuador_ventilador, sensor_luz]
 
    for dispositivo in red_iot:
        dispositivo.conectar()
 
    for dispositivo in red_iot:
        dispositivo.enviar_telemetria()
 
 
if __name__ == "__main__":
    main()
 
