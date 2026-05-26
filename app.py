from __future__ import annotations

import sys
import importlib.util
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent / "nomina-app" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

spec = importlib.util.spec_from_file_location("nomina_backend_app", BACKEND_DIR / "app.py")
if spec is None or spec.loader is None:
    raise RuntimeError("No se pudo cargar la aplicacion Flask.")

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = module.app
