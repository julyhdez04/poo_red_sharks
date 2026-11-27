#pragma once
#include "NodoIoT.h"

// ---------- Subclase 1: sensor analógico ----------
class NodoSensorFisico : public NodoIoT {
  private:
    int _umbralAlerta;   // Encapsulamiento: solo se cambia con el setter
    int _ultimaLectura;  // Último valor leído del ADC

  public:
    NodoSensorFisico(String id, int pinHardware)
        : NodoIoT(id, pinHardware), _umbralAlerta(2048), _ultimaLectura(0) {}

    // Setter con validación: el ADC del ESP32 es de 12 bits (0 a 4095).
    bool setUmbralAlerta(int umbral) {
        if (umbral >= 0 && umbral <= 4095) {
            _umbralAlerta = umbral;
            return true;
        }
        Serial.println("[" + idDispositivo + "] Error: umbral fuera de rango (0-4095).");
        return false;
    }

    int getUmbralAlerta() const { return _umbralAlerta; }
    int getUltimaLectura() const { return _ultimaLectura; }
    bool hayAlerta() const { return _ultimaLectura > _umbralAlerta; }

    void iniciar() override {
        pinMode(pin, INPUT);
        NodoIoT::iniciar();
    }

    // Polimorfismo: lectura analógica y reporte por Puerto Serie.
    void ejecutarAccion() override {
        _ultimaLectura = analogRead(pin);
        Serial.print("[" + idDispositivo + "] Lectura ADC = " + String(_ultimaLectura));
        Serial.print(" (umbral " + String(_umbralAlerta) + ")");
        Serial.println(hayAlerta() ? "  >> ALERTA" : "  OK");
    }
};
