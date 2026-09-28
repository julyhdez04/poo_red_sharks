# POO Red Sharks

<p align="center">
  <img src="https://images.seeklogo.com/logo-png/13/2/tiburones-rojos-de-veracruz-logo-png_seeklogo-139813.png" alt="Logo Red Sharks">
</p>

<p align="center">
  <b>Repositorio de la Experiencia Educativa: Programación Orientada a Objetos</b><br>
  Universidad Veracruzana
</p>

---

## Integrantes del equipo

| Nombre | Matrícula | GitHub |
| :--- | :---: | :---: |
| **Castillo Acosta Josué Marcelo** | `S23013913` | [@Pinging78](https://github.com/Pinging78) |
| **Hernández Hernández Juliana** | `S23013963` | [@julyhdez04](https://github.com/julyhdez04) |
| **Gil Martínez Daniel Alberto** | `S23013953` | [@Mushi0w0](https://github.com/Mushi0w0) |
| **Navarro Hernández Hugo Jesús** | `S23013957` | [@Hiukilll](https://github.com/Hiukilll) |

---

## Descripción

Este repositorio reúne las prácticas, proyectos y actividades del curso de POO. El trabajo principal hasta ahora es la **Práctica 01**, que tiene dos partes que se complementan:

1. **Simulador de reactor químico (Python):** un panel de control industrial (HMI) en terminal, construido con clases `Actuador`, `ValvulaAlivio`, `Sensor` y `Reactor`, con interlocks de seguridad y modo de pruebas con inyección de fallas.
2. **Micro-invernadero inteligente (ESP32):** firmware en Arduino/C++ que lee temperatura y luz, controla un ventilador y un LED por PWM y envía telemetría en formato JSON por puerto serie.

---

## Estructura del repositorio

```
poo_red_sharks/
├── practica-01/
│   ├── src/
│   │   └── reactor_sim.py           # Simulador HMI del reactor (Python)
│   ├── invernadero_esp32/
│   │   ├── invernadero_esp32.ino    # Firmware del micro-invernadero
│   │   └── README.md                # Componentes del invernadero
│   ├── docs/
│   │   └── Readme.md                # Diagramas UML y conceptos de POO
│   └── README.md
├── practica-02/                     # En desarrollo
├── practica-03/                     # En desarrollo
├── tests/
│   └── prueba1/test1.py             # Script de captura de datos
├── foro_JHH.py                      # Versión anterior del integrador (referencia)
├── AUTHORS.md
└── README.md
```

---

## Práctica 01

### A) Simulador del reactor (`practica-01/src/reactor_sim.py`)

**Requisitos:** Python 3.8 o superior. No necesita instalar librerías externas.

**Ejecución:**

```bash
python3 practica-01/src/reactor_sim.py
```

Al iniciar se elige el modo de operación:

| Modo | Descripción |
| :--- | :--- |
| **1. Manual** | El operador controla directamente la bomba y la válvula. |
| **2. Automático** | El reactor avanza un paso de simulación en cada ciclo (lazo cerrado). |
| **3. Pruebas** | Igual que el manual, más comandos para inyectar fallas en los sensores. |

**Clases principales**

| Clase | Responsabilidad |
| :--- | :--- |
| `Actuador` | Modela un actuador proporcional (0–100 %): `encender()`, `apagar()`, `ajustar(valor)`. |
| `ValvulaAlivio` | Hereda de `Actuador`; es digital (solo acepta 0 o 1). |
| `Sensor` | Simula lecturas con rango, sensibilidad, decimales y unidad; soporta fallas y valores forzados. |
| `Reactor` | Modelo físico: temperatura y presión que evolucionan según la bomba. |

**Modelo físico:** en cada paso, `ΔT = 1.5 °C − (0.05 °C × %bomba)`. La presión se acopla de forma simplificada al cambio de temperatura.

**Interlock de seguridad:** si la temperatura supera **85 °C** o la presión supera **12 bar**, el sistema ignora al operador, fuerza la bomba al 100 % y abre la válvula de alivio.

**Comandos**

| Comando | Ejemplo | Disponible en |
| :--- | :--- | :--- |
| `encender <actuador>` | `encender bomba` | Todos los modos |
| `apagar <actuador>` | `apagar valvula` | Todos los modos |
| `ajustar <actuador> <valor>` | `ajustar bomba 75.5` | Todos los modos |
| `leer <sensor>` | `leer temperatura` | Todos los modos |
| `automatico` | `automatico` | Activa o desactiva la simulación continua |
| `falla <sensor> <tipo>` | `falla manometro saturado` | Solo modo Pruebas |
| `forzar <sensor> <valor>` | `forzar temperatura 90` | Solo modo Pruebas |
| `reparar <sensor\|todos>` | `reparar todos` | Solo modo Pruebas |
| `terminar` | `terminar` | Todos los modos |

- **Actuadores:** `bomba`, `valvula`
- **Sensores:** `temperatura`, `manometro`, `caudal`
- **Tipos de falla:** `atascado` (lectura congelada), `saturado` (sale del rango físico), `desconectado` (sin señal)

### B) Micro-invernadero con ESP32 (`practica-01/invernadero_esp32/`)

**Hardware:** ESP32, sensor DHT11 (temperatura), fotorresistencia LDR, ventilador DC y LED ultrabrillante. Las fotos de los componentes están en el [README del invernadero](practica-01/invernadero_esp32/README.md).

**Pines**

| Pin | Función |
| :---: | :--- |
| 32 | LDR (ADC, luz) |
| 4 | DHT11 (digital, temperatura) |
| 18 | Ventilador (PWM) |
| 19 | LED (PWM) |

**Software:** Arduino IDE con soporte para ESP32 (el código usa la API `ledcAttach` de la versión 3.x) y la librería **DHT sensor library**.

**Funcionamiento**

- **Modo automático:** el ventilador se enciende si la temperatura pasa de 30 °C; el LED se ajusta de forma inversa a la luz que mide el LDR.
- **Modo manual:** se controla por el Monitor Serie a **115200 baudios**.
- **Comandos serie:** `AUTO`, `FAN_ON`, `FAN_OFF`, `LED_ON`, `LED_OFF`.
- **Telemetría:** cada 2 segundos envía un JSON, por ejemplo:

```json
{"modo_control":"AUTO", "temp_c":27.00, "ldr_adc":1450, "pwm_fan":0, "pwm_led":70}
```

### Documentación y diagramas UML

Los diagramas UML de actuadores y sensores, junto con la explicación de abstracción y encapsulamiento aplicados al código, están en [`practica-01/docs/Readme.md`](practica-01/docs/Readme.md).

---

## Prácticas 02 y 03

Aún en desarrollo. Sus resultados se documentarán en [`practica-02/`](practica-02/) y [`practica-03/`](practica-03/).

---

## Flujo de trabajo del equipo

- La rama `main` contiene la versión integrada y estable.
- Cada funcionalidad se desarrolla en su propia rama y se integra con *pull request*.
- Los mensajes de commit siguen el formato `feat:`, `fix:` y similares, por ejemplo `feat(esp32): control PWM de ventilador y LED`.

---
