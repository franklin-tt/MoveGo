import math
from models.base import Vehiculo


class Carro(Vehiculo):
    def __init__(
        self,
        id_vehiculo: str,
        marca: str,
        modelo: str,
        anio: int,
        velocidad_max: float,
        num_puertas: int = 4,
        aire_acondicionado: bool = True,
        nivel_tanque: float = 100.0,
        kilometraje: float = 0.0,
    ):
        super().__init__(
            id_vehiculo, marca, modelo, anio, velocidad_max, nivel_tanque, kilometraje
        )
        self._num_puertas = num_puertas
        self._aire_acondicionado = aire_acondicionado

    @property
    def num_puertas(self) -> int:
        return self._num_puertas

    @property
    def aire_acondicionado(self) -> bool:
        return self._aire_acondicionado

    def obtener_tipo(self) -> str:
        return "Carro"

    def calcular_consumo(self, distancia_km: float) -> float:
        # Base: 8.5L / 100km -> 0.085L por km
        factor_base = 0.085
        factor_ac = 1.15 if self._aire_acondicionado else 1.0
        # Carga por puertas: mayor peso estructural
        peso_adicional = math.sqrt(self._num_puertas) * 0.005
        return distancia_km * (factor_base + peso_adicional) * factor_ac

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["especificaciones"]["num_puertas"] = self._num_puertas
        data["especificaciones"]["aire_acondicionado"] = self._aire_acondicionado
        return data