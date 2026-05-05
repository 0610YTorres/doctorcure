import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import export, upload

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

app = FastAPI(
    title="DoctorCure API",
    description="Extracción automática de historias clínicas en PDF → Excel",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # mismo origen en producción (localhost:8000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(export.router, prefix="/api", tags=["export"])


@app.get("/api/health", tags=["system"])
async def health():
    return {"status": "ok", "service": "DoctorCure API"}


# ── Servir el frontend (Next.js export estático) ───────────────────────────────
# La carpeta "out/" se genera con: cd frontend && npm run build
FRONTEND_OUT = Path(__file__).parent.parent / "frontend" / "out"

if FRONTEND_OUT.exists():
    # StaticFiles con html=True sirve index.html automáticamente en "/"
    app.mount("/", StaticFiles(directory=str(FRONTEND_OUT), html=True), name="frontend")
else:
    import warnings
    warnings.warn(
        f"Carpeta frontend/out/ no encontrada en {FRONTEND_OUT}. "
        "Ejecute: cd frontend && npm run build",
        stacklevel=1,
    )
