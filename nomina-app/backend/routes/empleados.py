from __future__ import annotations

from flask import Blueprint, jsonify, request

from auth import login_requerido
from models import Empleado, db, validar_datos_empleado


empleados_bp = Blueprint("empleados", __name__)


@empleados_bp.post("/empleados")
@login_requerido
def crear_empleado():
    datos, errores = validar_datos_empleado(request.get_json(silent=True) or {})
    if errores:
        return jsonify({"error": "Datos inválidos", "detalles": errores}), 400

    empleado = Empleado(**datos)
    db.session.add(empleado)
    db.session.commit()
    return jsonify(empleado.to_dict()), 201


@empleados_bp.get("/empleados")
@login_requerido
def listar_empleados():
    empleados = Empleado.query.order_by(Empleado.id.asc()).all()
    return jsonify([empleado.to_dict() for empleado in empleados]), 200


@empleados_bp.get("/empleados/<int:empleado_id>")
@login_requerido
def obtener_empleado(empleado_id: int):
    empleado = Empleado.query.get_or_404(empleado_id, description="Empleado no encontrado.")
    return jsonify(empleado.to_dict()), 200


@empleados_bp.put("/empleados/<int:empleado_id>")
@login_requerido
def actualizar_empleado(empleado_id: int):
    empleado = Empleado.query.get_or_404(empleado_id, description="Empleado no encontrado.")
    datos, errores = validar_datos_empleado(
        request.get_json(silent=True) or {},
        parcial=True,
    )
    if errores:
        return jsonify({"error": "Datos inválidos", "detalles": errores}), 400

    if not datos:
        return jsonify({"error": "No se enviaron campos para actualizar."}), 400

    for clave, valor in datos.items():
        setattr(empleado, clave, valor)

    db.session.commit()
    return jsonify(empleado.to_dict()), 200


@empleados_bp.delete("/empleados/<int:empleado_id>")
@login_requerido
def eliminar_empleado(empleado_id: int):
    empleado = Empleado.query.get_or_404(empleado_id, description="Empleado no encontrado.")
    db.session.delete(empleado)
    db.session.commit()
    return jsonify({"mensaje": "Empleado eliminado correctamente."}), 200
