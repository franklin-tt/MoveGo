import json
import os
from typing import Dict, List, Optional
from models.base import Vehiculo
from models.carro import Carro
from models.moto import Moto


class GestorVehiculos:
    def __init__(self, ruta_archivo: str = "data/vehiculos.json"):
        self._ruta = ruta_archivo
        self._vehiculos: Dict[str, Vehiculo] = {}
        self._asegurar_directorio()
        self.cargar_desde_json()

    def _asegurar_directorio(self) -> None:
        directorio = os.path.dirname(self._ruta)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)

    def agregar_vehiculo(self, vehiculo: Vehiculo) -> bool:
        if vehiculo.id in self._vehiculos:
            return False
        self._vehiculos[vehiculo.id] = vehiculo
        self.guardar_en_json()
        return True

    def eliminar_vehiculo(self, id_vehiculo: str) -> bool:
        if id_vehiculo in self._vehiculos:
            del self._vehiculos[id_vehiculo]
            self.guardar_en_json()
            return True
        return False

    def obtener_vehiculo(self, id_vehiculo: str) -> Optional[Vehiculo]:
        return self._vehiculos.get(id_vehiculo)

    def listar_todos(self) -> List[Vehiculo]:
        return list(self._vehiculos.values())

    def guardar_en_json(self) -> None:
        datos_guardar = {
            "version": "1.0",
            "vehiculos": [v.to_dict() for v in self._vehiculos.values()]
        }
        with open(self._ruta, "w", encoding="utf-8") as f:
            json.dump(datos_guardar, f, indent=4, ensure_ascii=False)

    def cargar_desde_json(self) -> None:
        if not os.path.exists(self._ruta):
            self._vehiculos = {}
            return

        try:
            with open(self._ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)

            self._vehiculos.clear()
            items = datos.get("vehiculos", [])

            # Bucle para reconstruir objetos polimórficos desde las estructuras anidadas
            for item in items:
                v_id = item["id"]
                tipo = item["tipo"]
                marca = item["marca"]
                modelo = item["modelo"]
                anio = item["anio"]
                specs = item.get("especificaciones", {})
                v_max = specs.get("velocidad_max", 160.0)
                tanque = specs.get("nivel_tanque", 100.0)
                km = specs.get("kilometraje", 0.0)

                if tipo == "Carro":
                    puertas = specs.get("num_puertas", 4)
                    ac = specs.get("aire_acondicionado", True)
                    obj = Carro(v_id, marca, modelo, anio, v_max, puertas, ac, tanque, km)
                elif tipo == "Moto":
                    cc = specs.get("cilindraje", 250)
                    t_manejo = specs.get("tipo_manejo", "Urbano")
                    obj = Moto(v_id, marca, modelo, anio, v_max, cc, t_manejo, tanque, km)
                else:
                    continue

                # Restaurar historial anidado
                metricas = item.get("metricas", {})
                for ruta in metricas.get("historial", []):
                    obj._historial_rutas.append(ruta)

                self._vehiculos[v_id] = obj

        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            self._vehiculos = {}