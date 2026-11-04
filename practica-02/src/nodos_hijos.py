"""Subclases de NodoIoT: NodoSensor y NodoActuador."""

import math
import random

from nodo_iot import NodoIoT


def _es_numero(valor) -> bool:
    """True si es int o float real (no bool, no NaN, no infinito)."""
    return (isinstance(valor, (int, float))
            and not isinstance(valor, bool)
            and math.isfinite(valor))


class NodoSensor(NodoIoT):
    """Nodo que mide una magnitud física y avisa si supera su límite."""

    def __init__(self, id_dispositivo: str, ip: str, ubicacion: str,
                 magnitud: str, unidad: str, rango_min: float,
                 rango_max: float, limite_alerta: float):
        # Herencia: se reutiliza el constructor del padre.
        super().__init__(id_dispositivo, ip, ubicacion)

        if not (_es_numero(rango_min) and _es_numero(rango_max)):
            raise TypeError("El rango del sensor debe ser numérico.")
        if rango_min >= rango_max:
            raise ValueError("rango_min debe ser menor que rango_max.")

        self.magnitud = magnitud
        self.unidad = unidad
        self.__rango_min = float(rango_min)
        self.__rango_max = float(rango_max)
        self.__lectura = float(rango_min)
        self.__limite_alerta = float(rango_max)
        # Se asigna con el setter para validar también el valor inicial.
        self.limite_alerta = limite_alerta

    @property
    def limite_alerta(self) -> float:
        """GET del límite de alerta."""
        return self.__limite_alerta

    @limite_alerta.setter
    def limite_alerta(self, valor: float) -> None:
        """SET con validación: número dentro del rango real del sensor."""
        if not _es_numero(valor):
            raise TypeError("El límite de alerta debe ser un número válido.")
        if not self.__rango_min <= valor <= self.__rango_max:
            raise ValueError(
                f"Límite {valor} fuera del rango del sensor "
                f"({self.__rango_min} a {self.__rango_max} {self.unidad})."
            )
        self.__limite_alerta = float(valor)

    @property
    def lectura(self) -> float:
        return self.__lectura

    @property
    def rango_min(self) -> float:
        return self.__rango_min

    @property
    def rango_max(self) -> float:
        return self.__rango_max
    
    def leer(self) -> float:
        """Simula una medición dentro del rango del sensor."""
        self.__lectura = round(
            random.uniform(self.__rango_min, self.__rango_max), 1)
        return self.__lectura

    def enviar_telemetria(self) -> None:
        """Polimorfismo: un sensor reporta su lectura actual."""
        lectura = self.leer()
        aviso = "  [ALERTA: supera el límite]" if lectura > self.__limite_alerta else ""
        print(f"[{self.id_dispositivo}] {self.magnitud}: {lectura} {self.unidad} "
              f"(límite {self.__limite_alerta} {self.unidad}){aviso}")

        

class NodoActuador(NodoIoT):
    """Nodo que acciona un dispositivo (relé, motor, ventilador)."""

    def __init__(self, id_dispositivo: str, ip: str, ubicacion: str, tipo: str):
        # Herencia: se reutiliza el constructor del padre.
        super().__init__(id_dispositivo, ip, ubicacion)
        self.tipo = tipo
        self.__estado_activo = False
        self.__potencia_pwm = 0

    @property
    def potencia_pwm(self) -> int:
        """GET de la potencia PWM (%)."""
        return self.__potencia_pwm

    @potencia_pwm.setter
    def potencia_pwm(self, valor: int) -> None:
        """SET con validación: entero entre 0 y 100."""
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError("La potencia PWM debe ser un número entero.")
        if not 0 <= valor <= 100:
            raise ValueError(f"Potencia {valor}% fuera de rango (0 a 100).")
        self.__potencia_pwm = valor

    @property
    def estado_activo(self) -> bool:
        """GET del estado. Solo cambia con encender() y apagar()."""
        return self.__estado_activo

    def encender(self, potencia: int = 100) -> None:
        # Se valida primero; si es inválida no cambia el estado.
        self.potencia_pwm = potencia
        self.__estado_activo = True
        print(f"[{self.id_dispositivo}] {self.tipo} encendido al "
              f"{self.__potencia_pwm}% de potencia.")

    def apagar(self) -> None:
        self.__estado_activo = False
        self.__potencia_pwm = 0
        print(f"[{self.id_dispositivo}] {self.tipo} apagado.")

    def enviar_telemetria(self) -> None:
        """Polimorfismo: un actuador reporta su estado."""
        if self.__estado_activo:
            print(f"[{self.id_dispositivo}] {self.tipo}: ENCENDIDO "
                  f"({self.__potencia_pwm}% PWM)")
        else:
            print(f"[{self.id_dispositivo}] {self.tipo}: APAGADO")