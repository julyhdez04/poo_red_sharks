/*
 * EE: Programacion Orientada a Objetos (UV)
 * Practica 1 - Version 2.0.0: Micro-Invernadero Inteligente (ESP32)
 *
 * Etapa 1: Lectura de sensores analogicos (ADC)
 *   - Sensor Termico (LM35/DHT) -> GPIO 34, resolucion de 12 bits.
 *   - Sensor LDR (luz ambiental) -> GPIO 32, resolucion de 12 bits.
 */

// --- Asignacion de pines (segun especificacion) ---
const int PIN_SENSOR_TEMPERATURA = 34;  // ADC, GPIO 34
const int PIN_SENSOR_LDR = 32;          // ADC, GPIO 32

// --- Constantes de conversion ---
const int RESOLUCION_ADC_BITS = 12;          // 12 bits de resolucion
const int RESOLUCION_ADC_MAX = 4095;         // 2^12 - 1
const float VOLTAJE_REFERENCIA = 3.3;        // Voltaje de referencia del ESP32

// --- Asignacion de pines de actuadores (PWM) ---
const int PIN_VENTILADOR = 18;   // Motor DC, PWM
const int PIN_LED_POTENCIA = 19; // LED de potencia, PWM

// --- Configuracion de canales PWM (ledc) ---
const int CANAL_PWM_VENTILADOR = 0;
const int CANAL_PWM_LED = 1;
const int FRECUENCIA_PWM = 5000;      // 5 kHz
const int RESOLUCION_PWM_BITS = 8;    // Duty cycle de 0 a 255

// --- Umbrales de control ---
const float TEMPERATURA_LIMITE_VENTILADOR = 30.0;  // C

// --- Estado del sistema (controlado por comandos seriales) ---
bool modoAutomatico = true;
int dutyManualVentilador = 0;
int dutyManualLed = 0;

void setup() {
  Serial.begin(115200);
  delay(500);

  analogReadResolution(RESOLUCION_ADC_BITS);

  pinMode(PIN_SENSOR_TEMPERATURA, INPUT);
  pinMode(PIN_SENSOR_LDR, INPUT);

  // Configuracion de los canales PWM para ventilador y LED de potencia
  ledcSetup(CANAL_PWM_VENTILADOR, FRECUENCIA_PWM, RESOLUCION_PWM_BITS);
  ledcAttachPin(PIN_VENTILADOR, CANAL_PWM_VENTILADOR);

  ledcSetup(CANAL_PWM_LED, FRECUENCIA_PWM, RESOLUCION_PWM_BITS);
  ledcAttachPin(PIN_LED_POTENCIA, CANAL_PWM_LED);

  Serial.println("==============================================");
  Serial.println(" MICRO-INVERNADERO INTELIGENTE - ESP32");
  Serial.println(" Comandos disponibles por Monitor Serie:");
  Serial.println("   leer            -> telemetria en texto plano");
  Serial.println("   modo auto       -> control automatico (por defecto)");
  Serial.println("   modo manual     -> control manual de PWM");
  Serial.println("   vent <0-255>    -> fija duty cycle del ventilador (modo manual)");
  Serial.println("   led <0-255>     -> fija duty cycle del LED (modo manual)");
  Serial.println("==============================================");
}

void procesarComandoSerial(String comando) {
  comando.trim();
  if (comando.length() == 0) {
    return;
  }

  if (comando.equalsIgnoreCase("leer")) {
    float temperatura = leerTemperatura();
    int luz = leerLuzAmbiental();
    Serial.print("TEMP=");
    Serial.print(temperatura, 2);
    Serial.print(";LUZ=");
    Serial.print(luz);
    Serial.print(";MODO=");
    Serial.println(modoAutomatico ? "AUTO" : "MANUAL");
  } else if (comando.equalsIgnoreCase("modo auto")) {
    modoAutomatico = true;
    Serial.println("OK: modo automatico activado");
  } else if (comando.equalsIgnoreCase("modo manual")) {
    modoAutomatico = false;
    Serial.println("OK: modo manual activado");
  } else if (comando.startsWith("vent ")) {
    int valor = comando.substring(5).toInt();
    dutyManualVentilador = constrain(valor, 0, 255);
    Serial.print("OK: ventilador manual = ");
    Serial.println(dutyManualVentilador);
  } else if (comando.startsWith("led ")) {
    int valor = comando.substring(4).toInt();
    dutyManualLed = constrain(valor, 0, 255);
    Serial.print("OK: led manual = ");
    Serial.println(dutyManualLed);
  } else {
    Serial.println("ERROR: comando no reconocido");
  }
}

float leerTemperatura() {
  // Lectura cruda del ADC (0 - 4095)
  int lecturaCruda = analogRead(PIN_SENSOR_TEMPERATURA);

  // Conversion a voltaje
  float voltaje = (lecturaCruda / (float)RESOLUCION_ADC_MAX) * VOLTAJE_REFERENCIA;

  // Conversion aproximada de voltaje a grados Celsius (sensor tipo LM35: 10mV/C)
  float temperaturaC = voltaje * 100.0;

  return temperaturaC;
}

int leerLuzAmbiental() {
  // Lectura cruda del LDR (0 - 4095). A mayor luz, mayor valor en el ADC.
  return analogRead(PIN_SENSOR_LDR);
}

void controlarVentilador(float temperatura) {
  // Gestion termica: ventilador al 100% si la temperatura supera el limite
  if (temperatura > TEMPERATURA_LIMITE_VENTILADOR) {
    ledcWrite(CANAL_PWM_VENTILADOR, 255);  // 100% duty cycle
  } else {
    ledcWrite(CANAL_PWM_VENTILADOR, 0);
  }
}

void controlarLedPotencia(int luz) {
  // Gestion luminica: a menor luz (LDR), mayor duty cycle del LED (proporcional inverso)
  int dutyCycle = map(luz, 0, RESOLUCION_ADC_MAX, 255, 0);
  dutyCycle = constrain(dutyCycle, 0, 255);
  ledcWrite(CANAL_PWM_LED, dutyCycle);
}

void loop() {
  if (Serial.available() > 0) {
    String entrada = Serial.readStringUntil('\n');
    procesarComandoSerial(entrada);
  }

  float temperatura = leerTemperatura();
  int luz = leerLuzAmbiental();

  if (modoAutomatico) {
    controlarVentilador(temperatura);
    controlarLedPotencia(luz);
  } else {
    ledcWrite(CANAL_PWM_VENTILADOR, dutyManualVentilador);
    ledcWrite(CANAL_PWM_LED, dutyManualLed);
  }

  delay(200);
}
