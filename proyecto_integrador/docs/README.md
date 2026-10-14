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
| **DHT22** | Temperatura, humedad | Digital de un hilo | GPIO 4 | Es un sensor de respaldo. Permite comparar sus lecturas con las del BME280 para detectar fallas, y muestra el polimorfismo con dos sensores de la misma familia. |
| **GUVA-S12SD** | Radiación UV → índice UV | Analógica (ADC1) | GPIO 34 | Entrega un voltaje proporcional a la radiación UV (≈ 0–1 V). Se usa ADC1, el convertidor más confiable del ESP32 para lecturas analógicas. |
 
### Salidas (actuadores e indicadores)
 
| Salida | Tipo | Interfaz | Pin ESP32 | Función |
| :--- | :--- | :--- | :---: | :--- |
| **Ventilador 5 V** | Potencia (PWM vía MOSFET IRLZ44N) | PWM 25 kHz, 8 bits | GPIO 18 | Ventila el protector de radiación para que el sol no caliente los sensores y falsee la temperatura. Su velocidad depende del índice UV. |
| **LED RGB** (cátodo común) | Indicador PWM | PWM 5 kHz, 8 bits ×3 | GPIO 25 · 26 · 27 | Indica el nivel de riesgo UV con la escala de colores de la OMS. |
| **OLED SSD1306 0.96"** | Indicador (pantalla) | I²C (dir. `0x3C`) | SDA 21 · SCL 22 | Muestra los datos en tres páginas que se alternan: clima, presión/altitud y UV/estado. |