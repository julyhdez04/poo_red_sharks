# Diagramas · Estación Meteorológica Automatizada

GitHub muestra los diagramas Mermaid como imagen.

---

## 1. Diagrama de clases UML

**Visibilidades:** `+` público · `-` privado · `#` protegido.
Los métodos en cursiva (marcados con `*` en el código Mermaid) son **abstractos**.

```mermaid
classDiagram
    direction TB

    class NodoIoT {
        <<abstract>>
        #id: String
        #activo: bool
        #intervalo_ms: uint32_t
        -ultimaActualizacion_ms: uint32_t
        +NodoIoT(id: String, intervalo_ms: uint32_t)
        +iniciar()* bool
        +actualizar()* void
        +imprimirSerie()* void
        +getId() String
        +estaActivo() bool
        #tocaActualizar() bool
    }

    class SensorBase {
        <<abstract>>
        #lecturaValida: bool
        #errores: uint16_t
        +actualizar() void
        +esValida() bool
        +getErrores() uint16_t
        #leer()* bool
    }

    class SensorTermoHigrometrico {
        <<abstract>>
        #temperatura_C: float
        #humedad_pct: float
        #filtroT: FiltroMediaMovil
        #filtroHR: FiltroMediaMovil
        +getTemperatura() float
        +getHumedad() float
        +getPuntoRocio() float
        +getIndiceCalor() float
        -calcularPuntoRocio(T: float, HR: float) float
        -calcularIndiceCalor(T: float, HR: float) float
    }

    class SensorBME280 {
        -bme: Adafruit_BME280
        -direccionI2C: uint8_t
        -presion_hPa: float
        -presionNivelMar_hPa: float
        -filtroP: FiltroMediaMovil
        +SensorBME280(id: String, direccion: uint8_t)
        +iniciar() bool
        +imprimirSerie() void
        +getPresion() float
        +getAltitudEstimada() float
        +setPresionNivelMar(p: float) void
        #leer() bool
        -calcularAltitud(p: float) float
    }

    class SensorDHT22 {
        -dht: DHT
        -pinDatos: uint8_t
        +SensorDHT22(id: String, pin: uint8_t)
        +iniciar() bool
        +imprimirSerie() void
        #leer() bool
    }

    class SensorUV {
        -pinADC: uint8_t
        -voltaje_mV: float
        -indiceUV: float
        -filtroUV: FiltroMediaMovil
        +SensorUV(id: String, pin: uint8_t)
        +iniciar() bool
        +imprimirSerie() void
        +getIndiceUV() float
        +getNivelRiesgo() String
        #leer() bool
        -convertirAIndice(mV: float) float
    }

    class ActuadorBase {
        <<abstract>>
        #frecuenciaPWM_Hz: uint32_t
        #resolucion_bits: uint8_t
        #nivel_pct: float
        +ajustar(pct: float) void
        +encender() void
        +apagar() void
        +getNivel() float
        +actualizar() void
        #escribirPWM(pin: uint8_t, pct: float) void
        #aplicarSalida()* void
    }

    class VentiladorPWM {
        -pinGate: uint8_t
        -nivelMinimo_pct: float
        +VentiladorPWM(id: String, pin: uint8_t)
        +iniciar() bool
        +imprimirSerie() void
        #aplicarSalida() void
    }

    class LedRGB {
        -pinR: uint8_t
        -pinG: uint8_t
        -pinB: uint8_t
        -r: uint8_t
        -g: uint8_t
        -b: uint8_t
        +LedRGB(id: String, pinR: uint8_t, pinG: uint8_t, pinB: uint8_t)
        +iniciar() bool
        +imprimirSerie() void
        +setColor(r: uint8_t, g: uint8_t, b: uint8_t) void
        +mostrarNivelUV(indice: float) void
        #aplicarSalida() void
    }

    class PantallaOLED {
        -display: Adafruit_SSD1306
        -direccionI2C: uint8_t
        -pagina: uint8_t
        -lineas: String[4]
        +PantallaOLED(id: String, direccion: uint8_t)
        +iniciar() bool
        +actualizar() void
        +imprimirSerie() void
        +setLinea(n: uint8_t, texto: String) void
        -dibujarPagina() void
    }

    class FiltroMediaMovil {
        -muestras: float[8]
        -indice: uint8_t
        -cantidad: uint8_t
        +agregar(x: float) float
        +promedio() float
        +reiniciar() void
    }

    class EstacionMeteorologica {
        -nodos: NodoIoT*[8]
        -numNodos: uint8_t
        +agregarNodo(n: NodoIoT*) void
        +iniciar() bool
        +ciclo() void
        -aplicarReglas() void
        -imprimirMonitorSerie() void
    }

    NodoIoT <|-- SensorBase
    NodoIoT <|-- ActuadorBase
    NodoIoT <|-- PantallaOLED
    SensorBase <|-- SensorTermoHigrometrico
    SensorBase <|-- SensorUV
    SensorTermoHigrometrico <|-- SensorBME280
    SensorTermoHigrometrico <|-- SensorDHT22
    ActuadorBase <|-- VentiladorPWM
    ActuadorBase <|-- LedRGB

    SensorTermoHigrometrico *-- "2" FiltroMediaMovil : filtroT, filtroHR
    SensorBME280 *-- "1" FiltroMediaMovil : filtroP
    SensorUV *-- "1" FiltroMediaMovil : filtroUV
    EstacionMeteorologica o-- "1..8" NodoIoT : contiene
```

### Relaciones

| Símbolo | Relación | Ejemplo |
| :---: | :--- | :--- |
| `<\|--` (triángulo hueco) | **Herencia** ("es un") | `SensorBME280` es un `SensorTermoHigrometrico`, que es un `SensorBase`, que es un `NodoIoT` |
| `*--` (rombo relleno) | **Composición** | Cada sensor crea y destruye sus propios `FiltroMediaMovil` |
| `o--` (rombo hueco) | **Agregación** | `EstacionMeteorologica` agrupa los nodos, que existen por separado (se crean en `setup()`) |

---

## 2. Esquema de conexiones

### Diagrama de bloques

```mermaid
flowchart LR
    USB["Fuente USB<br/>5 V / 1 A"]

    subgraph ESP["ESP32 DevKit V1"]
        VIN["VIN 5 V"]
        V33["3V3"]
        G21["GPIO 21 · SDA"]
        G22["GPIO 22 · SCL"]
        G4["GPIO 4"]
        G34["GPIO 34 · ADC1"]
        G18["GPIO 18 · PWM"]
        G25["GPIO 25 · PWM"]
        G26["GPIO 26 · PWM"]
        G27["GPIO 27 · PWM"]
    end

    subgraph IN["Entradas · sensores"]
        BME["BME280<br/>I2C 0x76<br/>T · HR · P"]
        DHT["DHT22<br/>1 hilo<br/>T · HR"]
        UV["GUVA-S12SD<br/>analógico<br/>UV"]
    end

    subgraph OUT["Salidas · actuadores e indicadores"]
        OLED["OLED SSD1306<br/>I2C 0x3C"]
        RGB["LED RGB<br/>cátodo común"]
        MOS["MOSFET IRLZ44N<br/>+ diodo 1N5819"]
        FAN["Ventilador<br/>5 V DC"]
    end

    USB --> VIN
    V33 -->|3.3 V| BME & DHT & UV & OLED
    VIN -->|5 V| FAN

    G21 <-->|SDA| BME
    G22 -->|SCL| BME
    G21 <-->|SDA| OLED
    G22 -->|SCL| OLED
    DHT -->|datos + pull-up 10 kΩ| G4
    UV -->|0 – 1 V| G34

    G25 -->|150 Ω| RGB
    G26 -->|47 Ω| RGB
    G27 -->|47 Ω| RGB
    G18 -->|100 Ω compuerta<br/>10 kΩ a GND| MOS
    MOS -->|drenador a terminal −| FAN
```

### Tabla de conexiones

| Componente | Terminal | Se conecta a | Notas |
| :--- | :--- | :--- | :--- |
| **BME280** | VCC / GND | 3V3 / GND | Usar el módulo de 3.3 V |
| | SDA / SCL | GPIO 21 / GPIO 22 | Comparte el bus I²C con la OLED |
| **OLED SSD1306** | VCC / GND | 3V3 / GND | |
| | SDA / SCL | GPIO 21 / GPIO 22 | Dirección `0x3C` (no choca con el BME280 en `0x76`) |
| **DHT22** | VCC / GND | 3V3 / GND | |
| | DATA | GPIO 4 | Pull-up de 10 kΩ a 3V3 (omitir si el módulo ya la tiene) |
| **GUVA-S12SD** | VCC / GND | 3V3 / GND | |
| | OUT | GPIO 34 | Solo entrada, ADC1. Atenuación 0 dB o 2.5 dB para tener más resolución en 0–1 V |
| **LED RGB** | R / G / B | GPIO 25 / 26 / 27 | Con resistencias en serie de 150 Ω (R), 47 Ω (G) y 47 Ω (B) |
| | Cátodo común | GND | |
| **MOSFET IRLZ44N** | Compuerta (G) | GPIO 18 | 100 Ω en serie y 10 kΩ de G a GND (evita que el ventilador arranque al encender) |
| | Fuente (S) | GND | |
| | Drenador (D) | Terminal − del ventilador | |
| **Ventilador 5 V** | Terminal + | VIN (5 V) | |
| | Terminal − | Drenador del MOSFET | Diodo 1N5819 en antiparalelo (cátodo a +5 V) y 100 µF entre 5 V y GND |

**Todas las tierras (GND) son comunes.**

### Pines que no se usan a propósito

- **GPIO 0, 2, 5, 12 y 15:** son pines de arranque (*strapping*) y pueden impedir que la placa inicie.
- **ADC2 (GPIO 25–27 como entrada analógica):** es menos confiable que ADC1 y deja de funcionar si se activa el WiFi. Por eso el sensor UV va en GPIO 34 (ADC1), y los GPIO 25–27 se usan solo como salidas PWM.
