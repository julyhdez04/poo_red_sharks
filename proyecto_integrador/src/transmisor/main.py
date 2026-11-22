from machine import Pin, I2C, UART, SPI
import time

from bme280 import BME280
from gps import GPS
from sx127x import SX127x

INTERVALO_MS = 3000

# ---------- Configuración ----------
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
direcciones = i2c.scan()
print("Dispositivos I2C:", [hex(x) for x in direcciones])

if 0x76 in direcciones:
    sensor = BME280(i2c, 0x76)
elif 0x77 in direcciones:
    sensor = BME280(i2c, 0x77)
else:
    raise OSError("No se encontró el BME280, revisa SDA/SCL")

# GPS: TX del módulo -> GP1
gps = GPS(UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1)))

# LoRa Ra-02 por SPI0
spi = SPI(0, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(19), miso=Pin(16))
lora = SX127x(spi, cs=Pin(17, Pin.OUT), rst=Pin(20, Pin.OUT))
print("LoRa listo")

# ---------- Bucle principal ----------
ultimo = time.ticks_ms()
while True:
    gps.update()

    if time.ticks_diff(time.ticks_ms(), ultimo) >= INTERVALO_MS:
        ultimo = time.ticks_ms()
        t, p, h = sensor.read()

        con_fix = gps.fix and gps.lat is not None
        lat = "{:.6f}".format(gps.lat) if con_fix else ""
        lon = "{:.6f}".format(gps.lon) if con_fix else ""
        alt = "{:.1f}".format(gps.alt) if con_fix and gps.alt is not None else ""

        paquete = "{:.2f};{:.2f};{:.1f};{};{};{};{};{};{}".format(
            t, p, h, 1 if con_fix else 0, lat, lon, alt,
            gps.sats, gps.hora or "")

        ok = lora.enviar(paquete.encode())
        print("TX", "ok" if ok else "FALLÓ", paquete)

    time.sleep_ms(20)
