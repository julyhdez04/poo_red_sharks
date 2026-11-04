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