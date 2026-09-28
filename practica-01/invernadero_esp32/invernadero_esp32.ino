/*
 * Versión 2.0.2: Portafolio Físico en Hardware (DHT11)
 * Micro-Invernadero Inteligente
 */
#include "DHT.h"

// --- Asignación de Pines ---
#define PIN_LDR   32  // ADC - Luz
#define PIN_TEMP  4   // DIGITAL - DHT11 
#define PIN_FAN   18  // PWM - Motor DC
#define PIN_LED   19  // PWM - LED Ultrabrillante

#define DHTTYPE DHT11
DHT dht(PIN_TEMP, DHTTYPE);

// --- Configuración de Periféricos (PWM ledc v3.x) ---
const int PWM_FREQ = 5000;
const int PWM_RES  = 8;

// --- Variables del Sistema ---
bool modoManual = false;
int pwmManualFan = 0;
int pwmManualLed = 0;

float temperaturaC = 0.0; // Almacena la última lectura válida

unsigned long tiempoTelemetria = 0;
unsigned long tiempoDHT = 0;
const unsigned long INTERVALO_TX = 2000;  // Transmisión cada 2s
const unsigned long INTERVALO_DHT = 2000; // El DHT11 no soporta lecturas menores a 2 segundos

void setup() {
  Serial.begin(115200);
  
  // Resolución del ADC a 12 bits para el LDR
  analogReadResolution(12);

  // Iniciar sensor digital DHT11
  dht.begin();

  // Configuración de PWM
  ledcAttach(PIN_FAN, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_LED, PWM_FREQ, PWM_RES);
  ledcWrite(PIN_FAN, 0);
  ledcWrite(PIN_LED, 0);

  Serial.println("INICIO DE SISTEMA: Micro-Invernadero v2.0.1 (DHT11)");
  Serial.println("Comandos Serial: AUTO, FAN_ON, FAN_OFF, LED_ON, LED_OFF");
}

void loop() {
  // 1. Adquisición de Señales
  int lecturaLDR = analogRead(PIN_LDR);
  
  // El DHT11 es lento. Solo se lee cada 2 segundos para no bloquear el ESP32
  if (millis() - tiempoDHT >= INTERVALO_DHT) {
    tiempoDHT = millis();
    float temp = dht.readTemperature();
    // Validar que la lectura no sea un error (NaN = Not a Number)
    if (!isnan(temp)) {
      temperaturaC = temp; 
    }
  }

  int dutyFan = 0;
  int dutyLed = 0;

  // 2. Procesamiento de Comandos (Monitor Serie)
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    comando.toUpperCase();
    
    if (comando == "AUTO") {
      modoManual = false;
    } else if (comando == "FAN_ON") {
      modoManual = true; pwmManualFan = 255;
    } else if (comando == "FAN_OFF") {
      modoManual = true; pwmManualFan = 0;
    } else if (comando == "LED_ON") {
      modoManual = true; pwmManualLed = 255;
    } else if (comando == "LED_OFF") {
      modoManual = true; pwmManualLed = 0;
    }
  }

  // 3. Algoritmo de Control Físico
  if (!modoManual) {
    // Gestión Térmica
    if (temperaturaC > 30.0) {
      dutyFan = 255; // 100% Duty Cycle
    } else {
      dutyFan = 0;
    }

    // Gestión Lumínica
    int luzMximaReal = 2000;
    dutyLed = map(lecturaLDR, 0, luzMximaReal, 255, 0);
    dutyLed = constrain(dutyLed, 0, 255);
  } else {
    dutyFan = pwmManualFan;
    dutyLed = pwmManualLed;
  }

  // 4. Actuación Física
  ledcWrite(PIN_FAN, dutyFan);
  ledcWrite(PIN_LED, dutyLed);

  // 5. Telemetría en formato JSON
  if (millis() - tiempoTelemetria >= INTERVALO_TX) {
    tiempoTelemetria = millis();
    
    Serial.print("{");
    Serial.print("\"modo_control\":\""); Serial.print(modoManual ? "MANUAL" : "AUTO"); Serial.print("\", ");
    Serial.print("\"temp_c\":"); Serial.print(temperaturaC, 2); Serial.print(", ");
    Serial.print("\"ldr_adc\":"); Serial.print(lecturaLDR); Serial.print(", ");
    Serial.print("\"pwm_fan\":"); Serial.print(dutyFan); Serial.print(", ");
    Serial.print("\"pwm_led\":"); Serial.print(dutyLed);
    Serial.println("}");
  }

//  delay(20); // Estabilidad del lazo general
  vTaskDelay(pdMS_TO_TICKS(20));//Función que aisla el tiempo del loop a 20ms

}
