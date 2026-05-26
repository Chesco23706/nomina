from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from flask import current_app, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash


def password_valido(usuario: str, password: str) -> bool:
    usuario_configurado = current_app.config["ADMIN_USER"]
    password_configurado = current_app.config["ADMIN_PASSWORD"]
    hash_password = generate_password_hash(password_configurado)
    return usuario == usuario_configurado and check_password_hash(hash_password, password)


def usuario_actual() -> dict[str, str] | None:
    usuario = session.get("usuario")
    if not usuario:
        return None
    return {"usuario": str(usuario), "rol": str(session.get("rol", "Administrador"))}


def login_requerido(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if usuario_actual() is None:
            return jsonify({"error": "No autorizado", "mensaje": "Inicia sesion para continuar."}), 401
        return func(*args, **kwargs)

    return wrapper
