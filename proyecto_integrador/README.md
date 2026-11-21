 Etapa 1 · Planteamiento (Propuesta y Arquitectura)
 
**Proyecto:** Estación Meteorológica Automatizada
**Equipo:** POO Red Sharks · EE Programación Orientada a Objetos · Universidad Veracruzana
 
Los diagramas (UML y esquema de conexiones) están en [`../diagrams/README.md`](../diagrams/README.md).
 
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
| **NEO6VM2** | Latitud, longitud y altitud | UART (serie, 9600 baudios) | GPIO 16 (RX2) y GPIO 17 (TX2) | Módulo GPS que entrega la posición y la altitud del sistema, además de la hora UTC y la velocidad. Muestra el polimorfismo al implementar la misma interfaz de sensor que los demás dispositivos, aunque su fuente de datos sea satelital. |
| **GUVA-S12SD** | Radiación UV → índice UV | Analógica (ADC1) | GPIO 34 | Entrega un voltaje proporcional a la radiación UV (≈ 0–1 V). Se usa ADC1, el convertidor más confiable del ESP32 para lecturas analógicas. |
 
### Salidas (actuadores e indicadores)
 
| Salida | Tipo | Interfaz | Pin ESP32 | Función |
| :--- | :--- | :--- | :---: | :--- |
| **LED rojo** (5 mm, resistencia de 220 Ω) | Indicador digital | Digital ON/OFF · interfaz `Indicador` de la API | GPIO 32 | Indica que el GPS aún no está calibrado. Parpadea mientras busca satélites y queda fijo si se pierde la señal. |
| **LED verde** (5 mm, resistencia de 220 Ω) | Indicador digital | Digital ON/OFF · interfaz `Indicador` de la API | GPIO 33 | Indica que el GPS ya está calibrado, es decir, que tiene fix y entrega posición y altitud válidas. Se apaga si pierde la señal. |

 

