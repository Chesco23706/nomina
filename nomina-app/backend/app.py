from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

from config import Config
from models import db
from routes.auth_routes import auth_bp
from routes.empleados import empleados_bp
from routes.nomina import nomina_bp


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path="",
    )
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)
    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(empleados_bp)
    app.register_blueprint(nomina_bp)

    with app.app_context():
        db.create_all()
        migrar_esquema()

    registrar_manejo_errores(app)
    registrar_rutas_frontend(app)
    return app


def migrar_esquema() -> None:
    with db.engine.begin() as conexion:
        columnas = conexion.execute(text("PRAGMA table_info(empleados)")).fetchall()
        nombres_columnas = {columna[1] for columna in columnas}
        if "dias_trabajados" not in nombres_columnas:
            conexion.execute(
                text("ALTER TABLE empleados ADD COLUMN dias_trabajados FLOAT NOT NULL DEFAULT 0")
            )
            conexion.execute(
                text("UPDATE empleados SET dias_trabajados = horas_trabajadas")
            )


def registrar_rutas_frontend(app: Flask) -> None:
    @app.get("/")
    def servir_index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/<path:archivo>")
    def servir_archivos(archivo: str):
        ruta = FRONTEND_DIR / archivo
        if ruta.exists() and ruta.is_file():
            return send_from_directory(app.static_folder, archivo)
        return jsonify({"error": "Recurso no encontrado."}), 404


def registrar_manejo_errores(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def manejar_http_exception(error: HTTPException):
        return (
            jsonify(
                {
                    "error": error.name,
                    "mensaje": error.description,
                    "codigo": error.code,
                }
            ),
            error.code,
        )

    @app.errorhandler(Exception)
    def manejar_error_general(error: Exception):
        return (
            jsonify(
                {
                    "error": "Error interno del servidor",
                    "mensaje": str(error),
                    "codigo": 500,
                }
            ),
            500,
        )


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
