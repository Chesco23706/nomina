from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Empleado:
    id_empleado: str
    nombre: str
    puesto: str
    salario_base: float
    horas_trabajadas: float

    def actualizar(
        self,
        nombre: str | None = None,
        puesto: str | None = None,
        salario_base: float | None = None,
        horas_trabajadas: float | None = None,
    ) -> None:
        if nombre is not None:
            self.nombre = nombre
        if puesto is not None:
            self.puesto = puesto
        if salario_base is not None:
            self.salario_base = salario_base
        if horas_trabajadas is not None:
            self.horas_trabajadas = horas_trabajadas

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Empleado":
        return cls(
            id_empleado=str(data["id_empleado"]),
            nombre=str(data["nombre"]),
            puesto=str(data["puesto"]),
            salario_base=float(data["salario_base"]),
            horas_trabajadas=float(data["horas_trabajadas"]),
        )


@dataclass
class ResultadoNomina:
    empleado: Empleado
    salario_bruto: float
    descuento_isr: float
    descuento_imss: float
    salario_neto: float

    def como_texto(self, isr_pct: float, imss_pct: float) -> str:
        lineas = [
            "RECIBO DE NOMINA",
            "=" * 40,
            f"Empleado: {self.empleado.nombre}",
            f"ID: {self.empleado.id_empleado}",
            f"Puesto: {self.empleado.puesto}",
            f"Salario por hora: ${self.empleado.salario_base:,.2f}",
            f"Horas trabajadas: {self.empleado.horas_trabajadas:,.2f}",
            "-" * 40,
            f"Salario bruto: ${self.salario_bruto:,.2f}",
            f"ISR ({isr_pct:.2f}%): -${self.descuento_isr:,.2f}",
            f"IMSS ({imss_pct:.2f}%): -${self.descuento_imss:,.2f}",
            "-" * 40,
            f"Salario neto: ${self.salario_neto:,.2f}",
            "=" * 40,
        ]
        return "\n".join(lineas)
