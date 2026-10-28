class NodoIoT:
    def __init__(self, id_dispositivo: str, ip: str, ubicacion: str):
        self.id_dispositivo = id_dispositivo
        self.ip = ip
        self.ubicacion = ubicacion
        self.conectado = False

    def conectar(self):
        self.conectado = True
        print(f"[{self.id_dispositivo}] Conectado exitosamente a la red ({self.ip}).")

    def enviar_telemetria(self):
        print(f"[{self.id_dispositivo}] Enviando telemetría de {self.ubicacion}...")