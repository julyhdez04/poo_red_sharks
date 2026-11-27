#pragma once
#include <Arduino.h>

// ---------- Superclase base ----------
class NodoIoT {
  protected:
    String idDispositivo;
    int pin;
    bool conectado;

  public:
    NodoIoT(String id, int pinHardware) {
        idDispositivo = id;
        pin = pinHardware;
        conectado = false;
    }

    // Destructor virtual: necesario para borrar objetos hijos
    // a través de un puntero NodoIoT*.
    virtual ~NodoIoT() {}

    virtual void iniciar() {
        conectado = true;
        Serial.println("[" + idDispositivo + "] Nodo iniciado en pin " + String(pin));
    }

    // Método polimórfico puro: cada hijo define su propia acción.
    virtual void ejecutarAccion() = 0;

    String getId() const { return idDispositivo; }
    int getPin() const { return pin; }
    bool estaConectado() const { return conectado; }
};
