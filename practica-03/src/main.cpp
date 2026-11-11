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

    virtual void iniciar() {
    }

    virtual void ejecutarAccion() = 0; 
};

class NodoSensorFisico : public NodoIoT {
  private:
    int _umbralAlerta; // Encapsulamiento

  public:
    NodoSensorFisico(String id, int pinHardware) : NodoIoT(id, pinHardware) {
        _umbralAlerta = 2048; // Valor por defecto
    }

    void setUmbralAlerta(int umbral) {
        if (umbral >= 0 && umbral <= 4095) {
            _umbralAlerta = umbral;
        } else {
            Serial.println("Error: Umbral fuera de rango.");
        }
    }