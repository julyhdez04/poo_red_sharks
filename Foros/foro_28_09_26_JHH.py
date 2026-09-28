#!/usr/bin/env python3
"""
Actividad: Aplicando abstracción, herencia, polimorfismo y encapsulamiento
Concepto: ENCAPSULAMIENTO
Tema: Bomba de enfriamiento (ejemplo libre, independiente de las prácticas)

Los comentarios marcados con [INFOGRAFÍA] responden a los puntos de la
"Lista de Verificación: ¿Aplicaste Correctamente el Encapsulamiento?"
"""


class BombaEnfriamiento:

    # ------------------------------------------------------------------
    # CONTROL DE ATRIBUTOS Y ESTADO
    # ------------------------------------------------------------------
    def __init__(self, nombre: str, potencia_max: float = 100.0):
        # [INFOGRAFÍA] ¿Atributos declarados como privados?  SÍ.
        # El doble guion bajo (__) hace que Python cambie internamente el
        # nombre del atributo (name mangling), así que desde afuera
        # "bomba.__potencia" no existe. Esto oculta los datos del objeto
        # y evita alteraciones no controladas desde el exterior.
        # (Nota: en Python la privacidad es una protección fuerte por
        # convención; no es un candado absoluto como en Java o C++.)
        self.__nombre = nombre
        self.__potencia_max = potencia_max
        self.__potencia = 0.0
        self.__encendida = False

    # [INFOGRAFÍA] ¿Métodos Get y Set implementados?  SÍ.
    # En Python se hacen con @property (get) y @<nombre>.setter (set).
    # Son la única vía para consultar o cambiar los valores privados.

    @property
    def nombre(self) -> str:
        """GET del nombre. No tiene setter: es de solo lectura."""
        return self.__nombre

    @property
    def potencia(self) -> float:
        """GET de la potencia actual (%)."""
        return self.__potencia

    @potencia.setter
    def potencia(self, valor: float):
        """SET de la potencia, con lógica de validación."""
        # [INFOGRAFÍA] ¿Lógica de validación en los Setters?  SÍ.
        # Las reglas viven DENTRO del setter, para impedir que se asignen
        # datos inválidos (texto, negativos o por encima del máximo).
        if not isinstance(valor, (int, float)) or isinstance(valor, bool):
            raise TypeError("La potencia debe ser un número.")
        if not self.__valor_en_rango(valor):
            raise ValueError(
                f"Potencia {valor}% fuera de rango (0% - {self.__potencia_max}%)."
            )
        self.__potencia = float(valor)

    @property
    def encendida(self) -> bool:
        """GET del estado. Solo se cambia con iniciar/detener_proceso()."""
        return self.__encendida

    # ------------------------------------------------------------------
    # VISIBILIDAD E INTERFAZ DE LA CLASE
    # ------------------------------------------------------------------

    # [INFOGRAFÍA] ¿Métodos internos marcados como privados?  SÍ.
    # Estas funciones de validación y cálculo son lógica interna: se
    # protegen con __ para que nadie las ejecute desde afuera.

    def __valor_en_rango(self, valor: float) -> bool:
        """Privado: regla de validación usada por el setter."""
        return 0.0 <= valor <= self.__potencia_max

    def __calcular_caudal(self) -> float:
        """Privado: cálculo interno del caudal (0.5 L/min por cada 1%)."""
        return self.__potencia * 0.5

    # [INFOGRAFÍA] ¿Métodos públicos como punto de entrada?  SÍ.
    # Estas son las funciones claras que usa el exterior; ellas gestionan
    # la llamada a los procesos privados.

    def iniciar_proceso(self, potencia: float) -> str:
        """Público: enciende la bomba y fija la potencia."""
        self.potencia = potencia      # pasa por el setter (se valida)
        self.__encendida = True
        return f"{self.__nombre} ENCENDIDA -> {self.__potencia:.1f}% | Caudal: {self.__calcular_caudal():.1f} L/min"

    def detener_proceso(self) -> str:
        """Público: apaga la bomba y deja la potencia en 0."""
        self.__potencia = 0.0
        self.__encendida = False
        return f"{self.__nombre} APAGADA"

    def __str__(self) -> str:
        estado = "ON" if self.__encendida else "OFF"
        return f"{self.__nombre} | {estado} | {self.__potencia:.1f}%"


# ----------------------------------------------------------------------
# DEMOSTRACIÓN
# ----------------------------------------------------------------------
def main():
    bomba = BombaEnfriamiento("Bomba de Enfriamiento")

    print("1) Uso correcto por la interfaz pública:")
    print("  ", bomba.iniciar_proceso(75.5))
    print("  ", bomba)

    print("\n2) Acceso directo a un atributo privado:")
    try:
        print(bomba.__potencia)
    except AttributeError as error:
        print("   BLOQUEADO ->", error)

    print("\n3) Validación en el setter (dato inválido):")
    for dato in (150, -10, "alta"):
        try:
            bomba.potencia = dato
        except (ValueError, TypeError) as error:
            print(f"   RECHAZADO ({dato!r}) -> {error}")
    print("   La potencia sigue siendo:", bomba.potencia)

    print("\n4) Llamar un método privado desde afuera:")
    try:
        bomba.__calcular_caudal()
    except AttributeError as error:
        print("   BLOQUEADO ->", error)

    print("\n5) El nombre es de solo lectura (sin setter):")
    try:
        bomba.nombre = "Otra"
    except AttributeError as error:
        print("   BLOQUEADO ->", error)

    print("\n6) Cierre del proceso:")
    print("  ", bomba.detener_proceso())


if __name__ == "__main__":
    main()