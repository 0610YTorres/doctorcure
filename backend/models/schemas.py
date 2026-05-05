from pydantic import BaseModel
from typing import Optional, List, Dict


class PatientData(BaseModel):
    # ── Sección I: Identificación ──────────────────────────────────────────────
    nombre_paciente: Optional[str] = None       # nombre completo (display)
    nombre: Optional[str] = None                # nombres (D6)
    apellidos: Optional[str] = None             # apellidos (J6)
    documento: Optional[str] = None             # CC — también va en Historia Clínica No. (F4)
    tipo_documento: Optional[str] = None
    edad: Optional[str] = None                  # (P4)
    sexo: Optional[str] = None
    fecha_atencion: Optional[str] = None        # Fecha de atención (J4/K4/L4)
    medico_tratante: Optional[str] = None       # (F8)
    especialidad: Optional[str] = None          # (P8)
    entidad: Optional[str] = None               # institución (J10)
    fecha_diagnostico: Optional[str] = None     # (E10)

    # ── Sección II: Resumen ───────────────────────────────────────────────────
    resumen_historia: Optional[str] = None      # (B14)

    # ── Sección III: Diagnóstico ──────────────────────────────────────────────
    diagnostico_cie10: Optional[str] = None
    diagnostico_descripcion: Optional[str] = None
    diagnostico_clinico: Optional[str] = None   # CIE10 + descripción (G25)
    diagnostico_patologico: Optional[str] = None  # resultado patología (N25)
    tipo_cancer: Optional[str] = None

    # TNM desglosado (C27/E27/G27/I27)
    tnm_t: Optional[str] = None
    tnm_n: Optional[str] = None
    tnm_m: Optional[str] = None
    estadificacion: Optional[str] = None        # EST (I27)

    # ── Sección III: Imágenes diagnósticas ────────────────────────────────────
    ecografia: Optional[str] = None             # (D31)
    tac: Optional[str] = None                   # (F31)
    rmn: Optional[str] = None                   # (H31)
    pet: Optional[str] = None                   # (J31)
    mamografia: Optional[str] = None            # (O31)
    informes_imagenes: Optional[str] = None     # (B34)

    # ── Sección III: Tratamientos ─────────────────────────────────────────────
    cirugia_recibio: Optional[str] = None       # Sí/No (D38)
    cirugia_fecha: Optional[str] = None         # (F38)
    cirugia_tipo: Optional[str] = None          # (J38)

    quimioterapia_recibio: Optional[str] = None  # Sí/No (E40)
    quimioterapia_esquema: Optional[str] = None  # (I40)

    radioterapia_recibio: Optional[str] = None  # Sí/No (E42)
    radioterapia_dosis: Optional[str] = None    # (G42)

    hormonoterapia_recibio: Optional[str] = None  # Sí/No (E44)
    hormonoterapia_tipo: Optional[str] = None     # (G44)

    # ── Compatibilidad / display ──────────────────────────────────────────────
    tratamiento_inicial: Optional[str] = None
    resultado_tratamiento: Optional[str] = None


class ExtractionResult(BaseModel):
    success: bool
    data: PatientData
    raw_text: str
    confidence: Dict[str, float] = {}
    warnings: List[str] = []
    method: str = "text"


class ExportRequest(BaseModel):
    data: PatientData
    filename: Optional[str] = None
