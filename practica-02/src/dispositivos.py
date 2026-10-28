from nodo_iot import NodoIoT

class NodoSensor(NodoIoT):
    def __init__(self, id_dispositivo: str, ip: str, ubicacion: str, limite_alerta: float = 50.0):
        super().__init__(id_dispositivo, ip, ubicacion)
        self.__limite_alerta = limite_alerta
        self.lectura_actual = 0.0