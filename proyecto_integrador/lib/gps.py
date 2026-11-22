def nmea_a_decimal(valor, hemisferio):
    if not valor:
        return None
    punto = valor.index(".")
    grados = int(valor[:punto - 2])
    minutos = float(valor[punto - 2:])
    dec = grados + minutos / 60
    if hemisferio in ("S", "W"):
        dec = -dec
    return dec


class GPS:
    """Lector NMEA (GGA) por UART. Llama a update() seguido en el bucle."""

    def __init__(self, uart):
        self.uart = uart
        self.buffer = b""
        self.bytes_recibidos = 0
        self.fix = False
        self.lat = None
        self.lon = None
        self.alt = None
        self.sats = 0
        self.hora = None

    def _procesar(self, linea):
        partes = linea.split(",")
        tipo = partes[0][3:]   # GGA, RMC, etc. (ignora GP/GN)
        if tipo == "GGA" and len(partes) > 9:
            self.fix = partes[6] not in ("", "0")
            self.sats = int(partes[7]) if partes[7] else 0
            if self.fix:
                self.lat = nmea_a_decimal(partes[2], partes[3])
                self.lon = nmea_a_decimal(partes[4], partes[5])
                self.alt = float(partes[9]) if partes[9] else None
            if partes[1]:
                t = partes[1]
                self.hora = "{}:{}:{} UTC".format(t[0:2], t[2:4], t[4:6])

    def update(self):
        """Acumula bytes y procesa solo líneas NMEA completas."""
        n = self.uart.any()
        if n:
            datos = self.uart.read(n)
            if datos:
                self.bytes_recibidos += len(datos)
                self.buffer += datos
        while b"\n" in self.buffer:
            linea, self.buffer = self.buffer.split(b"\n", 1)
            try:
                texto = linea.decode("ascii", "ignore").strip()
                if texto.startswith("$"):
                    self._procesar(texto)
            except Exception:
                pass  # línea corrupta, se ignora
        if len(self.buffer) > 512:   # evita que crezca si no hay saltos de línea
            self.buffer = b""
