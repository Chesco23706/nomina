from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from auth import password_valido, usuario_actual


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/auth/status")
def estado_sesion():
    usuario = usuario_actual()
    return jsonify({"autenticado": usuario is not None, "usuario": usuario}), 200


@auth_bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    usuario = str(payload.get("usuario", "")).strip()
    password = str(payload.get("password", ""))

    if not usuario or not password:
        return jsonify({"error": "Usuario y contrasena son obligatorios."}), 400

    if not password_valido(usuario, password):
        return jsonify({"error": "Credenciales incorrectas."}), 401

    session.clear()
    session["usuario"] = usuario
    session["rol"] = "Administrador"
    return jsonify({"mensaje": "Sesion iniciada correctamente.", "usuario": usuario}), 200


@auth_bp.post("/auth/logout")
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesion cerrada correctamente."}), 200
