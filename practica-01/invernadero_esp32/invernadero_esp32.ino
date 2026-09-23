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

void setup() {
  Serial.begin(115200);
  delay(500);

  analogReadResolution(RESOLUCION_ADC_BITS);

  pinMode(PIN_SENSOR_TEMPERATURA, INPUT);
  pinMode(PIN_SENSOR_LDR, INPUT);

  Serial.println("==============================================");
  Serial.println(" MICRO-INVERNADERO INTELIGENTE - ESP32");
  Serial.println(" Etapa 1: Lectura de sensores (ADC 12 bits)");
  Serial.println("==============================================");
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

void loop() {
  float temperatura = leerTemperatura();
  int luz = leerLuzAmbiental();

  Serial.print("Temperatura: ");
  Serial.print(temperatura, 2);
  Serial.print(" C | Luz (LDR): ");
  Serial.println(luz);

  delay(1000);
}
