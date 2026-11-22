from machine import Pin, SPI
import time


class SX127x:
    """Driver mínimo LoRa para Ra-02 (SX1278). Sin interrupciones: usa polling."""

    def __init__(self, spi, cs, rst, freq=433e6, sf=7, bw=7, power=17):
        # bw: 7 = 125 kHz, 8 = 250 kHz, 9 = 500 kHz
        self.spi = spi
        self.cs = cs
        self.cs.value(1)

        rst.value(0)
        time.sleep_ms(10)
        rst.value(1)
        time.sleep_ms(20)

        if self._read(0x42) != 0x12:
            raise OSError("No se detecta el SX127x, revisa el cableado SPI")

        self._write(0x01, 0x80)                      # LoRa + sleep
        time.sleep_ms(10)

        frf = int(freq * 524288 // 32000000)
        self._write(0x06, (frf >> 16) & 0xFF)
        self._write(0x07, (frf >> 8) & 0xFF)
        self._write(0x08, frf & 0xFF)

        self._write(0x0C, 0x23)                      # LNA máxima ganancia
        self._write(0x26, 0x04)                      # AGC automático
        self._write(0x09, 0x80 | (power - 2))        # PA_BOOST
        self._write(0x1D, (bw << 4) | (1 << 1))      # BW, CR 4/5, header explícito
        self._write(0x1E, (sf << 4) | 0x04)          # SF, CRC activado
        self._write(0x20, 0x00)
        self._write(0x21, 0x08)                      # preámbulo = 8
        self._write(0x39, 0x12)                      # sync word
        self._write(0x0E, 0x00)                      # base TX
        self._write(0x0F, 0x00)                      # base RX
        self._write(0x01, 0x81)                      # standby

    # ---- SPI ----
    def _read(self, reg):
        self.cs.value(0)
        self.spi.write(bytes([reg & 0x7F]))
        r = self.spi.read(1)
        self.cs.value(1)
        return r[0]

    def _write(self, reg, val):
        self.cs.value(0)
        self.spi.write(bytes([reg | 0x80, val]))
        self.cs.value(1)

    # ---- Transmitir ----
    def enviar(self, datos, timeout_ms=3000):
        self._write(0x01, 0x81)                      # standby
        self._write(0x0D, 0x00)                      # puntero FIFO = 0
        self.cs.value(0)
        self.spi.write(bytes([0x80]))                # escritura en FIFO
        self.spi.write(datos)
        self.cs.value(1)
        self._write(0x22, len(datos))
        self._write(0x12, 0xFF)                      # limpia banderas
        self._write(0x01, 0x83)                      # TX
        t0 = time.ticks_ms()
        while not (self._read(0x12) & 0x08):         # TxDone
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
                self._write(0x01, 0x81)
                return False
            time.sleep_ms(1)
        self._write(0x12, 0xFF)
        return True

    # ---- Recibir ----
    def escuchar(self):
        self._write(0x0F, 0x00)
        self._write(0x12, 0xFF)
        self._write(0x01, 0x85)                      # RX continuo

    def recibir(self):
        """Devuelve (bytes, rssi, snr) o None si no hay paquete."""
        flags = self._read(0x12)
        if not (flags & 0x40):                       # RxDone
            return None
        self._write(0x12, 0xFF)
        if flags & 0x20:                             # error de CRC
            return None
        n = self._read(0x13)
        self._write(0x0D, self._read(0x10))
        self.cs.value(0)
        self.spi.write(bytes([0x00]))
        datos = self.spi.read(n)
        self.cs.value(1)
        snr = self._read(0x19)
        if snr > 127:
            snr -= 256
        rssi = self._read(0x1A) - 164                # banda baja (433 MHz)
        return datos, rssi, snr / 4
