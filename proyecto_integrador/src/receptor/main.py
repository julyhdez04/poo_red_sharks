from machine import Pin, SPI
import time

from sx127x import SX127x

# ---------- LoRa Ra-02 por SPI0 (mismos pines que el transmisor) ----------
spi = SPI(0, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(19), miso=Pin(16))
lora = SX127x(spi, cs=Pin(17, Pin.OUT), rst=Pin(20, Pin.OUT))
lora.escuchar()
print("Receptor LoRa listo, esperando datos...")

# ---------- Bucle principal ----------
while True:
    r = lora.recibir()
    if r is None:
        time.sleep_ms(10)
        continue

    datos, rssi, snr = r
    try:
        texto = datos.decode()
    except Exception:
        print("Paquete invalido:", datos)
        continue

    # t;p;h;fix;lat;lon;alt;sats;hora  (9 campos)
    c = texto.split(";")
    if len(c) != 9:
        print("Paquete invalido:", texto)
        continue

    # Mismo formato que lee el panel HTML
    print("-" * 30)
    print("Temperatura: {} °C".format(c[0]))
    print("Presión:     {} hPa".format(c[1]))
    print("Humedad:     {} %".format(c[2]))

    if c[3] == "1":
        print("GPS: lat {}, lon {}".format(c[4], c[5]))
        print("     alt {} m, satélites {}, {}".format(
            c[6] or "None", c[7], c[8] or "--"))
    else:
        print("GPS: buscando señal... satélites: {}".format(c[7]))

    print("LoRa RSSI {} dBm, SNR {} dB".format(rssi, snr))
