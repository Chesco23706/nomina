import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = Path("/tmp/nomina-database") if os.getenv("VERCEL") else BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "NOMINA_DATABASE_URL",
        f"sqlite:///{DATABASE_DIR / 'nomina.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    SECRET_KEY = os.getenv("NOMINA_SECRET_KEY", "cambia-esta-clave-en-produccion")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    ADMIN_USER = os.getenv("NOMINA_ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.getenv("NOMINA_ADMIN_PASSWORD", "admin123")
