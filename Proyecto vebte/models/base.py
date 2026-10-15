import abc
import math
import random
import time


class Vehiculo(abc.ABC):
    def __init__(
        self,
        id_vehiculo: str,
        marca: str,
        modelo: str,
        anio: int,
        velocidad_max: float,
        nivel_tanque: float = 100.0,
        kilometraje: float = 0.0,
    ):
        self._id = id_vehiculo
        self._marca = marca
        self._modelo = modelo
        self._anio = anio
        self._velocidad_max = float(velocidad_max)
        self._nivel_tanque = float(nivel_tanque)
        self._kilometraje = float(kilometraje)
        self._historial_rutas = []
        self._timestamp_creacion = time.time()

    @property
    def id(self) -> str:
        return self._id

    @property
    def marca(self) -> str:
        return self._marca

    @property
    def modelo(self) -> str:
        return self._modelo

    @property
    def anio(self) -> int:
        return self._anio

    @property
    def velocidad_max(self) -> float:
        return self._velocidad_max

    @property
    def nivel_tanque(self) -> float:
        return self._nivel_tanque

    @property
    def kilometraje(self) -> float:
        return self._kilometraje

    @abc.abstractmethod
    def calcular_consumo(self, distancia_km: float) -> float:
        """Cálculo específico de consumo de combustible según tipo de vehículo."""
        pass

    @abc.abstractmethod
    def obtener_tipo(self) -> str:
        """Devuelve el tipo identificador del vehículo."""
        pass

    def simular_recorrido(self, distancia_km: float) -> dict:
        """
        Simula una ruta calculando aceleración, resistencia y consumo
        usando math, random y time.
        """
        tiempo_inicio = time.time()
        
        # Variabilidad aleatoria de velocidad promedio (70% - 95% de la velocidad máx)
        factor_trafico = random.uniform(0.70, 0.95)
        velocidad_media = self._velocidad_max * factor_trafico

        # Tiempo estimado de viaje en horas: t = d / v
        tiempo_estimado_horas = distancia_km / velocidad_media
        
        # Consumo de combustible base según el modelo
        combustible_requerido = self.calcular_consumo(distancia_km)

        # Cálculo trigonométrico simulando desgaste por pendientes de ruta
        angulo_terreno = math.radians(random.randint(2, 12))
        resistencia_gravedad = math.sin(angulo_terreno) * 1.5
        combustible_final = combustible_requerido * (1 + resistencia_gravedad)

        if combustible_final > self._nivel_tanque:
            distancia_posible = (self._nivel_tanque / combustible_final) * distancia_km
            self._kilometraje += distancia_posible
            self._nivel_tanque = 0.0
            completado = False
        else:
            self._kilometraje += distancia_km
            self._nivel_tanque -= combustible_final
            completado = True

        registro = {
            "timestamp": time.time(),
            "duracion_simulacion_seg": round(time.time() - tiempo_inicio, 4),
            "distancia_solicitada": distancia_km,
            "combustible_consumido": round(combustible_final, 2),
            "velocidad_promedio": round(velocidad_media, 2),
            "completado": completado,
        }
        self._historial_rutas.append(registro)
        return registro

    def recargar_tanque(self, litros: float) -> float:
        self._nivel_tanque = min(100.0, self._nivel_tanque + litros)
        return self._nivel_tanque

    def to_dict(self) -> dict:
        """Estructura de datos anidada para serialización JSON."""
        return {
            "id": self._id,
            "tipo": self.obtener_tipo(),
            "marca": self._marca,
            "modelo": self._modelo,
            "anio": self._anio,
            "especificaciones": {
                "velocidad_max": self._velocidad_max,
                "nivel_tanque": round(self._nivel_tanque, 2),
                "kilometraje": round(self._kilometraje, 2),
            },
            "metricas": {
                "timestamp_creacion": self._timestamp_creacion,
                "total_viajes": len(self._historial_rutas),
                "historial": self._historial_rutas,
            },
        }