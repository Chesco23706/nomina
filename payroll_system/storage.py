from __future__ import annotations

import json
from pathlib import Path

from payroll_system.models import Empleado


class RepositorioEmpleados:
    def __init__(self, ruta_archivo: str | Path = "data/empleados.json") -> None:
        self.ruta_archivo = Path(ruta_archivo)

    def cargar(self) -> list[Empleado]:
        if not self.ruta_archivo.exists():
            return []

        with self.ruta_archivo.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return [Empleado.from_dict(item) for item in datos]

    def guardar(self, empleados: list[Empleado]) -> None:
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        datos = [empleado.to_dict() for empleado in empleados]
        with self.ruta_archivo.open("w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
