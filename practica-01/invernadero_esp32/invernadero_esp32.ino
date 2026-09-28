/*
 * Versión 1.0.0: Portafolio Físico en Hardware (Actualizado para ESP32 Core v3.x)
 * Micro-Invernadero Inteligente
 */

// --- Asignación Estricta de Pines ---
#define PIN_LDR   32  // ADC - Luz
#define PIN_TEMP  34  // ADC - LM35
#define PIN_FAN   18  // PWM - Motor DC
#define PIN_LED   19  // PWM - LED Ultrabrillante

// --- Configuración de Periféricos (PWM ledc) ---
const int PWM_FREQ = 5000;       // 5kHz requerido
const int PWM_RES  = 8;          // Resolución de 8 bits (0-255) para controlar Duty Cycle

// Nota: Ya no es necesario declarar CH_FAN ni CH_LED. 
// En la nueva versión de la API, el control se hace directo sobre el pin.

// --- Variables del Sistema ---
bool modoManual = false;
int pwmManualFan = 0;
int pwmManualLed = 0;

unsigned long tiempoTelemetria = 0;
const unsigned long INTERVALO_TX = 2000; // Transmisión cada 2 segundos

void setup() {
  Serial.begin(115200);
  
  // Resolución del ADC a 12 bits (0 - 4095)
  analogReadResolution(12);

  // NUEVA API: Configuración de PWM usando solo ledcAttach
  ledcAttach(PIN_FAN, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_LED, PWM_FREQ, PWM_RES);
  
  // Iniciar periféricos apagados (ahora se indica el PIN, no el canal)
  ledcWrite(PIN_FAN, 0);
  ledcWrite(PIN_LED, 0);

  Serial.println("INICIO DE SISTEMA: Micro-Invernadero v2.0.0");
  Serial.println("Comandos Serial: AUTO, FAN_ON, FAN_OFF, LED_ON, LED_OFF");
}

void loop() {
  // 1. Adquisición de Señales
  int lecturaLDR = analogRead(PIN_LDR);
  int lecturaTemp = analogRead(PIN_TEMP);
  
  // Conversión de LM35 a °C (Asumiendo Vref de 3.3V y 10mV/°C)
  // Voltaje (mV) = (lectura / 4095.0) * 3300.0
  float voltajeLM35 = (lecturaTemp / 4095.0) * 3.3; 
  float temperaturaC = voltajeLM35 * 100.0; 

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

    // Gestión Lumínica (Control Proporcional Inverso)
    // Se mapea la lectura ADC (0 oscuro, 4095 muy luminoso) inversamente a PWM (255 a 0)
    dutyLed = map(lecturaLDR, 0, 4095, 255, 0);
    dutyLed = constrain(dutyLed, 0, 255);
  } else {
    dutyFan = pwmManualFan;
    dutyLed = pwmManualLed;
  }

  // 4. Actuación Física (usando el PIN, no el canal)
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

  delay(20); // Estabilidad del lazo
}
