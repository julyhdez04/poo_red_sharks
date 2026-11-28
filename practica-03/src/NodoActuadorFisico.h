#pragma once
#include "NodoIoT.h"
#include "NodoSensorFisico.h"

// ---------- Subclase 2: actuador digital ----------
class NodoActuadorFisico : public NodoIoT {
  private:
    bool _estadoActivo;                    // Encapsulamiento del estado de la salida
    const NodoSensorFisico* _sensor;       // Sensor que gobierna al actuador (opcional)

  public:
    NodoActuadorFisico(String id, int pinHardware)
        : NodoIoT(id, pinHardware), _estadoActivo(false), _sensor(nullptr) {}

    void vincularSensor(const NodoSensorFisico* sensor) { _sensor = sensor; }

    void setEstado(bool activo) { _estadoActivo = activo; }
    bool getEstado() const { return _estadoActivo; }

    void iniciar() override {
        pinMode(pin, OUTPUT);
        digitalWrite(pin, LOW);
        NodoIoT::iniciar();
    }

    // Polimorfismo: conmuta la salida física según el estado.
    void ejecutarAccion() override {
        if (_sensor != nullptr) {
            _estadoActivo = _sensor->hayAlerta();
        }
        digitalWrite(pin, _estadoActivo ? HIGH : LOW);
        Serial.println("[" + idDispositivo + "] Salida " + String(_estadoActivo ? "ACTIVA (HIGH)" : "INACTIVA (LOW)"));
    }
};
