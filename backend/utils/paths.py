"""
Resolución de rutas compatible con desarrollo y PyInstaller bundle.

En desarrollo:
    backend/utils/paths.py  →  base = backend/
    frontend/out/           →  base/../frontend/out
    backend/templates/      →  base/templates/

En bundle PyInstaller (_MEIPASS):
    Todos los recursos se copian a _MEIPASS/
    _MEIPASS/frontend/out/
    _MEIPASS/templates/
"""

import sys
from pathlib import Path


def _base() -> Path:
    """Raíz del bundle (PyInstaller) o del directorio backend (desarrollo)."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent  # backend/


def get_frontend_out() -> Path:
    base = _base()
    if hasattr(sys, "_MEIPASS"):
        return base / "frontend" / "out"
    return base.parent / "frontend" / "out"   # dev: DoctorCure/frontend/out


def get_templates_dir() -> Path:
    return _base() / "templates"


def get_template_xlsx() -> Path:
    return get_templates_dir() / "plantilla_comite_tumores.xlsx"
