from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Empleado(db.Model):
    __tablename__ = "empleados"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(120), nullable=False)
    puesto = db.Column(db.String(120), nullable=False)
    salario_base = db.Column(db.Float, nullable=False)
    horas_trabajadas = db.Column(db.Float, nullable=False)
    dias_trabajados = db.Column(db.Float, nullable=False, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "puesto": self.puesto,
            "salario_base": self.salario_base,
            "horas_trabajadas": self.horas_trabajadas,
            "horas_jornada": self.horas_trabajadas,
            "dias_trabajados": self.dias_trabajados,
        }


def validar_datos_empleado(payload: dict, parcial: bool = False) -> tuple[dict, list[str]]:
    errores: list[str] = []
    datos: dict = {}
    campos_requeridos = ("nombre", "puesto", "salario_base", "dias_trabajados", "horas_jornada")

    if not isinstance(payload, dict):
        return {}, ["El cuerpo de la solicitud debe ser un JSON válido."]

    for campo in campos_requeridos:
        if parcial and campo not in payload:
            continue

        valor = payload.get(campo)
        if campo == "dias_trabajados" and valor is None:
            valor = payload.get("dias")
        if campo == "horas_jornada" and valor is None:
            valor = payload.get("horas_trabajadas")
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            errores.append(f"El campo '{campo}' es obligatorio.")
            continue

        if campo in {"nombre", "puesto"}:
            datos[campo] = str(valor).strip()
            continue

        try:
            numero = float(valor)
        except (TypeError, ValueError):
            errores.append(f"El campo '{campo}' debe ser numérico.")
            continue

        if numero < 0:
            errores.append(f"El campo '{campo}' no puede ser negativo.")
            continue

        datos[campo] = numero
        if campo == "horas_jornada":
            datos["horas_trabajadas"] = numero
            datos.pop("horas_jornada", None)

    return datos, errores
