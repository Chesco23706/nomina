from __future__ import annotations

import csv
from io import StringIO

from flask import Blueprint, Response, jsonify

from auth import login_requerido
from models import Empleado


nomina_bp = Blueprint("nomina", __name__)

ISR_PORCENTAJE = 0.10
IMSS_PORCENTAJE = 0.05


def calcular_desglose(empleado: Empleado) -> dict:
    salario_bruto = empleado.salario_base * empleado.dias_trabajados * empleado.horas_trabajadas
    isr = salario_bruto * ISR_PORCENTAJE
    imss = salario_bruto * IMSS_PORCENTAJE
    salario_neto = salario_bruto - isr - imss

    return {
        "empleado": empleado.to_dict(),
        "salario_bruto": round(salario_bruto, 2),
        "isr": round(isr, 2),
        "imss": round(imss, 2),
        "salario_neto": round(salario_neto, 2),
        "porcentajes": {
            "isr": int(ISR_PORCENTAJE * 100),
            "imss": int(IMSS_PORCENTAJE * 100),
        },
    }


@nomina_bp.post("/nomina/calcular/<int:empleado_id>")
@login_requerido
def calcular_nomina(empleado_id: int):
    empleado = Empleado.query.get_or_404(empleado_id, description="Empleado no encontrado.")
    return jsonify(calcular_desglose(empleado)), 200


@nomina_bp.get("/nomina/recibo/<int:empleado_id>")
@login_requerido
def obtener_recibo(empleado_id: int):
    empleado = Empleado.query.get_or_404(empleado_id, description="Empleado no encontrado.")
    recibo = calcular_desglose(empleado)
    recibo["mensaje"] = "Recibo de nomina generado correctamente."
    return jsonify(recibo), 200


@nomina_bp.get("/nomina/resumen")
@login_requerido
def obtener_resumen():
    empleados = Empleado.query.order_by(Empleado.nombre.asc()).all()
    desgloses = [calcular_desglose(empleado) for empleado in empleados]
    totales = {
        "empleados": len(desgloses),
        "salario_bruto": round(sum(item["salario_bruto"] for item in desgloses), 2),
        "isr": round(sum(item["isr"] for item in desgloses), 2),
        "imss": round(sum(item["imss"] for item in desgloses), 2),
        "salario_neto": round(sum(item["salario_neto"] for item in desgloses), 2),
    }
    return jsonify({"totales": totales, "detalle": desgloses}), 200


@nomina_bp.get("/nomina/reporte.csv")
@login_requerido
def exportar_reporte_csv():
    empleados = Empleado.query.order_by(Empleado.nombre.asc()).all()
    salida = StringIO()
    writer = csv.writer(salida)
    writer.writerow(
        [
            "ID",
            "Empleado",
            "Puesto",
            "Salario por hora",
            "Dias trabajados",
            "Horas por jornada",
            "Salario bruto",
            "ISR",
            "IMSS",
            "Salario neto",
        ]
    )

    for empleado in empleados:
        desglose = calcular_desglose(empleado)
        writer.writerow(
            [
                empleado.id,
                empleado.nombre,
                empleado.puesto,
                empleado.salario_base,
                empleado.dias_trabajados,
                empleado.horas_trabajadas,
                desglose["salario_bruto"],
                desglose["isr"],
                desglose["imss"],
                desglose["salario_neto"],
            ]
        )

    return Response(
        salida.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=reporte_nomina.csv"},
    )
