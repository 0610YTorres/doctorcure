import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import export, upload
from utils.paths import get_frontend_out

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

app = FastAPI(
    title="DoctorCure API",
    description="Extracción automática de historias clínicas en PDF → Excel",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(export.router, prefix="/api", tags=["export"])


@app.get("/api/health", tags=["system"])
async def health():
    return {"status": "ok", "service": "DoctorCure API"}


# ── Servir frontend estático (Next.js export) ─────────────────────────────────
FRONTEND_OUT = get_frontend_out()

if FRONTEND_OUT.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_OUT), html=True), name="frontend")
else:
    import warnings
    warnings.warn(
        f"frontend/out/ no encontrado en {FRONTEND_OUT}. "
        "Ejecute: cd frontend && npm run build",
        stacklevel=1,
    )
