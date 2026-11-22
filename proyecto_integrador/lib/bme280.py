import struct
import time


class BME280:
    """Driver BME280 (temperatura, presión, humedad) por I2C."""

    def __init__(self, i2c, addr=0x76):
        self.i2c = i2c
        self.addr = addr

        if i2c.readfrom_mem(addr, 0xD0, 1)[0] != 0x60:
            raise OSError("El chip no es un BME280 (¿es un BMP280?)")

        # Calibración temperatura + presión (24 bytes desde 0x88)
        c = struct.unpack("<HhhHhhhhhhhh", i2c.readfrom_mem(addr, 0x88, 24))
        self.T1, self.T2, self.T3 = c[0:3]
        self.P1, self.P2, self.P3, self.P4, self.P5 = c[3:8]
        self.P6, self.P7, self.P8, self.P9 = c[8:12]

        # Calibración humedad
        self.H1 = i2c.readfrom_mem(addr, 0xA1, 1)[0]
        h = i2c.readfrom_mem(addr, 0xE1, 7)
        self.H2 = struct.unpack("<h", h[0:2])[0]
        self.H3 = h[2]
        self.H4 = (struct.unpack("b", h[3:4])[0] << 4) | (h[4] & 0x0F)
        self.H5 = (struct.unpack("b", h[5:6])[0] << 4) | (h[4] >> 4)
        self.H6 = struct.unpack("b", h[6:7])[0]

        i2c.writeto_mem(addr, 0xF2, b"\x01")  # humedad x1
        i2c.writeto_mem(addr, 0xF5, b"\x00")
        i2c.writeto_mem(addr, 0xF4, b"\x27")  # temp x1, presión x1, modo normal
        time.sleep_ms(50)

    def read(self):
        """Devuelve (temperatura °C, presión hPa, humedad %)."""
        d = self.i2c.readfrom_mem(self.addr, 0xF7, 8)
        adc_p = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        adc_t = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)
        adc_h = (d[6] << 8) | d[7]

        # Temperatura
        v1 = (adc_t / 16384.0 - self.T1 / 1024.0) * self.T2
        v2 = ((adc_t / 131072.0 - self.T1 / 8192.0) ** 2) * self.T3
        t_fine = v1 + v2
        temp = t_fine / 5120.0

        # Presión
        v1 = t_fine / 2.0 - 64000.0
        v2 = v1 * v1 * self.P6 / 32768.0
        v2 = v2 + v1 * self.P5 * 2.0
        v2 = v2 / 4.0 + self.P4 * 65536.0
        v1 = (self.P3 * v1 * v1 / 524288.0 + self.P2 * v1) / 524288.0
        v1 = (1.0 + v1 / 32768.0) * self.P1
        if v1 == 0:
            pres = 0.0
        else:
            p = (1048576.0 - adc_p - v2 / 4096.0) * 6250.0 / v1
            v1 = self.P9 * p * p / 2147483648.0
            v2 = p * self.P8 / 32768.0
            p = p + (v1 + v2 + self.P7) / 16.0
            pres = p / 100.0

        # Humedad
        h = t_fine - 76800.0
        h = (adc_h - (self.H4 * 64.0 + self.H5 / 16384.0 * h)) * (
            self.H2 / 65536.0
            * (1.0 + self.H6 / 67108864.0 * h * (1.0 + self.H3 / 67108864.0 * h))
        )
        h = h * (1.0 - self.H1 * h / 524288.0)
        hum = max(0.0, min(100.0, h))

        return temp, pres, hum
