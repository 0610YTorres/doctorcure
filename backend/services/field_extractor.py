import re
import logging
from typing import Optional

from models.schemas import PatientData
from utils.patterns import (
    PATTERNS,
    normalize_doc_number,
    normalize_sex,
    infer_cancer_type_from_cie10,
    infer_cancer_type_from_text,
    identify_treatment_from_text,
    identify_result_from_text,
    TREATMENT_KEYWORDS,
)

logger = logging.getLogger(__name__)

_INVALID_RE = re.compile(
    r"(?i)^\s*(?:no\s+aplica|no\s+apply|n\.?\/?a\.?|desconocido|unknown|"
    r"sin\s+dato|s\.?d\.?|no\s+registra|no\s+reporta|---?|\.+|"
    r"subsidiado|contributivo|r[eé]gimen\s+subsidiado|r[eé]gimen\s+contributivo)\s*$"
)

NOTA_RESUMEN = (
    "⚠️ VALIDACIÓN REQUERIDA: El resumen de la historia clínica debe ser "
    "elaborado por el médico tratante a partir del documento completo. "
    "Los datos clave extraídos automáticamente se encuentran en las secciones "
    "III (Diagnóstico) y Tratamientos."
)


def _is_invalid(value: str) -> bool:
    return bool(_INVALID_RE.match(value.strip()))


def extract_fields(text: str) -> tuple[PatientData, dict[str, float], list[str]]:
    """
    Cascade regex extraction for all clinical fields.
    Returns (PatientData, confidence_scores, warnings).
    """
    confidence: dict[str, float] = {}
    warnings: list[str] = []

    def first_match(field: str, patterns: list[str], transform=None) -> Optional[str]:
        for i, pattern in enumerate(patterns):
            for m in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
                groups = [g for g in m.groups() if g]
                if not groups:
                    continue
                value = " ".join(groups).strip()
                value = re.sub(r"\s+", " ", value)
                if _is_invalid(value):
                    continue
                if transform:
                    value = transform(value)
                confidence[field] = max(1.0 - i * 0.15, 0.4)
                return value
        confidence[field] = 0.0
        return None

    def treatment_present(keywords: list[str]) -> bool:
        tl = text.lower()
        return any(kw in tl for kw in keywords)

    # ── Identificación ─────────────────────────────────────────────────────────
    nombre_completo = first_match("nombre_paciente", PATTERNS["nombre_paciente"])
    if nombre_completo:
        nombre_completo = _clean_name(nombre_completo)

    nombre, apellidos = _split_name(nombre_completo) if nombre_completo else (None, None)

    documento_raw = first_match("documento", PATTERNS["documento"])
    documento = normalize_doc_number(documento_raw) if documento_raw else None

    tipo_doc_raw = first_match("tipo_documento", PATTERNS["tipo_documento"])
    tipo_doc = _normalize_doc_type(tipo_doc_raw) if tipo_doc_raw else None

    edad = first_match("edad", PATTERNS["edad"])
    if edad:
        edad = re.sub(r"[^\d]", "", edad.split()[0])[:3]

    sexo_raw = first_match("sexo", PATTERNS["sexo"])
    sexo = normalize_sex(sexo_raw) if sexo_raw else None

    fecha_atencion = first_match("fecha_atencion", PATTERNS["fecha_atencion"])

    medico = first_match("medico_tratante", PATTERNS["medico_tratante"])
    if medico:
        medico = _clean_name(medico)

    especialidad = first_match("especialidad", PATTERNS["especialidad"])

    entidad = first_match("entidad", PATTERNS["entidad"])
    if not entidad:
        entidad = _extract_institution_from_header(text)
    # Limpiar términos de régimen de salud del nombre de la entidad
    if entidad:
        entidad = re.sub(
            r"(?i)\s*[-–]?\s*(?:r[eé]gimen\s+)?(?:subsidiado|contributivo|especial)\b.*", "", entidad
        ).strip() or None

    fecha_dx = first_match("fecha_diagnostico", PATTERNS["fecha_diagnostico"])

    # ── Diagnóstico ────────────────────────────────────────────────────────────
    cie10 = first_match("diagnostico_cie10", PATTERNS["diagnostico_cie10"])
    if cie10:
        cie10 = cie10.upper()

    desc = first_match("diagnostico_descripcion", PATTERNS["diagnostico_descripcion"])
    if desc:
        desc = desc[:200].strip()

    diagnostico_clinico = f"{cie10} - {desc}" if cie10 and desc else (desc or cie10)

    dx_patologico = first_match("diagnostico_patologico", PATTERNS["diagnostico_patologico"])
    if dx_patologico:
        dx_patologico = dx_patologico[:200].strip()

    tipo_cancer = first_match("tipo_cancer", PATTERNS["tipo_cancer"])
    if not tipo_cancer:
        tipo_cancer = infer_cancer_type_from_cie10(cie10) or infer_cancer_type_from_text(text)
        if tipo_cancer:
            confidence["tipo_cancer"] = 0.6
            warnings.append("Tipo de cáncer inferido automáticamente")

    # ── TNM desglosado ─────────────────────────────────────────────────────────
    estadif_raw = first_match("estadificacion", PATTERNS["estadificacion"])
    estadif = _normalize_staging(estadif_raw) if estadif_raw else None

    tnm_t = first_match("tnm_t", PATTERNS["tnm_t"])
    tnm_n = first_match("tnm_n", PATTERNS["tnm_n"])
    tnm_m = first_match("tnm_m", PATTERNS["tnm_m"])

    # Si el estadio tiene formato TNM completo, desglósalo
    if estadif_raw and re.match(r"(?i)T\d", estadif_raw):
        m = re.match(r"(?i)T(\d[abc]?)\s*N(\d[abc]?)\s*M(\d[abc]?)", estadif_raw)
        if m:
            tnm_t = tnm_t or m.group(1)
            tnm_n = tnm_n or m.group(2)
            tnm_m = tnm_m or m.group(3)
            estadif = estadif_raw  # keep full TNM as staging too

    # ── Imágenes diagnósticas — X si se menciona, vacío si no ────────────────
    tl = text.lower()

    def imagen_x(keywords: list[str], field: str) -> str | None:
        """Devuelve 'X' si alguna keyword aparece en el texto, None si no."""
        found = any(kw in tl for kw in keywords)
        confidence[field] = 0.7 if found else 0.0
        return "X" if found else None

    ecografia = imagen_x(["ecograf", "ultrasonido", "ecoscopia"], "ecografia")
    tac       = imagen_x(["tac", "tomograf"], "tac")
    rmn       = imagen_x(["rmn", "resonancia magn"], "rmn")
    pet       = imagen_x(["pet tc", "pet/ct", "pet ct", "pet-ct", "petct"], "pet")
    mamografia = imagen_x(["mamograf"], "mamografia")
    informes  = first_match("informes_imagenes", PATTERNS["informes_imagenes"])

    # ── Tratamientos ───────────────────────────────────────────────────────────
    # Cirugía
    cirugia_recibio = None
    cirugia_fecha = None
    cirugia_tipo = None
    cir_keywords = TREATMENT_KEYWORDS["Cirugía"]
    if treatment_present(cir_keywords):
        cirugia_recibio = "Sí"
        confidence["cirugia_recibio"] = 0.7
        cirugia_fecha = first_match("cirugia_fecha", PATTERNS["cirugia_fecha"])
        cirugia_tipo = first_match("cirugia_tipo", PATTERNS["cirugia_tipo"])
    else:
        cirugia_recibio = "No"
        confidence["cirugia_recibio"] = 0.5

    # Quimioterapia
    quimio_recibio = None
    quimio_esquema = None
    quimio_keywords = TREATMENT_KEYWORDS["Quimioterapia"]
    if treatment_present(quimio_keywords):
        quimio_recibio = "Sí"
        confidence["quimioterapia_recibio"] = 0.7
        quimio_esquema = first_match("quimioterapia_esquema", PATTERNS["quimioterapia_esquema"])
    else:
        quimio_recibio = "No"
        confidence["quimioterapia_recibio"] = 0.5

    # Radioterapia
    radio_recibio = None
    radio_dosis = None
    radio_keywords = TREATMENT_KEYWORDS["Radioterapia"]
    if treatment_present(radio_keywords):
        radio_recibio = "Sí"
        confidence["radioterapia_recibio"] = 0.7
        radio_dosis = first_match("radioterapia_dosis", PATTERNS["radioterapia_dosis"])
    else:
        radio_recibio = "No"
        confidence["radioterapia_recibio"] = 0.5

    # Hormonoterapia
    hormono_recibio = None
    hormono_tipo = None
    hormono_keywords = TREATMENT_KEYWORDS["Hormonoterapia"]
    if treatment_present(hormono_keywords):
        hormono_recibio = "Sí"
        confidence["hormonoterapia_recibio"] = 0.7
        hormono_tipo = first_match("hormonoterapia_tipo", PATTERNS["hormonoterapia_tipo"])
    else:
        hormono_recibio = "No"
        confidence["hormonoterapia_recibio"] = 0.5

    # ── Otros ──────────────────────────────────────────────────────────────────
    tratamiento_raw = first_match("tratamiento_inicial", PATTERNS["tratamiento_inicial"])
    tratamiento = tratamiento_raw[:300].strip() if tratamiento_raw else identify_treatment_from_text(text)

    resultado_raw = first_match("resultado_tratamiento", PATTERNS["resultado_tratamiento"])
    resultado = resultado_raw[:200].strip() if resultado_raw else identify_result_from_text(text)

    # ── Advertencias ───────────────────────────────────────────────────────────
    empty = [k for k, v in {
        "nombre": nombre_completo,
        "documento": documento,
        "diagnostico_cie10": cie10,
        "estadificacion": estadif,
        "medico_tratante": medico,
    }.items() if not v]
    if empty:
        warnings.append(f"Campos no encontrados: {', '.join(empty)}")

    data = PatientData(
        nombre_paciente=nombre_completo,
        nombre=nombre,
        apellidos=apellidos,
        documento=documento,
        tipo_documento=tipo_doc,
        edad=edad,
        sexo=sexo,
        fecha_atencion=fecha_atencion,
        medico_tratante=medico,
        especialidad=especialidad,
        entidad=entidad,
        fecha_diagnostico=fecha_dx,
        resumen_historia=NOTA_RESUMEN,
        diagnostico_cie10=cie10,
        diagnostico_descripcion=desc,
        diagnostico_clinico=diagnostico_clinico,
        diagnostico_patologico=dx_patologico,
        tipo_cancer=tipo_cancer,
        tnm_t=tnm_t,
        tnm_n=tnm_n,
        tnm_m=tnm_m,
        estadificacion=estadif,
        ecografia=ecografia,
        tac=tac,
        rmn=rmn,
        pet=pet,
        mamografia=mamografia,
        informes_imagenes=informes,
        cirugia_recibio=cirugia_recibio,
        cirugia_fecha=cirugia_fecha,
        cirugia_tipo=cirugia_tipo,
        quimioterapia_recibio=quimio_recibio,
        quimioterapia_esquema=quimio_esquema,
        radioterapia_recibio=radio_recibio,
        radioterapia_dosis=radio_dosis,
        hormonoterapia_recibio=hormono_recibio,
        hormonoterapia_tipo=hormono_tipo,
        tratamiento_inicial=tratamiento,
        resultado_tratamiento=resultado,
    )
    return data, confidence, warnings


# ── Helpers ────────────────────────────────────────────────────────────────────

def _clean_name(name: str) -> str:
    name = re.sub(r"\b(?:CC|NIT|TEL|FIRMA|REG|ESPECIALIDAD)\b.*", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[^\w\sáéíóúñÁÉÍÓÚÑ,\.]", "", name)
    name = re.sub(r"\s+", " ", name).strip().strip(",").strip()
    return name.title() if name else name


def _split_name(full_name: str) -> tuple[str, str]:
    """
    Convención colombiana: primeros 2 palabras = nombres, resto = apellidos.
    - 4 palabras: nombre1 nombre2 | apellido1 apellido2  ✓
    - 3 palabras: nombre1 | apellido1 apellido2           ✓
    - 2 palabras: nombre1 | apellido1                    ✓
    """
    words = full_name.split()
    n = len(words)
    if n >= 4:
        # Siempre las 2 primeras = nombres, el resto = apellidos
        return " ".join(words[:2]), " ".join(words[2:])
    if n == 3:
        return words[0], " ".join(words[1:])
    if n == 2:
        return words[0], words[1]
    return full_name, ""


def _normalize_doc_type(raw: str) -> str:
    r = raw.strip().lower()
    if re.search(r"c\.?\s*c\.?|ciudadan", r):
        return "Cédula de Ciudadanía"
    if re.search(r"t\.?\s*i\.?|tarjeta\s+identidad", r):
        return "Tarjeta de Identidad"
    if re.search(r"c\.?\s*e\.?|extranjería", r):
        return "Cédula de Extranjería"
    if "pasaporte" in r:
        return "Pasaporte"
    return raw.strip().title()


def _normalize_staging(raw: str) -> str:
    raw = raw.strip()
    if re.match(r"(?i)T\d", raw):
        return raw.upper()
    roman_map = {"1": "I", "2": "II", "3": "III", "4": "IV"}
    normalized = raw.upper().replace(" ", "")
    for digit, roman in roman_map.items():
        if normalized.startswith(digit):
            normalized = roman + normalized[1:]
    return normalized


def _extract_institution_from_header(text: str) -> Optional[str]:
    """Try to extract the institution from the first non-empty lines."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    inst_keywords = ("hospital", "clínica", "clinica", "centro", "fundación", "fundacion",
                     "instituto", "ltda", "s.a.s", "e.s.e", "ips", "eps", "cancerológico",
                     "cancerologico", "oncológico", "oncologico")
    # Términos de régimen de salud que no forman parte del nombre de la institución
    _regime_re = re.compile(
        r"(?i)\s*[-–]?\s*(?:r[eé]gimen\s+)?(?:subsidiado|contributivo|especial|excepci[oó]n)"
        r"|\s*[-–]?\s*(?:afiliado|tipo\s+de\s+usuario|usuario)\b.*",
        re.IGNORECASE,
    )
    for line in lines[:10]:
        if any(kw in line.lower() for kw in inst_keywords) and len(line) > 5:
            clean = _regime_re.sub("", line).strip()
            if clean:
                return clean[:120].title()
    return None
