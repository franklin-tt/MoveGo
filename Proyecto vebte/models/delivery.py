import time


class PedidoDelivery:
    def __init__(
        self,
        id_pedido: str,
        cliente: str,
        direccion: str,
        distancia_km: float,
        tarifa_base_km: float = 1.5,
    ):
        self.id_pedido = id_pedido
        self.cliente = cliente
        self.direccion = direccion
        self.distancia_km = distancia_km
        self.tarifa_base_km = tarifa_base_km
        self.estado = "Pendiente"
        self.pago_confirmado = False
        self.timestamp = time.time()

    def calcular_total(self) -> float:
        return round(self.distancia_km * self.tarifa_base_km + 2.0, 2)

    def procesar_pago(self, metodo_pago: str) -> bool:
        if metodo_pago in ["Tarjeta", "Pago Móvil", "Efectivo", "PayPal"]:
            self.pago_confirmado = True
            self.estado = "En Camino"
            return True
        return False