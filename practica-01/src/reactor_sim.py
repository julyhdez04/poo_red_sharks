#!/usr/bin/env python3
"""
EE: Programación Orientada a Objetos (UV)
Ejemplo de un Integrador v7: Panel HMI Estático con Limpieza de Pantalla y Registro de Eventos (Obtenido en clase)

"""
# ==============================================================================
# IMPORTACIONES
# ==============================================================================

import os
import random

# Lista global para simular un registrador de eventos (Event Logger) tipo SCADA/HMI
# Esto evita que los mensajes de acción se borren al limpiar la pantalla
historial_eventos = []

def registrar_evento(mensaje: str):
    """Agrega un evento al historial y mantiene solo los últimos 5 para que no desplace la pantalla."""
    historial_eventos.append(mensaje)
    if len(historial_eventos) > 5:
        historial_eventos.pop(0)

def limpiar_pantalla():
    """Limpia la terminal según el sistema operativo (cls para Windows, clear para Unix)."""
    os.system('cls' if os.name == 'nt' else 'clear')


# ==============================================================================
# ACTUADORES (Dispositivos de Control)
# ==============================================================================

# ==============================================================================
# SUPERCLASE  (Base para todos los actuadores)
# ==============================================================================

class Actuador:
    def __init__(self, nombre: str):
        # Atributos de estado del actuador
        self.nombre = nombre
        self.rango_operacion_min = 0.0   # Límite mínimo de operación (0%)
        self.rango_operacion_max = 100.0 # Límite máximo de operación (100%)
        self.estado = False              # Estado lógico de encendido: False = OFF, True = ON
        self.punto_operacion = 0.0       # Porcentaje actual de operación

    def encender(self):
        """Cambia el estado lógico a ON y registra la acción."""
        self.estado = True
        registrar_evento(f"[+] {self.nombre} -> Estado cambiado a: ENCENDIDO (ON)")

    def apagar(self):
        """Cambia el estado lógico a OFF y registra la acción."""
        self.estado = False
        self.punto_operacion = 0.0
        registrar_evento(f"[-] {self.nombre} -> Estado cambiado a: APAGADO (OFF)")

    def ajustar(self, valor: float):
        """Ajusta el punto de operación si está dentro del rango permitido."""
        if self.rango_operacion_min <= valor <= self.rango_operacion_max:
            self.punto_operacion = valor
            registrar_evento(f"[⚙] {self.nombre} -> Punto de operación ajustado al {self.punto_operacion:.1f}%")
        else:
            registrar_evento(f"[⚠️ ERROR] {self.nombre} -> Valor {valor}% fuera de rango (0% - 100%).")

    def info(self) -> str:
        """Retorna una cadena con el estado formateado del actuador."""
        estado_str = "ON" if self.estado else "OFF"
        return f"{self.nombre:<20} | Estado: {estado_str:<3} | Punto Op: {self.punto_operacion:>5.1f}% | Rango: [0.0% - 100.0%]"

# ==============================================================================
# SUBCLASE  (Válvula de Alivio)
# ==============================================================================

class ValvulaAlivio(Actuador):
    """Actuador digital de alivio: 0 = OFF y 1 = ON."""

    def __init__(self, nombre: str = "Válvula de Alivio"):
        super().__init__(nombre)
        self.rango_operacion_min = 0
        self.rango_operacion_max = 1
        self.punto_operacion = 0

    def encender(self):
        super().encender()
        self.punto_operacion = 1

    def apagar(self):
        super().apagar()
        self.punto_operacion = 0

    def ajustar(self, valor: float):
        """Permite únicamente los valores digitales 0 y 1."""
        if valor in (0, 1):
            if valor == 1:
                self.encender()
            else:
                self.apagar()
        else:
            registrar_evento(
                f"[⚠️ ERROR] {self.nombre} -> Valor {valor} inválido. "
                "Solo se permite 0 (OFF) o 1 (ON)."
            )

    def info(self) -> str:
        estado_str = "ON" if self.estado else "OFF"
        return f"{self.nombre:<20} | Estado: {estado_str:<3} | Digital: {int(self.estado)} | Control: ON/OFF"

# ==============================================================================
# MODO AUTOMATICO 
# ==============================================================================
class Reactor:
    """Modela el estado térmico y barométrico interno del reactor químico."""

    def __init__(self):
        self.temperatura = 25.0   # °C, arranca a temperatura ambiente
        self.presion = 1.0        # Bar, arranca a presión atmosférica aprox.
        self.limite_temp = 85.0   # °C, umbral de interlock
        self.limite_presion = 12.0  # Bar, umbral de interlock

    def actualizar(self, porcentaje_bomba: float):
        """Actualiza la temperatura y presión del reactor según el porcentaje de operación de la bomba."""
        delta_t = 1.5 - (0.05 * porcentaje_bomba)
        self.temperatura = max(0.0, self.temperatura + delta_t)
        self.presion = max(0.0, self.presion + (delta_t * 0.08))
        return delta_t

    def en_alarma(self) -> bool:
        """Indica si el reactor superó alguno de los límites de seguridad."""
        return self.temperatura > self.limite_temp or self.presion > self.limite_presion
# ==============================================================================
# SUPERCLASE SENSOR (Base para todos los sensores)
# ==============================================================================
class Sensor:

# ==============================================================================
# MODO PRUEBAS (Tipos de falla simulables)
# ==============================================================================
    # Tipos de falla simulables en el modo PRUEBAS
    #   atascado     -> la lectura se congela en el último valor medido
    #   saturado     -> la lectura se sale del rango físico del sensor
    #   desconectado -> circuito abierto, no hay señal
    FALLAS_VALIDAS = ("atascado", "saturado", "desconectado")
# ==============================================================================

    def __init__(self, nombre: str, variable_fisica: str, rango_min: float, rango_max: float, sensibilidad: float, decimales_medicion: int, unidad: str, fuente=None):
        # Atributos de especificación técnica del sensor
        self.nombre = nombre
        self.variable_fisica = variable_fisica
        self.rango_min = rango_min
        self.rango_max = rango_max
        self.sensibilidad = sensibilidad
        self.decimales_medicion = decimales_medicion
        self.unidad = unidad
        # Función opcional que entrega el valor real del proceso (lazo cerrado).
        # Si no se especifica, el sensor simula lecturas aleatorias dentro de su rango.
        self.fuente = fuente
    
# ==============================================================================
# Atributos de estado para el modo pruebas
# ==============================================================================
        self.falla = None            # Falla inyectada (None = sensor sano)
        self.valor_forzado = None    # Valor fijo forzado desde el modo PRUEBAS
        self.medido = False          # verifica si por lo menos hizo una lectura
        self.ultima_lectura = None   # Último valor medido (None = sin señal)
# ==============================================================================

    def _valor_base(self) -> float:
        """Valor real del proceso (si hay fuente) o lectura aleatoria dentro del rango."""
        if self.fuente is not None:
            crudo = self.fuente()
        else:
            crudo = random.uniform(self.rango_min, self.rango_max)
        return round(crudo, self.decimales_medicion)

    def medir(self):
        """Genera una lectura simulada respetando las fallas inyectadas. No registra eventos."""
        if self.falla == "desconectado":
            valor = None
        elif self.falla == "saturado":
            valor = round(self.rango_max * 1.25, self.decimales_medicion)
        elif self.falla == "atascado":
            if self.ultima_lectura is None:
                valor = self._valor_base()
            else:
                valor = self.ultima_lectura
        elif self.valor_forzado is not None:
            valor = round(self.valor_forzado, self.decimales_medicion)
        else:
            valor = self._valor_base()

        self.medido = True
        self.ultima_lectura = valor
        return valor

    def leer_valor_actual(self):
        """Simula una lectura física, la redondea a la precisión dada y la registra en eventos."""
        valor = self.medir()
        if valor is None:
            registrar_evento(f"[📊 LECTURA] {self.nombre}: SIN SEÑAL (circuito abierto)")
        else:
            lectura_str = f"{valor:.{self.decimales_medicion}f} {self.unidad}"
            registrar_evento(f"[📊 LECTURA] {self.nombre}: {lectura_str} (Var: {self.variable_fisica})")
        return valor

    def inyectar_falla(self, tipo: str) -> bool:
        """Inyecta una falla simulada en el sensor (solo modo PRUEBAS)."""
        if tipo not in self.FALLAS_VALIDAS:
            registrar_evento(f"[ERROR] Falla '{tipo}' no válida. Opciones: {', '.join(self.FALLAS_VALIDAS)}")
            return False
        self.falla = tipo
        registrar_evento(f"[FALLA] {self.nombre} -> falla '{tipo}' inyectada")
        return True

    def forzar_valor(self, valor: float):
        """Fuerza una lectura fija en el sensor para probar reacciones."""
        self.valor_forzado = valor
        registrar_evento(f"[FORZADO] {self.nombre} -> lectura forzada a {valor:.{self.decimales_medicion}f} {self.unidad}")

    def reparar(self, registrar: bool = True):
        """Retira la falla y el valor forzado."""
        self.falla = None
        self.valor_forzado = None
        if registrar:
            registrar_evento(f"[REPARADO] {self.nombre} -> falla/forzado retirado")

    def lectura_str(self) -> str:
        """Texto de la última lectura para mostrar en el panel."""
        if not self.medido:
            return "---"
        if self.ultima_lectura is None:
            return "SIN SEÑAL"
        return f"{self.ultima_lectura:.{self.decimales_medicion}f} {self.unidad}"

    def info(self) -> str:
        """Retorna una cadena con las especificaciones técnicas del sensor."""
        return f"{self.nombre:<20} | Var: {self.variable_fisica:<18} | Rango: [{self.rango_min:>4.1f} - {self.rango_max:>5.1f}] {self.unidad:<5} | Sensibilidad: {self.sensibilidad} | Dec: {self.decimales_medicion}"


# ==============================================================================
# INTERFAZ HMI (TABLERO DE CONTROL)
# ==============================================================================
def mostrar_interfaz_hmi(actuadores, sensores, modo):
    """Pinta el menú y los estados actuales de los objetos en una pantalla fija."""
    print("=" * 85)
    print("                PANEL DE CONTROL INDUSTRIAL HMI (ESTÁTICO)")
    print("=" * 85)
    
    # 1. Sección de Actuadores
    print(" [ACTUADORES]")
    for key, act in actuadores.items():
        print(f"   ► [{key:<7}] {act.info()}")
    print("-" * 85)
    
    # 2. Sección de Sensores
    print(" [SENSORES]")
    for key, sen in sensores.items():
        print(f"   ► [{key:<9}] {sen.info()}")
        etiqueta = ""
        if sen.falla:
            etiqueta = f"   <<< FALLA INYECTADA: {sen.falla}"
        elif sen.valor_forzado is not None:
            etiqueta = f"   <<< VALOR FORZADO: {sen.valor_forzado}"
        print(f"       ↳ Última lectura: {sen.lectura_str()}{etiqueta}")
    print("=" * 85)
    
    # 3. Sección de Registro de Eventos (Event Logger)
    print(" [REGISTRO DE EVENTOS EN VIVO (SCADA/HMI)]")
    if not historial_eventos:
        print("   (Sin actividad reciente)")
    else:
        for ev in historial_eventos:
            print(f"   {ev}")
    print("=" * 85)

    print(" COMANDOS DISPONIBLES:")
    if modo == "PRUEBAS":
        print("[COMANDOS DE DIAGNÓSTICO]")
        print("   • falla <sensor> <atascado|saturado|desconectado>     (Ej: falla manometro saturado)")
        print("   • forzar <sensor> <val>     (Ej: forzar temperatura 95.5)")
        print("   • reparar <sensor|todos>    (Ej: reparar todos)")
    # 4. Sección de Comandos
    print(" COMANDOS DISPONIBLES:")
    print("   • encender <actuador>       (Ej: encender bomba)")
    print("   • apagar <actuador>         (Ej: apagar valvula)")
    print("   • ajustar <actuador> <val>  (Ej: ajustar bomba 75.5)")
    print("   • leer <sensor>             (Ej: leer caudal  O  leer manometro)")
    print("   • terminar                  (Finaliza la simulación)")
    print("=" * 85)


# ==============================================================================
# INTERLOCKS DE SEGURIDAD
# ==============================================================================
def aplicar_interlocks(reactor, bomba, valvula, termometro=None, manometro=None):
    """
    Si Temperatura > 85.0 C o Presion > 12.0 Bar, el sistema ignora cualquier
    instruccion del operario y fuerza la Bomba al 100% y la Valvula de Alivio abierta.
    """
    # La proteccion lee los instrumentos: una lectura forzada o con falla tambien la dispara
    temperatura = reactor.temperatura
    presion = reactor.presion
    if termometro is not None:
        lectura = termometro.medir()
        if lectura is not None:
            temperatura = lectura
    if manometro is not None:
        lectura = manometro.medir()
        if lectura is not None:
            presion = lectura

    if temperatura > reactor.limite_temp or presion > reactor.limite_presion:
        if bomba.punto_operacion != 100.0 or not bomba.estado:
            bomba.encender()
            bomba.ajustar(100.0)
            registrar_evento("🛑 [INTERLOCK] Límite de seguridad excedido: Bomba forzada al 100%.")
        if valvula.punto_operacion != 1:
            valvula.encender()
            registrar_evento("🛑 [INTERLOCK] Límite de seguridad excedido: Válvula forzada a ABIERTA.")
        return True
    return False


# ==============================================================================
# BUCLE INTERACTIVO PRINCIPAL
# ==============================================================================
def main():
    # Modelo físico del proceso que alimenta las lecturas de los sensores
    reactor = Reactor()
    # 3. Creación de dos objetos de la clase Actuador
        # --- Actuadores especificados en la práctica ---
    bomba = Actuador("Bomba de Enfriamiento")   # 0-100 %, modulación proporcional
    valvula = ValvulaAlivio()                   # digital 0/1

    # --- Sensores especificados en la práctica ---
    termometro = Sensor(
        nombre="Termopar de Reactor",
        variable_fisica="Temperatura",
        rango_min=0.0, rango_max=150.0,
        sensibilidad=0.01, decimales_medicion=2, unidad="°C",
        fuente=lambda: reactor.temperatura,
    )

    manometro = Sensor(
        nombre="Manómetro Digital",
        variable_fisica="Presión de Reactor",
        rango_min=0.0, rango_max=15.0,
        sensibilidad=0.001, decimales_medicion=3, unidad="Bar",
        fuente=lambda: reactor.presion,
    )

    caudalimetro = Sensor(
        nombre="Caudalímetro",
        variable_fisica="Flujo de Refrigerante",
        rango_min=0.0, rango_max=50.0,
        sensibilidad=0.1, decimales_medicion=1, unidad="L/min",
        fuente=lambda: bomba.punto_operacion * 0.5,
    )

    actuadores = {
        "bomba": bomba,
        "valvula": valvula,
    }
    sensores = {
        "temperatura": termometro,
        "manometro": manometro,
        "caudal": caudalimetro,
    }

# ==============================================================================
# Seleccion del modo de operacion
# ==============================================================================
    print("=" * 85)
    print("           SISTEMA DE CONTROL - SELECCION DE MODO DE OPERACION")
    print("=" * 85)
    print(" 1. Modo Manual      (control directo del operario)")
    print(" 2. Modo Automatico  (lazo cerrado de estabilidad)")
    print(" 3. Modo de Pruebas  (inyeccion de fallos)")
    opcion_modo = input("Seleccione un modo [1-3]: ").strip()
    modos_disponibles = {"1": "MANUAL", "2": "AUTOMATICO", "3": "PRUEBAS"}
    modo = modos_disponibles.get(opcion_modo, "MANUAL")
    registrar_evento(f"[MODO] Sistema iniciado en modo {modo}.")
    modo_automatico = (modo == "AUTOMATICO")

    # Bucle interactivo directo
    while True:
        # 0. Verificamos los interlocks de seguridad antes de cualquier otra cosa
        en_alarma = aplicar_interlocks(reactor, bomba, valvula, termometro, manometro)

        # 0.2 Modo automatico (o alarma activa): el reactor avanza un paso segun la bomba
        delta_t = reactor.actualizar(bomba.punto_operacion)

        if modo_automatico or reactor.en_alarma():
            registrar_evento(f"[🔄 ESTABILIDAD] dT: {delta_t:+.2f} C | Nueva Temp: {reactor.temperatura:.2f} C")

        # 1. Limpiamos la pantalla antes de volver a dibujar
        limpiar_pantalla()

        print(f" MODO DE OPERACION ACTUAL: {modo}")

        if en_alarma:
            print(" [ALARMA DE SEGURIDAD ACTIVA: LÍMITES DE OPERACIÓN EXCEDIDOS] ")

        # 2. Dibujamos el HMI con los estados actualizados en memoria
        mostrar_interfaz_hmi(actuadores, sensores, modo)

        print(" COMANDO ADICIONAL: automatico (activa/desactiva la simulacion continua)")

        try:
            # Solicitamos el comando de entrada al usuario
            entrada = input("Ingrese comando >> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n[+] Programa terminado.")
            break

        if not entrada:
            continue

        if entrada.lower() == "terminar":
            print("\n[+] Cerrando sistema de control... Programa finalizado con éxito.")
            break

        partes = entrada.split()
        if len(partes) == 0:
            continue

        comando = partes[0].lower()

        # Bloqueo de comandos manuales sobre bomba/valvula durante interlock activo
        if en_alarma and comando in ("ajustar", "apagar", "encender") and len(partes) >= 2:
            if partes[1].lower() in ("bomba", "valvula"):
                registrar_evento("[BLOQUEADO] Interlock activo: no se permite control manual de bomba/válvula.")
                continue

        # Procesamiento del Comando: AUTOMATICO (activa/desactiva la simulacion continua)
        if comando == "automatico":
            modo_automatico = not modo_automatico
            estado = "ACTIVADO" if modo_automatico else "DESACTIVADO"
            registrar_evento(f"[MODO AUTOMATICO] Sistema {estado}.")
            continue

        # Los comandos de inyeccion de fallos solo existen en Modo de Pruebas
        if comando in ("falla", "forzar", "reparar") and modo != "PRUEBAS":
            registrar_evento(f"[ERROR] El comando '{comando}' solo esta disponible en Modo de Pruebas.")
            continue

# ==============================================================================
# Mensaje de error de ingreso de comando
# ==============================================================================

        # Procesamiento del Comando: ENCENDER
        if comando == "encender":
            if len(partes) < 2:
                registrar_evento("[⚠️ ERROR] Especifica el actuador. Uso: encender <bomba/valvula>")
                continue
            target = partes[1].lower()
            if target in actuadores:
                actuadores[target].encender()
            else:
                registrar_evento(f"[⚠️ ERROR] Actuador '{target}' no existe. Opciones: bomba, valvula")

        # Procesamiento del Comando: APAGAR
        elif comando == "apagar":
            if len(partes) < 2:
                registrar_evento("[⚠️ ERROR] Especifica el actuador. Uso: apagar <bomba/valvula>")
                continue
            target = partes[1].lower()
            if target in actuadores:
                actuadores[target].apagar()
            else:
                registrar_evento(f"[⚠️ ERROR] Actuador '{target}' no existe. Opciones: bomba, valvula")

        # Procesamiento del Comando: AJUSTAR
        elif comando == "ajustar":
            if len(partes) < 3:
                registrar_evento("[⚠️ ERROR] Faltan parámetros. Uso: ajustar <bomba/valvula> <valor>")
                continue
            target = partes[1].lower()
            try:
                valor = float(partes[2])
                if target in actuadores:
                    actuadores[target].ajustar(valor)
                else:
                    registrar_evento(f"[⚠️ ERROR] Actuador '{target}' no existe. Opciones: bomba, valvula")
            except ValueError:
                registrar_evento("[⚠️ ERROR] El valor de ajuste debe ser numérico.")

        # Procesamiento del Comando: LEER
        elif comando == "leer":
            if len(partes) < 2:
                registrar_evento("[⚠️ ERROR] Especifica el sensor. Uso: leer <caudal/manometro>")
                continue
            target = partes[1].lower()
            if target in sensores:
                sensores[target].leer_valor_actual()
            else:
                registrar_evento(f"[⚠️ ERROR] Sensor '{target}' no existe. Opciones: temperatura, manometro, caudal")

        # Procesamiento del Comando: FALLA
        elif comando == "falla":
            if len(partes) < 3:
                registrar_evento("[⚠️ ERROR] Uso: falla <sensor> <atascado|saturado|desconectado>")
                continue
            target = partes[1].lower()
            if target in sensores:
                sensores[target].inyectar_falla(partes[2].lower())
            else:
                registrar_evento(f"[⚠️ ERROR] Sensor '{target}' no existe.")

        # Procesamiento del Comando: FORZAR
        elif comando == "forzar":
            if len(partes) < 3:
                registrar_evento("[⚠️ ERROR] Uso: forzar <sensor> <valor>")
                continue
            target = partes[1].lower()
            try:
                valor = float(partes[2])
                if target in sensores:
                    sensores[target].forzar_valor(valor)
                else:
                    registrar_evento(f"[⚠️ ERROR] Sensor '{target}' no existe.")
            except ValueError:
                registrar_evento("[⚠️ ERROR] El valor forzado debe ser numérico.")

        # Procesamiento del Comando: REPARAR
        elif comando == "reparar":
            if len(partes) < 2:
                registrar_evento("[⚠️ ERROR] Uso: reparar <sensor|todos>")
                continue
            target = partes[1].lower()
            if target == "todos":
                for sensor in sensores.values():
                    sensor.reparar(registrar=False)
                registrar_evento("[🛠 REPARADO] Todos los sensores restablecidos")
            elif target in sensores:
                sensores[target].reparar()
            else:
                registrar_evento(f"[⚠️ ERROR] Sensor '{target}' no existe.")

        # Comando no reconocido
        else:
            registrar_evento(f"[⚠️ ERROR] Comando '{comando}' no reconocido.")


if __name__ == "__main__":
    main()