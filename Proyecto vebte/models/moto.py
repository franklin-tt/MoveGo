import math
from models.base import Vehiculo


class Moto(Vehiculo):
    def __init__(
        self,
        id_vehiculo: str,
        marca: str,
        modelo: str,
        anio: int,
        velocidad_max: float,
        cilindraje: int = 250,
        tipo_manejo: str = "Deportivo",
        nivel_tanque: float = 100.0,
        kilometraje: float = 0.0,
    ):
        super().__init__(
            id_vehiculo, marca, modelo, anio, velocidad_max, nivel_tanque, kilometraje
        )
        self._cilindraje = cilindraje
        self._tipo_manejo = tipo_manejo

    @property
    def cilindraje(self) -> int:
        return self._cilindraje

    @property
    def tipo_manejo(self) -> str:
        return self._tipo_manejo

    def obtener_tipo(self) -> str:
        return "Moto"

    def calcular_consumo(self, distancia_km: float) -> float:
        # Consumo según cilindraje mediante fórmula logarítmica
        factor_cilindraje = (math.log(self._cilindraje) / 100.0)
        return distancia_km * factor_cilindraje

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["especificaciones"]["cilindraje"] = self._cilindraje
        data["especificaciones"]["tipo_manejo"] = self._tipo_manejo
        return data