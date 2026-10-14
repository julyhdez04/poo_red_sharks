## **Etapa 1. Propuesta y Arquitectura**
### **EE: Temas Selectos de IIE II (Código: IEDI 18005)**
#### **Facultad de Instrumentación Electrónica — Universidad Veracruzana**
---

### **Información General del Equipo**

*   **Número de Etapa:** Etapa 1
*   **Título del Proyecto:** Estación Meteorológica Automatizada
*   **Fecha de Entrega:** [16/10/2026]
*   **Enlace al Repositorio de GitHub:** https://github.com/julyhdez04/poo_red_sharks.git

| Nombre Completo del Integrante | Matrícula UV | Usuario de GitHub |
| :--- | :--- | :--- |
| Castillo Acosta Josué Marcelo | `S23013913` | [@Pinging78](https://github.com/Pinging78) |
| Hernández Hernández Juliana | `S23013963` | [@julyhdez04](https://github.com/julyhdez04) |
| Gil Martínez Daniel Alberto | `S23013953` | [@Mushi0w0](https://github.com/Mushi0w0) |
| Navarro Hernández Hugo Jesús | `S23013957` | [@Hiukilll](https://github.com/Hiukilll) |
---

## 1. Selección del proyecto

| Campo | Definición |
| :--- | :--- |
| **Opción elegida** | Estación Meteorológica Automatizada |
| **Objetivo general** | Desarrollar un sistema de monitoreo ambiental autónomo que adquiera, filtre y procese de forma continua variables atmosféricas en tiempo real. |
| **Aplicación tangible** | Estación de mesa o exterior (dentro de un protector de radiación ventilado) que muestra las condiciones del clima en una pantalla OLED, indica el nivel de riesgo UV con un LED de color e imprime los valores en el Monitor Serie para depuración. |

### Objetivos específicos

1. Medir temperatura, humedad relativa, presión barométrica y radiación UV con al menos dos transductores distintos.
2. Filtrar las lecturas con una media móvil para reducir el ruido de los sensores.
3. Calcular variables secundarias: **punto de rocío**, **índice de calor** y **altitud estimada**.
4. Mostrar los datos en una pantalla OLED y señalizar el riesgo UV con un LED RGB.
5. Controlar por PWM un ventilador que ventila el protector de radiación según la intensidad del sol.
6. Imprimir los valores medidos y calculados en el Monitor Serie (115200 baudios) para depurar y verificar el funcionamiento.
7. Organizar todo el firmware con POO: una superclase abstracta `NodoIoT` de la que heredan sensores, actuadores y la pantalla.

---

## 2. Definición de hardware

### Entradas (sensores)

| Sensor | Variable(s) | Interfaz | Pin ESP32 | Por qué se eligió |
| :--- | :--- | :--- | :---: | :--- |
| **BME280** | Temperatura, humedad, presión | I²C (dir. `0x76`) | SDA 21 · SCL 22 | Es el sensor principal. Da la presión necesaria para calcular la altitud y tiene buena precisión (±1 hPa, ±1 °C). |
| **DHT22** | Temperatura, humedad | Digital de un hilo | GPIO 4 | Es un sensor de respaldo. Permite comparar sus lecturas con las del BME280 para detectar fallas, y muestra el polimorfismo con dos sensores de la misma familia. |
| **GUVA-S12SD** | Radiación UV → índice UV | Analógica (ADC1) | GPIO 34 | Entrega un voltaje proporcional a la radiación UV (≈ 0–1 V). Se usa ADC1, el convertidor más confiable del ESP32 para lecturas analógicas. |

### Salidas (actuadores e indicadores)

| Salida | Tipo | Interfaz | Pin ESP32 | Función |
| :--- | :--- | :--- | :---: | :--- |
| **Ventilador 5 V** | Potencia (PWM vía MOSFET IRLZ44N) | PWM 25 kHz, 8 bits | GPIO 18 | Ventila el protector de radiación para que el sol no caliente los sensores y falsee la temperatura. Su velocidad depende del índice UV. |
| **LED RGB** (cátodo común) | Indicador PWM | PWM 5 kHz, 8 bits ×3 | GPIO 25 · 26 · 27 | Indica el nivel de riesgo UV con la escala de colores de la OMS. |
| **OLED SSD1306 0.96"** | Indicador (pantalla) | I²C (dir. `0x3C`) | SDA 21 · SCL 22 | Muestra los datos en tres páginas que se alternan: clima, presión/altitud y UV/estado. |

### Escala de color del LED (índice UV, OMS)

| Índice UV | Riesgo | Color |
| :---: | :--- | :--- |
| 0 – 2 | Bajo | Verde |
| 3 – 5 | Moderado | Amarillo |
| 6 – 7 | Alto | Naranja |
| 8 – 10 | Muy alto | Rojo |
| ≥ 11 | Extremo | Violeta |

### Lista de materiales

| Cant. | Componente |
| :---: | :--- |
| 1 | ESP32 DevKit V1 (30 pines) |
| 1 | Módulo BME280 (3.3 V, I²C) |
| 1 | Sensor DHT22 / AM2302 |
| 1 | Módulo UV GUVA-S12SD |
| 1 | Pantalla OLED SSD1306 128×64 I²C |
| 1 | LED RGB 5 mm cátodo común |
| 1 | Ventilador DC 5 V (≤ 200 mA) |
| 1 | MOSFET IRLZ44N (nivel lógico) |
| 1 | Diodo 1N5819 (o 1N4007) |
| 1 | Resistencia 10 kΩ (pull-up DHT22, si el módulo no la trae) |
| 1 | Resistencia 10 kΩ (pull-down de compuerta) |
| 1 | Resistencia 100 Ω (compuerta del MOSFET) |
| 1 | Resistencia 150 Ω (LED rojo) |
| 2 | Resistencia 47 Ω (LED verde y azul) |
| 1 | Capacitor electrolítico 100 µF / 16 V (en la alimentación del ventilador) |
| 1 | Protoboard, cables y fuente USB 5 V / 1 A |

### Consumo estimado

| Bloque | Corriente aprox. |
| :--- | :---: |
| ESP32 (sin WiFi) | 40 – 80 mA |
| Ventilador 5 V | 100 – 200 mA |
| OLED | ≈ 20 mA |
| LED RGB | ≈ 15 mA |
| BME280 + DHT22 + GUVA | < 3 mA |
| **Total** | **< 350 mA** → una fuente USB de 1 A es suficiente |

---

## 3. Arquitectura de software

El firmware se organiza con una jerarquía de clases. La raíz es la superclase abstracta **`NodoIoT`**, que representa cualquier elemento conectado al ESP32 y define la interfaz común: `iniciar()`, `actualizar()` e `imprimirSerie()`. El diagrama completo está en [`../diagrams/README.md`](../diagrams/README.md#1-diagrama-de-clases-uml).

| Nivel | Clases | Rol |
| :--- | :--- | :--- |
| Superclase abstracta | `NodoIoT` | Identificador, estado, temporización no bloqueante (`millis()`) e interfaz común. |
| Subclases abstractas | `SensorBase`, `ActuadorBase` | `SensorBase` es la lectura genérica de transductores, con validación y conteo de errores. `ActuadorBase` es la salida PWM genérica en porcentaje (0–100 %). |
| Subclase abstracta intermedia | `SensorTermoHigrometrico` | Agrupa lo que comparten el BME280 y el DHT22: temperatura, humedad, **punto de rocío** e **índice de calor**. |
| Subclases concretas | `SensorBME280`, `SensorDHT22`, `SensorUV`, `VentiladorPWM`, `LedRGB`, `PantallaOLED` | Cada una implementa el hardware específico. |
| Composición | `FiltroMediaMovil` | Cada sensor tiene sus propios filtros, uno por variable. |
| Controlador | `EstacionMeteorologica` | Contiene los nodos (`NodoIoT*`), los recorre de forma polimórfica, aplica las reglas de control e imprime los valores en el Monitor Serie. |

### Cómo se aplican los pilares de POO

- **Abstracción.** `EstacionMeteorologica` solo llama `nodo->actualizar()` sobre cada `NodoIoT*`, sin conocer el bus (I²C, un hilo, ADC o PWM) que usa cada uno.
- **Herencia.** `SensorBME280` y `SensorDHT22` heredan de `SensorTermoHigrometrico`, que a su vez hereda de `SensorBase` → `NodoIoT`. Los cálculos de punto de rocío e índice de calor se escriben una sola vez.
- **Polimorfismo.** `leer()`, `aplicarSalida()`, `iniciar()` e `imprimirSerie()` se redefinen en cada subclase. El ciclo principal trata igual a un sensor que a la pantalla.
- **Encapsulamiento.**
  - Las fórmulas (`calcularPuntoRocio()`, `calcularIndiceCalor()`, `calcularAltitud()`, `convertirAIndice()`) son **privadas** (`-`). Desde fuera solo se accede a los getters públicos (`+`).
  - Las variables medidas son **protegidas** (`#`): las subclases las escriben al leer, pero el resto del programa no puede modificarlas.
  - `ajustar()` limita el nivel del actuador a 0–100 % antes de escribir el PWM.

### Temporización (sin `delay()`)

| Nodo | Intervalo | Motivo |
| :--- | :---: | :--- |
| `SensorUV` | 200 ms | Muestreo rápido para que el filtro promedie bien el ruido del ADC. |
| `SensorBME280` | 1 s | Lectura principal. |
| `SensorDHT22` | 2 s | Es el tiempo mínimo entre lecturas que permite el DHT22. |
| `PantallaOLED` | 3 s | Cambio de página. |
| Monitor Serie | 2 s | Impresión de los valores filtrados para depuración. |

### Reglas de control

- **Ventilador:** se apaga con índice UV < 1 (de noche). Con más sol, el nivel crece en proporción al índice UV, desde 30 % hasta 100 % con UV ≥ 8; el 30 % es el mínimo para que el motor arranque. Si la temperatura supera 32 °C, el ventilador sube al menos a 60 %.
- **LED RGB:** muestra el color correspondiente al índice UV filtrado. Si un sensor acumula fallas, parpadea en blanco.
- **Validación cruzada:** si el BME280 y el DHT22 difieren en más de 2 °C, se muestra un aviso en la OLED y en el Monitor Serie.

### Variables secundarias (métodos privados)

| Variable | Fórmula | Clase |
| :--- | :--- | :--- |
| Punto de rocío | Magnus: γ = ln(HR/100) + a·T/(b+T); T<sub>d</sub> = b·γ / (a − γ), con a = 17.62 y b = 243.12 °C | `SensorTermoHigrometrico` |
| Índice de calor | Regresión de Rothfusz (NOAA). Solo aplica con T ≥ 26.7 °C; por debajo se reporta T. | `SensorTermoHigrometrico` |
| Altitud estimada | h = 44330 · [1 − (P / P<sub>0</sub>)<sup>1/5.255</sup>], con P<sub>0</sub> = presión a nivel del mar (configurable) | `SensorBME280` |
| Índice UV | UVI ≈ V<sub>out</sub> [mV] / 100 (se ajustará al calibrar) | `SensorUV` |

### Salida al Monitor Serie (ejemplo)

Se imprime cada 2 s a 115200 baudios. Sirve para depurar y para comprobar las lecturas al hacer las pruebas.

```
[BME280] T=24.8 °C  HR=61.2 %  P=848.6 hPa  Alt=1428 m  Rocío=16.9 °C  IC=24.8 °C
[DHT22]  T=25.1 °C  HR=59.8 %
[UV]     412 mV  Índice=4.1 (moderado)
[SALIDAS] Ventilador=52 %  LED=amarillo
```

### Librerías previstas

- Núcleo **ESP32 para Arduino 3.x** (API `ledcAttach` / `ledcWrite`, igual que en la Práctica 01)
- `Adafruit BME280 Library` + `Adafruit Unified Sensor`
- `DHT sensor library` (Adafruit)
- `Adafruit SSD1306` + `Adafruit GFX`

---

## 4. Esquema de conexiones

El diagrama de bloques y la tabla completa de pines están en [`../diagrams/README.md`](../diagrams/README.md#2-esquema-de-conexiones).
